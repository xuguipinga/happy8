"""
删除不需要的文件
"""
import os

files_to_delete = [
    r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\backend\app\utils\smart_matcher.py",
    r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\backend\app\models\sku_mapping.py",
    r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\backend\app\api\sku_mappings.py",
    r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\backend\create_sku_mapping_table.py",
    r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\backend\add_smart_matching_fields.py",
    r"d:\WorkSpec\Project\Ecommerce-admin\ecommerce-admin\frontend\src\api\skuMapping.js",
]

print("=" * 60)
print("删除不需要的文件...")
print("=" * 60)

deleted_count = 0
for file_path in files_to_delete:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"✓ 已删除: {os.path.basename(file_path)}")
            deleted_count += 1
        except Exception as e:
            print(f"✗ 删除失败 {os.path.basename(file_path)}: {str(e)}")
    else:
        print(f"  跳过(不存在): {os.path.basename(file_path)}")

print("\n" + "=" * 60)
print(f"✓ 完成! 共删除 {deleted_count} 个文件")
print("=" * 60)
