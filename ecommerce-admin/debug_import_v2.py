
import pandas as pd
from decimal import Decimal
import io
import os

def parse_inventory_excel(file_content):
    """
    [Copy of the logic in inventory_parser.py]
    """
    df = pd.read_excel(io.BytesIO(file_content), header=None)
    
    header_idx = -1
    for idx, row in df.iterrows():
        if any(str(cell).strip() == '型号' for cell in row):
            header_idx = idx
            break
    
    if header_idx == -1:
        return []
        
    results = []
    data_df = df.iloc[header_idx+1:].copy()
    cols = len(df.columns)
    
    for i in range(0, cols, 3):
        if i + 2 >= cols:
            break
            
        sub_df = data_df.iloc[:, i:i+3].copy()
        sub_df.columns = ['model', 'spec', 'quantity']
        
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

def debug_excel_file(file_path):
    print(f"--- Debugging File Struct: {file_path} ---")
    if not os.path.exists(file_path):
        print("Error: File not found!")
        return

    try:
        df_raw = pd.read_excel(file_path, header=None)
        print("\n[Row 0-5 Snapshot]:")
        for i in range(min(10, len(df_raw))):
            print(f"Row {i}: {list(df_raw.iloc[i])}")
            
        with open(file_path, 'rb') as f:
            content = f.read()
        
        results = parse_inventory_excel(content)
        
        print(f"\n[Extraction results]: {len(results)} items found.")
        if results:
            for item in results[:10]:
                print(item)
        else:
            print("FAILED: No items found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target = r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\docs\克罗心手镯库存清单.xlsx"
    debug_excel_file(target)
