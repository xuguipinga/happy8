
import pandas as pd
import sys
import os

# 模拟后端路径环境
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.utils.inventory_parser import parse_inventory_excel

def debug_excel_file(file_path):
    print(f"--- Debugging File: {file_path} ---")
    if not os.path.exists(file_path):
        print("Error: File not found!")
        return

    try:
        # 1. 打印原始结构快照
        df_raw = pd.read_excel(file_path, header=None)
        print("\n[Raw Data Snapshot - First 10 rows]:")
        print(df_raw.head(10).to_string())
        print(f"\nTotal Columns: {len(df_raw.columns)}")

        # 2. 尝试解析
        with open(file_path, 'rb') as f:
            content = f.read()
        
        results = parse_inventory_excel(content)
        
        print(f"\n[Parsing Result]:")
        print(f"Total items extracted: {len(results)}")
        if results:
            print("First 5 items sample:")
            for item in results[:5]:
                print(item)
        else:
            print("Warning: No items extracted. Checking why...")
            # 再次检查表头定位逻辑
            header_idx = -1
            for idx, row in df_raw.iterrows():
                row_vals = [str(cell).strip() for cell in row]
                print(f"Row {idx} contains '型号'?: {'型号' in row_vals} | Cells: {row_vals}")
                if '型号' in row_vals:
                    header_idx = idx
                    break
            print(f"Found '型号' at index: {header_idx}")

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    target_file = r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\docs\克罗心手镯库存清单.xlsx"
    debug_excel_file(target_file)
