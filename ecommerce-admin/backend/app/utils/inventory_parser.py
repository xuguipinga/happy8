import pandas as pd
from decimal import Decimal
import io

def parse_inventory_excel(file_content):
    """
    解析四列分布的库存 Excel
    格式: [型号, 长度, 数量, 型号, 长度, 数量, ...]
    """
    df = pd.read_excel(io.BytesIO(file_content))
    results = []
    
    # 获取总列数
    cols = len(df.columns)
    
    # 每 3 列为一个循环 (型号, 长度, 数量)
    for i in range(0, cols, 3):
        if i + 2 >= cols:
            break
            
        # 提取当前三列的项目
        sub_df = df.iloc[:, i:i+3].copy()
        sub_df.columns = ['model', 'spec', 'quantity']
        
        # 清洗数据
        # 1. 填充合并单元格产生的型号 (Forward Fill)
        sub_df['model'] = sub_df['model'].ffill()
        
        # 2. 去掉空行 (数量为空的行通常无效)
        sub_df = sub_df.dropna(subset=['quantity'])
        
        for _, row in sub_df.iterrows():
            model = str(row['model']).strip()
            if not model or model == 'nan':
                continue
                
            spec = str(row['spec']).strip() if pd.notna(row['spec']) else ''
            try:
                qty = Decimal(str(row['quantity']))
            except:
                qty = Decimal('0')
                
            results.append({
                'model': model,
                'spec': spec,
                'quantity': qty
            })
            
    return results
