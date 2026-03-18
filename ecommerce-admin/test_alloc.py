import pandas as pd
import numpy as np

df = pd.read_excel(r'd:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\excel-model\21903909_1772967545000.xlsx', dtype=str)

ffill_cols = ['订单编号', '运费(元)', '涨价或折扣(元)', '实付款(元)']
exist_cols = [c for c in ffill_cols if c in df.columns]
if exist_cols:
    df[exist_cols] = df[exist_cols].ffill()

# Convert needed columns to numeric
alloc_cols = ['运费(元)', '涨价或折扣(元)', '实付款(元)']
for col in alloc_cols + ['货品总价(元)']:
    if col in df.columns:
        df[col + '_num'] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Calculate sums per order
if '订单编号' in df.columns and '货品总价(元)_num' in df.columns:
    group_sums = df.groupby('订单编号')['货品总价(元)_num'].transform('sum')
    
    # Calculate ratio, defaulting to evenly split if total is 0
    group_counts = df.groupby('订单编号')['订单编号'].transform('count')
    df['ratio'] = np.where(group_sums > 0, df['货品总价(元)_num'] / group_sums, 1.0 / group_counts)
    
    # Apply ratio to alloc cols
    for col in alloc_cols:
        if col + '_num' in df.columns:
            df[col] = (df[col + '_num'] * df['ratio']).round(2).astype(str)

print(df[['订单编号', '货品总价(元)_num', 'ratio'] + alloc_cols].head(15))
