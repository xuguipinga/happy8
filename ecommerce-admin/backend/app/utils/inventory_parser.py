import pandas as pd
from decimal import Decimal
import io
import os
import openpyxl
import zipfile
import xml.etree.ElementTree as ET
from app.utils.image_helper import save_image_from_bytes

def extract_images_from_xlsx(file_content):
    """
    由于 openpyxl 偶尔无法直接读取图片，使用 zip 直接解析 XML 获取图片锚点
    返回: {(row, col): image_bytes}
    注: row/col 是从 0 开始的
    """
    image_map = {}
    try:
        with zipfile.ZipFile(io.BytesIO(file_content), 'r') as z:
            # 1. 找到 sheet1 的 rels 来定位 drawing
            sheet_rels_path = 'xl/worksheets/_rels/sheet1.xml.rels'
            if sheet_rels_path not in z.namelist():
                return {}
            
            rels_root = ET.fromstring(z.read(sheet_rels_path))
            drawing_path = None
            for rel in rels_root:
                if 'drawing' in rel.attrib.get('Type', ''):
                    target = rel.attrib.get('Target')
                    drawing_path = target.replace('../drawings/', 'xl/drawings/')
                    break
            
            if not drawing_path:
                return {}
            
            # 2. 读取 drawing 的 rels 来获取图片 ID 和路径的映射
            drawing_rels_path = f'xl/drawings/_rels/{os.path.basename(drawing_path)}.rels'
            media_map = {}
            if drawing_rels_path in z.namelist():
                draw_rels_root = ET.fromstring(z.read(drawing_rels_path))
                for r in draw_rels_root:
                    rid = r.attrib.get('Id')
                    target = r.attrib.get('Target').replace('../media/', 'xl/media/')
                    media_map[rid] = target
            
            # 3. 解析 drawing.xml 获取锚点
            draw_root = ET.fromstring(z.read(drawing_path))
            ns = {
                'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }
            
            for anchor in draw_root.findall('.//xdr:twoCellAnchor', ns) + draw_root.findall('.//xdr:oneCellAnchor', ns):
                from_el = anchor.find('.//xdr:from', ns)
                if from_el is None: continue
                row = int(from_el.find('xdr:row', ns).text)
                col = int(from_el.find('xdr:col', ns).text)
                
                pic = anchor.find('.//xdr:pic', ns)
                if pic is None: continue
                blip = pic.find('.//a:blip', ns)
                if blip is None: continue
                
                rid = blip.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if rid in media_map:
                    image_map[(row, col)] = z.read(media_map[rid])
                    
    except Exception as e:
        print(f"Deep image extraction error: {e}")
        
    return image_map

def parse_inventory_excel(file_content):
    """
    解析库存 Excel，支持：
    1. 标准 3 列纵向列表 (型号, 规格, 数量)
    2. 克罗心风格的水平网格 (示例图下方的 编号, 定价, 数量)
    """
    # 提取图片
    image_map = extract_images_from_xlsx(file_content)
    
    # 使用 openpyxl 读取数据以处理合并单元格和多表格
    wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
    ws = wb.active
    
    results = []
    max_row = ws.max_row
    max_col = ws.max_column
    current_series = None
    
    # 遍历所有行，动态识别格式
    r = 1
    while r <= max_row:
        cell_val_1 = str(ws.cell(r, 1).value).strip() if ws.cell(r, 1).value else ''
        
        # 1. 检测系列行 (如 "克罗心库存清单C系列")
        if '系列' in cell_val_1 and ('清单' in cell_val_1 or '库存' in cell_val_1):
            current_series = cell_val_1
            r += 1
            continue

        # 2. 检测 "型号 + 数量" 配对模式 (水平网格)
        row_vals_5 = [str(ws.cell(r, c).value).strip() for c in range(1, min(max_col, 6) + 1)]
        if '型号' in row_vals_5 and '数量' in row_vals_5:
            # 进入配对模式处理
            r += 1 # 跳过表头
            while r <= max_row:
                # 如果遇到下一个系列或列表表头，退出当前模式
                v1 = str(ws.cell(r, 1).value).strip() if ws.cell(r, 1).value else ''
                if ('系列' in v1 and '清单' in v1) or v1 == '型号':
                    break
                
                any_data = False
                for c_idx in range(1, max_col, 2):
                    model = str(ws.cell(r, c_idx).value).strip() if ws.cell(r, c_idx).value else ''
                    if not model or model.lower() in ['none', 'nan']: continue
                    
                    any_data = True
                    qty_val = ws.cell(r, c_idx + 1).value
                    qty = Decimal('0')
                    try:
                        if qty_val is not None: qty = Decimal(str(qty_val))
                    except: pass
                    
                    results.append({
                        'model': model,
                        'spec': '', # 配对模式通常没有单独规格列
                        'quantity': qty,
                        'avg_cost': Decimal('0'),
                        'image_url': None,
                        'series': current_series
                    })
                if not any_data: break
                r += 1
            continue

        # 2.5 检测 "规格/尺寸矩阵" 模式 (如 A:型号, B:17cm, C:18cm, D:19cm ...)
        # 特征：第一列是 '型号'，后面几列是数字或带 cm 的数字
        if cell_val_1 == '型号':
            specs = []
            for c in range(2, max_col + 1):
                s = str(ws.cell(r, c).value or '').strip()
                if not s or s.lower() in ['none', 'nan']: break
                specs.append(s)
            
            if specs and any(any(char.isdigit() for char in s) for s in specs):
                # 认为是矩阵模式
                r += 1 # 跳过表头
                while r <= max_row:
                    v1 = str(ws.cell(r, 1).value).strip() if ws.cell(r, 1).value else ''
                    if ('系列' in v1 and '清单' in v1) or v1 == '型号':
                        break
                    
                    model = v1
                    if not model: break
                    
                    any_data = False
                    for i, spec in enumerate(specs):
                        qty_val = ws.cell(r, i + 2).value
                        if qty_val is None or str(qty_val).strip() == '': continue
                        
                        qty = Decimal('0')
                        try:
                            qty = Decimal(str(qty_val))
                        except:
                            continue
                        
                        any_data = True
                        results.append({
                            'model': model,
                            'spec': spec,
                            'quantity': qty,
                            'avg_cost': Decimal('0'),
                            'image_url': None,
                            'series': current_series
                        })
                    if not any_data: # 如果整行没数据，可能在该系列结束
                        # 检查后续是否有数据，如果没有则 break
                        pass
                    r += 1
                continue

        # 3. 检测 "编号/型号" (后面无数量) -> 传统 3 行网格模式
        if cell_val_1 in ['编号', '型号']:
            # 这种模式下，R:型号, R+1:规格, R+2:价格
            for c in range(2, max_col + 1):
                model = str(ws.cell(r, c).value).strip() if ws.cell(r, c).value else ''
                if not model or model.lower() in ['none', 'nan']: continue
                
                spec = str(ws.cell(r + 1, c).value).strip() if ws.cell(r + 1, c).value else ''
                if spec.lower() in ['none', 'nan']: spec = ''
                
                price_val = ws.cell(r + 2, c).value
                avg_cost = Decimal('0')
                try:
                    if price_val is not None: avg_cost = Decimal(str(price_val))
                except: pass
                
                img_url = None
                if (r - 2, c - 1) in image_map:
                    img_url = save_image_from_bytes(image_map[(r - 2, c - 1)], f"{model}.jpg")
                elif (r - 1, c - 1) in image_map:
                    img_url = save_image_from_bytes(image_map[(r - 1, c - 1)], f"{model}.jpg")

                results.append({
                    'model': model,
                    'spec': spec,
                    'quantity': Decimal('0'),
                    'avg_cost': avg_cost,
                    'image_url': img_url,
                    'series': current_series
                })
            r += 3
            continue

        # 4. 检测纵向列表模式 (型号, 规格, 数量)
        if '型号' in row_vals_5:
            # 如果不是配对模式也不是网格模式，可能是纵向列表下的多列表
            header_row = r
            r += 1
            while r <= max_row:
                v1 = str(ws.cell(r, 1).value).strip() if ws.cell(r, 1).value else ''
                if '系列' in v1 and '清单' in v1: break
                
                any_data = False
                for c_start in range(1, max_col, 3):
                    model = str(ws.cell(r, c_start).value or '').strip()
                    if not model or model.lower() in ['none', 'nan', '型号']: continue
                    
                    any_data = True
                    spec = str(ws.cell(r, c_start + 1).value or '').strip()
                    qty_val = ws.cell(r, c_start + 2).value
                    qty = Decimal(str(qty_val)) if qty_val is not None else Decimal('0')
                    
                    img_url = None
                    if (r - 1, c_start - 2) in image_map:
                        img_url = save_image_from_bytes(image_map[(r - 1, c_start - 2)], f"{model}.jpg")
                        
                    results.append({
                        'model': model,
                        'spec': spec,
                        'quantity': qty,
                        'avg_cost': Decimal('0'),
                        'image_url': img_url,
                        'series': current_series
                    })
                if not any_data: break
                r += 1
            continue

        r += 1

    return results

    return results
