import pandas as pd
import os
import sys

# Set encoding for stdout just in case, though writing to file is safer
sys.stdout.reconfigure(encoding='utf-8')

base_dir = r'd:\\happy8\\ecommerce-admin\\excel-model'
files = ['物流.xlsx', '采购.xlsx', '销售订单明细.xlsx']
output_file = 'headers.txt'

with open(output_file, 'w', encoding='utf-8') as f_out:
    for f in files:
        path = os.path.join(base_dir, f)
        try:
            # Read only header row
            df = pd.read_excel(path, nrows=0)
            headers = df.columns.tolist()
            f_out.write(f"=== {f} ===\n")
            f_out.write(str(headers) + "\n\n")
            print(f"Processed {f}")
        except Exception as e:
            f_out.write(f"=== {f} ERROR ===\n")
            f_out.write(str(e) + "\n\n")
            print(f"Error processing {f}: {e}")

print(f"Headers written to {output_file}")
