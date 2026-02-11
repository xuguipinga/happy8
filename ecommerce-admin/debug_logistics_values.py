import pandas as pd
import sys

# Set encoding to utf-8 for output
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'd:\\happy8\\ecommerce-admin\\excel-model\\物流.xlsx'

try:
    df = pd.read_excel(file_path, nrows=5)
    cols = ['物流运费', '优惠金额', '实付金额', '申报价值（美元）']
    print(df[cols])
    print("\nData Types:")
    print(df[cols].dtypes)
except Exception as e:
    print(f"Error: {e}")
