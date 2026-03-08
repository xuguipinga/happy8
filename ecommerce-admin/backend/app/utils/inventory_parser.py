import pandas as pd
from decimal import Decimal
import io

def parse_inventory_excel(file_content):
    """
    解析四列分布的库存 Excel
    格式: [型号, 长度, 数量, 型号, 长度, 数量, ...]
    支持带标题行 (如 '克罗心库存清单')
    """
    # 先读取所有数据，不设 header
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
        
        for _, row in sub_df.iterrows():
            model = str(row['model']).strip() if pd.notna(row['model']) else ''
            if not model or model.lower() in ['nan', 'none', '型号']:
                continue
                
            qty_val = str(row['quantity']).strip() if pd.notna(row['quantity']) else '0'
            if qty_val.lower() in ['nan', 'none', '数量', '']:
                continue
                
            spec = str(row['spec']).strip() if pd.notna(row['spec']) else ''
            # 如果 spec 是 '长度' 这样的表头文案，则跳过
            if spec == '长度': continue

            try:
                qty = Decimal(qty_val)
            except:
                qty = Decimal('0')
                
            results.append({
                'model': model,
                'spec': spec,
                'quantity': qty
            })
            
    return results
