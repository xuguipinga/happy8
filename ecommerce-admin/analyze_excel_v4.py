import openpyxl
import pandas as pd
import zipfile
import os

file_path = r'd:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\excel-model\克罗心最新表格.xlsx'

print("--- Sheet Info ---")
wb = openpyxl.load_workbook(file_path, data_only=True)
for name in wb.sheetnames:
    ws = wb[name]
    print(f"Sheet: {name}, Images: {len(ws._images)}")
    for i, img in enumerate(ws._images):
        print(f"  Image {i} anchor: {img.anchor}")
        if hasattr(img.anchor, '_from'):
             print(f"    From row={img.anchor._from.row}, col={img.anchor._from.col}")

print("\n--- ZIP Internal Check (Images) ---")
try:
    with zipfile.ZipFile(file_path, 'r') as z:
        image_files = [f for f in z.namelist() if f.startswith('xl/media/')]
        print(f"Total image files in ZIP: {len(image_files)}")
        for f in image_files[:5]:
            print(f"  {f}")
except Exception as e:
    print(f"Error reading ZIP: {e}")

print("\n--- Data Sample (Pandas) ---")
df = pd.read_excel(file_path, header=None)
print(df.iloc[:10, :10])
