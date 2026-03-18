import os
from app import create_app, db
from app.models.stock import Inventory

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def fix_series():
    with app.app_context():
        # 查找所有系列为空的库存项
        items = Inventory.query.filter((Inventory.series == None) | (Inventory.series == '')).all()
        print(f"Found {len(items)} items to fix series.")
        
        count = 0
        for item in items:
            if item.model and len(item.model) > 0:
                prefix = item.model[0].upper()
                # 针对克罗心常见的 C, D, I 系列做映射
                if prefix in ['C', 'D', 'I']:
                    item.series = f"克罗心库存清单{prefix}系列"
                else:
                    item.series = f"{prefix}系列"
                count += 1
        
        db.session.commit()
        print(f"Successfully fixed {count} items.")

if __name__ == '__main__':
    fix_series()
