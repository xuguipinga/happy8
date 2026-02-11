import pandas as pd
import os

base_dir = r'd:\\happy8\\ecommerce-admin\\excel-model'
files = ['物流.xlsx', '采购.xlsx']

for f in files:
    path = os.path.join(base_dir, f)
    try:
        df = pd.read_excel(path, nrows=0)
        print(f"=== {f} Headers ===")
        print(df.columns.tolist())
        print("\n")
    except Exception as e:
        print(f"Error reading {f}: {e}")
