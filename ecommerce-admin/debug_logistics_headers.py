import pandas as pd
import sys

# Set encoding to utf-8 for output
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'd:\\happy8\\ecommerce-admin\\excel-model\\物流.xlsx'

try:
    df = pd.read_excel(file_path, nrows=0)
    print("Columns in Logistics Excel:")
    for col in df.columns:
        print(repr(col))
except Exception as e:
    print(f"Error: {e}")
