import pandas as pd
import os

files = [
    'excel-model/purchase.xlsx',
    'excel-model/saleDetail.xlsx',
    'excel-model/物流.xlsx'
]

for f in files:
    path = os.path.join(os.getcwd(), f)
    if os.path.exists(path):
        print(f"\n=== {os.path.basename(f)} headers ===")
        try:
            df = pd.read_excel(path, nrows=0)
            print(list(df.columns))
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"File not found: {path}")
