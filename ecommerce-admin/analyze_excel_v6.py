import pandas as pd
file_path = r'd:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\excel-model\克罗心最新表格.xlsx'
df = pd.read_excel(file_path, header=None)
print("Full Data Snapshot (15x9):")
print(df.iloc[:15, :9])
