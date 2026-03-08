
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
            
        # 检查 biz_stock_records 表是否有 operator_name 列
        result = db.session.execute(text("SHOW COLUMNS FROM biz_stock_records")).fetchall()
        columns = [row[0] for row in result]
        if 'operator_name' not in columns:
            print("Adding 'operator_name' column to biz_stock_records...")
            db.session.execute(text("ALTER TABLE biz_stock_records ADD COLUMN operator_name VARCHAR(50) COMMENT '操作人姓名'"))
            db.session.commit()
            print("Column 'operator_name' added successfully.")
        else:
            print("Column 'operator_name' already exists.")
            
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
            
            # SQLite check for biz_stock_records
            result = db.session.execute(text("PRAGMA table_info(biz_stock_records)")).fetchall()
            columns = [row[1] for row in result]
            if 'operator_name' not in columns:
                db.session.execute(text("ALTER TABLE biz_stock_records ADD COLUMN operator_name VARCHAR(50)"))
                db.session.commit()
                print("Column 'operator_name' added successfully (SQLite).")
        except Exception as e_inner:
            print(f"Error updating database: {e_inner}")
