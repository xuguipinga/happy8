
import sys
import os

# 模拟路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from backend.app import create_app
from backend.app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # 检查 biz_inventory 表是否有 status 列
        result = db.session.execute(text("PRAGMA table_info(biz_inventory)")).fetchall()
        columns = [row[1] for row in result]
        
        if 'status' not in columns:
            print("Adding 'status' column to biz_inventory...")
            db.session.execute(text("ALTER TABLE biz_inventory ADD COLUMN status VARCHAR(20) DEFAULT 'NORMAL'"))
            db.session.commit()
            print("Column added successfully.")
        else:
            print("'status' column already exists.")
            
    except Exception as e:
        print(f"Error checking/updating database: {e}")
