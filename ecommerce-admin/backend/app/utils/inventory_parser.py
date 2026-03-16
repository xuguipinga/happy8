import pandas as pd
from decimal import Decimal
import io
import openpyxl
from app.utils.image_helper import save_image_from_bytes

def parse_inventory_excel(file_content):
    """
    解析带图片的库存 Excel
    支持带标题行和四列/多列分布
    """
    # 使用 openpyxl 提取所有图片及其位置
    wb = openpyxl.load_workbook(io.BytesIO(file_content))
    image_map = {} # (row, col) -> image_bytes
    for sheetname in wb.sheetnames:
        ws = wb[sheetname]
        for image in ws._images:
            # openpyxl 的 row/col 是从 0 开始的
            row = image.anchor._from.row
            col = image.anchor._from.col
            image_map[(row, col)] = image._data()

    # 读取数据
    df = pd.read_excel(io.BytesIO(file_content), header=None)
    
    # 查找真正的表头行 (包含 '型号')
    header_idx = -1
    for idx, row in df.iterrows():
        if any(str(cell).strip() == '型号' for cell in row):
            header_idx = idx
            break
    
    if header_idx == -1:
        # 如果没找到表头，尝试直接作为无标题数据处理，或者报错
        return []
        
    results = []
    # 真正的表头以上的数据丢弃
    data_df = df.iloc[header_idx+1:].copy()
    
    # 获取总列数
    cols = len(df.columns)
    
    # 每 3 列为一个循环 (型号, 长度, 数量)
    for i in range(0, cols, 3):
        if i + 2 >= cols:
            break
            
        # 提取当前三列
        sub_df = data_df.iloc[:, i:i+3].copy()
        sub_df.columns = ['model', 'spec', 'quantity']
        
        # 处理合并单元格 (型号通常是合并的)
        # 注意: ffill 之前要先把无效的字符串转为 NaN
        sub_df['model'] = sub_df['model'].replace(['nan', 'None', '', 'NULL'], pd.NA)
        sub_df['model'] = sub_df['model'].ffill()
        
        for index, row in sub_df.iterrows():
            model = str(row['model']).strip() if pd.notna(row['model']) else ''
            if not model or model.lower() in ['nan', 'none', '型号']:
                continue
                
            qty_val = str(row['quantity']).strip() if pd.notna(row['quantity']) else '0'
            if qty_val.lower() in ['nan', 'none', '数量', '']:
                continue
                
            spec = str(row['spec']).strip() if pd.notna(row['spec']) else ''
            if spec == '长度': continue

            try:
                qty = Decimal(qty_val)
            except:
                qty = Decimal('0')
                
            # 查找关联图片
            img_url = None
            # pandas row index matches sheet row index because we didn't reset_index after splitting
            sheet_row = index 
            
            # 检查逻辑：在“型号”列的前一列（示例图）查找图片，或者在型号本身所在列查找
            for offset in [-1, 0]:
                check_col = i + offset
                if (sheet_row, check_col) in image_map:
                    image_bytes = image_map[(sheet_row, check_col)]
                    img_url = save_image_from_bytes(image_bytes() if callable(image_bytes) else image_bytes, f"{model}.jpg")
                    break

            results.append({
                'model': model,
                'spec': spec,
                'quantity': qty,
                'image_url': img_url
            })
            
    return results
