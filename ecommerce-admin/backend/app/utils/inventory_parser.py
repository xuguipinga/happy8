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
        for r in range(1, max_row + 1):
            cell_val = str(ws.cell(r, 1).value).strip() if ws.cell(r, 1).value else ''
            if cell_val in ['编号', '型号']:
                # 这一行是型号行，下面可能是规格和数量
                for c in range(2, max_col + 1):
                    model = str(ws.cell(r, c).value).strip() if ws.cell(r, c).value else ''
                    if not model or model.lower() in ['none', 'nan']: continue
                    
                    # 查找规格（下一行）
                    spec = str(ws.cell(r + 1, c).value).strip() if ws.cell(r + 1, c).value else ''
                    if spec.lower() in ['none', 'nan']: spec = ''
                    
                    # 查找数量（下下行）
                    qty_val = ws.cell(r + 2, c).value
                    try:
                        qty = Decimal(str(qty_val)) if qty_val is not None else Decimal('0')
                    except:
                        qty = Decimal('0')
                        
                    # 查找图片 (通常在型号行上方一行)
                    img_url = None
                    if (r - 2, c - 1) in image_map: # XML index is 0-based
                        img_url = save_image_from_bytes(image_map[(r - 2, c - 1)], f"{model}.jpg")
                    elif (r - 1, c - 1) in image_map:
                        img_url = save_image_from_bytes(image_map[(r - 1, c - 1)], f"{model}.jpg")

                    results.append({
                        'model': model,
                        'spec': spec,
                        'quantity': qty,
                        'image_url': img_url
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
                        'image_url': img_url
                    })

    return results
