import os
from sqlalchemy import text
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def update_db():
    with app.app_context():
        print("Updating database schema...")
        try:
            # 添加 series 字段
            db.session.execute(text("ALTER TABLE biz_inventory ADD COLUMN series VARCHAR(50) DEFAULT NULL"))
            db.session.commit()
            print("Successfully added 'series' column.")
        except Exception as e:
            if 'Duplicate column name' in str(e):
                print("Column 'series' already exists.")
            else:
                print(f"Error adding column: {e}")

        try:
            # 添加索引
            db.session.execute(text("CREATE INDEX idx_series ON biz_inventory(series)"))
            db.session.commit()
            print("Successfully created index idx_series.")
        except Exception as e:
            if 'Duplicate key name' in str(e) or 'already exists' in str(e).lower():
                print("Index 'idx_series' already exists.")
            else:
                print(f"Error adding index: {e}")

if __name__ == '__main__':
    update_db()
