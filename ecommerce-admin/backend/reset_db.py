"""
重置 MySQL 数据库脚本
Drop all tables and recreate from models
"""
from app import create_app, db
import os

# 设置使用 MySQL
os.environ['DATABASE_URL'] = 'mysql://root:root@localhost:3306/ecommerce_admin'

app = create_app()

with app.app_context():
    # 删除所有表
    print("正在删除所有表...")
    db.drop_all()
    print("[OK] 所有表已删除")
    
    # 直接从模型创建表
    print("正在创建表...")
    db.create_all()
    print("[OK] 所有表已创建")
    
    print("\n数据库已重置！")
