import pandas as pd
import os

file_path = r'd:\happy8\ecommerce-admin\excel-model\销售订单明细.xlsx'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    
    # Check SKU length
    # Based on headers.txt, SKU column might be 'SKU规格(Sku Specification)' or '单品货号' or 'SKU ID'
    sku_col = 'SKU规格(Sku Specification)'
    
    if sku_col in df.columns:
        # Convert to string and measure length
        max_len = df[sku_col].astype(str).map(len).max()
        print(f"Max length of '{sku_col}': {max_len}")
        
        # Print some long examples
        long_skus = df[df[sku_col].astype(str).map(len) > 90][sku_col].head(5).tolist()
        print("Examples of long SKUs:", long_skus)
    else:
        print(f"Column '{sku_col}' not found.")
        
except Exception as e:
    print(f"Error reading Excel: {e}")
