
import sys
import os

# 确保在容器内部能正确找到 app 包
sys.path.append(os.getcwd())

try:
    from app import create_app
    from app.extensions import db
except ImportError:
    # 兼容不同目录结构
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from app import create_app
        from app.extensions import db
    except ImportError:
        print("Error: Could not import 'app'. Please make sure the script is running in the correct directory.")
        sys.exit(1)

from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # 检查 biz_inventory 表是否有 status 列
        # 使用 SQLAlchemy 执行原生 SQL
        print("Checking database structure...")
        result = db.session.execute(text("SHOW COLUMNS FROM biz_inventory")).fetchall()
        columns = [row[0] for row in result]
        
        if 'status' not in columns:
            print("Adding 'status' column to biz_inventory...")
            db.session.execute(text("ALTER TABLE biz_inventory ADD COLUMN status VARCHAR(20) DEFAULT 'NORMAL' AFTER avg_cost"))
            db.session.commit()
            print("Column 'status' added successfully.")
        else:
            print("Column 'status' already exists.")
            
    except Exception as e:
        # 如果是 SQLite (开发环境)
        try:
            result = db.session.execute(text("PRAGMA table_info(biz_inventory)")).fetchall()
            columns = [row[1] for row in result]
            if 'status' not in columns:
                db.session.execute(text("ALTER TABLE biz_inventory ADD COLUMN status VARCHAR(20) DEFAULT 'NORMAL'"))
                db.session.commit()
                print("Column 'status' added successfully (SQLite).")
            else:
                print("Column 'status' already exists (SQLite).")
        except Exception as e_inner:
            print(f"Error updating database: {e_inner}")
