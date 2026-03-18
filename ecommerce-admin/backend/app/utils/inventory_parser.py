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
    
    # 策略 1: 寻找横向网格特征 (包含 "编号" 或 "型号" 且右侧有数据)
    is_grid = False
    for r in range(1, min(max_row, 10)):
        row_vals = [str(ws.cell(r, c).value).strip() if ws.cell(r, c).value else '' for c in range(1, 4)]
        if '编号' in row_vals or '型号' in row_vals:
            # 如果是横向的，通常第二列也是型号
            c2_val = str(ws.cell(r, 2).value).strip() if ws.cell(r, 2).value else ''
            if c2_val and c2_val not in ['编号', '型号', 'None']:
                is_grid = True
                break
                
    if is_grid:
        # 处理横向网格
        skipped_until = 0
        for r in range(1, max_row + 1):
            if r < skipped_until: continue
            cell_val = str(ws.cell(r, 1).value).strip() if ws.cell(r, 1).value else ''
            
            # 检测系列行 (如 "克罗心库存清单C系列")
            if '系列' in cell_val and ('清单' in cell_val or '库存' in cell_val):
                current_series = cell_val
                continue

            # 检测是否为 "型号+数量" 配对模式 (如 A:型号, B:数量, C:型号, D:数量)
            row_header_vals = [str(ws.cell(r, c).value).strip() for c in range(1, min(max_col, 5) + 1)]
            if '型号' in row_header_vals and '数量' in row_header_vals:
                # 这种模式下，数据通常在这一行之后
                # 我们继续向下扫描，直到遇到下一个系列或空行
                for data_r in range(r + 1, max_row + 1):
                    # 如果遇到系列行
                    next_val_1 = str(ws.cell(data_r, 1).value).strip() if ws.cell(data_r, 1).value else ''
                    if '系列' in next_val_1 and ('清单' in next_val_1 or '库存' in next_val_1):
                        skipped_until = data_r
                        break
                    
                    row_any_val = False
                    for c_idx in range(1, max_col, 2):
                        model = str(ws.cell(data_r, c_idx).value).strip() if ws.cell(data_r, c_idx).value else ''
                        if not model or model.lower() in ['none', 'nan', '型号']: continue
                        
                        row_any_val = True
                        qty_val = ws.cell(data_r, c_idx + 1).value
                        qty = Decimal('0')
                        try:
                            if qty_val is not None and str(qty_val).strip():
                                qty = Decimal(str(qty_val))
                        except:
                            pass
                        
                        results.append({
                            'model': model,
                            'spec': '',
                            'quantity': qty,
                            'avg_cost': Decimal('0'),
                            'image_url': None, # 这种紧凑格式暂不支持图片
                            'series': current_series
                        })
                    if not row_any_val: # 空行表示该段结束
                        skipped_until = data_r + 1
                        break
                    
                    if data_r == max_row:
                        skipped_until = max_row + 1
                continue 

            if cell_val in ['编号', '型号']:
                skipped_until = r + 3 # 之前的 3 行模式通常占用 3 行，跳过以避免重复处理
                # 原始 3 行网格模式 (型号 -> 规格 -> 价格)
                for c in range(2, max_col + 1):
                    model = str(ws.cell(r, c).value).strip() if ws.cell(r, c).value else ''
                    if not model or model.lower() in ['none', 'nan']: continue
                    
                    # 查找规格（下一行）
                    spec = str(ws.cell(r + 1, c).value).strip() if ws.cell(r + 1, c).value else ''
                    if spec.lower() in ['none', 'nan']: spec = ''
                    
                    # 查找价格 (下下行)
                    price_val = ws.cell(r + 2, c).value
                    avg_cost = Decimal('0')
                    try:
                        if price_val is not None:
                            avg_cost = Decimal(str(price_val))
                    except:
                        pass
                        
                    qty = Decimal('0')
                        
                    # 查找图片
                    img_url = None
                    if (r - 2, c - 1) in image_map:
                        img_url = save_image_from_bytes(image_map[(r - 2, c - 1)], f"{model}.jpg")
                    elif (r - 1, c - 1) in image_map:
                        img_url = save_image_from_bytes(image_map[(r - 1, c - 1)], f"{model}.jpg")

                    results.append({
                        'model': model,
                        'spec': spec,
                        'quantity': qty,
                        'avg_cost': avg_cost,
                        'image_url': img_url,
                        'series': current_series
                    })
    else:
        # 策略 2: 传统的纵向 3 列
        # 寻找包含 "型号" 的表头
        header_row = -1
        for r in range(1, 20):
            found = False
            for c in range(1, max_col + 1):
                if '型号' in str(ws.cell(r, c).value or ''):
                    header_row = r
                    found = True
                    break
            if found: break
            
        if header_row != -1:
            for r in range(header_row + 1, max_row + 1):
                # 检测系列行 (纵向列表模式也支持检测系列)
                cell_val_1 = str(ws.cell(r, 1).value or '').strip()
                if '系列' in cell_val_1 and ('清单' in cell_val_1 or '库存' in cell_val_1):
                    current_series = cell_val_1
                    continue

                # 假设每 3 列一个循环
                for c_start in range(1, max_col, 3):
                    model = str(ws.cell(r, c_start).value or '').strip()
                    if not model or model.lower() in ['none', 'nan', '型号']: continue
                    
                    spec = str(ws.cell(r, c_start + 1).value or '').strip()
                    qty_val = ws.cell(r, c_start + 2).value
                    try:
                        qty = Decimal(str(qty_val)) if qty_val is not None else Decimal('0')
                    except:
                        qty = Decimal('0')
                        
                    img_url = None
                    # 在型号左侧寻找图片
                    if (r - 1, c_start - 2) in image_map:
                        img_url = save_image_from_bytes(image_map[(r - 1, c_start - 2)], f"{model}.jpg")
                        
                    results.append({
                        'model': model,
                        'spec': spec,
                        'quantity': qty,
                        'avg_cost': Decimal('0'), # 默认纵向列表暂不支持读取成本
                        'image_url': img_url,
                        'series': current_series
                    })

    return results
