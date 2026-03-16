
import sys
import os

# 修正导入路径
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # 兼容 MySQL: 检查 biz_inventory 表的列信息
        result = db.session.execute(text("SHOW COLUMNS FROM biz_inventory")).fetchall()
        columns = [row[0] for row in result] # MySQL SHOW COLUMNS 第一列是 Field (列名)
        
        if 'status' not in columns:
            print("Adding 'status' column to biz_inventory...")
            db.session.execute(text("ALTER TABLE biz_inventory ADD COLUMN status VARCHAR(20) DEFAULT 'NORMAL'"))
            db.session.commit()
            print("Column added successfully.")
            
        if 'image_url' not in columns:
            print("Adding 'image_url' column to biz_inventory...")
            db.session.execute(text("ALTER TABLE biz_inventory ADD COLUMN image_url VARCHAR(255)"))
            db.session.commit()
            print("Column added successfully.")
        else:
            print("'image_url' column already exists.")
            
    except Exception as e:
        print(f"Error checking/updating database: {e}")
