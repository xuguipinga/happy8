"""
应用数据库迁移脚本
执行多租户迁移
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import app
from app.extensions import db
from sqlalchemy import text

def apply_migration():
    """应用多租户迁移"""
    with app.app_context():
        print("=" * 60)
        print("开始应用多租户数据库迁移...")
        print("=" * 60)
        
        try:
            # 1. 创建租户表
            print("\n1. 创建租户表...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS sys_tenants (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(150) NOT NULL COMMENT '公司/店铺名称',
                    code VARCHAR(50) NOT NULL UNIQUE COMMENT '租户代码',
                    contact_person VARCHAR(100) COMMENT '联系人',
                    contact_phone VARCHAR(20) COMMENT '联系电话',
                    contact_email VARCHAR(100) COMMENT '联系邮箱',
                    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    INDEX idx_code (code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户表'
            """))
            print("✓ 租户表创建成功")
            
            # 2. 插入默认租户
            print("\n2. 创建默认租户...")
            db.session.execute(text("""
                INSERT IGNORE INTO sys_tenants (id, name, code, is_active, created_at) 
                VALUES (1, '默认租户', 'DEFAULT', 1, NOW())
            """))
            print("✓ 默认租户创建成功")
            
            # 3. 为用户表添加字段
            print("\n3. 更新用户表...")
            try:
                db.session.execute(text("""
                    ALTER TABLE sys_users 
                    ADD COLUMN tenant_id INT COMMENT '租户ID' AFTER id,
                    ADD COLUMN role VARCHAR(20) DEFAULT 'user' COMMENT '角色: admin/user' AFTER password_hash
                """))
            except Exception as e:
                if "Duplicate column name" not in str(e):
                    raise
                print("  (字段已存在,跳过)")
            
            db.session.execute(text("UPDATE sys_users SET tenant_id = 1, role = 'admin' WHERE tenant_id IS NULL"))
            
            try:
                db.session.execute(text("ALTER TABLE sys_users MODIFY COLUMN tenant_id INT NOT NULL"))
                db.session.execute(text("ALTER TABLE sys_users ADD INDEX idx_tenant_id (tenant_id)"))
                db.session.execute(text("ALTER TABLE sys_users ADD FOREIGN KEY fk_users_tenant (tenant_id) REFERENCES sys_tenants(id)"))
            except Exception as e:
                if "Duplicate" not in str(e) and "already exists" not in str(e):
                    raise
            print("✓ 用户表更新成功")
            
            # 4. 为订单表添加字段
            print("\n4. 更新订单表...")
            try:
                db.session.execute(text("ALTER TABLE biz_orders ADD COLUMN tenant_id INT COMMENT '租户ID' AFTER id"))
            except Exception as e:
                if "Duplicate column name" not in str(e):
                    raise
                print("  (字段已存在,跳过)")
            
            db.session.execute(text("UPDATE biz_orders SET tenant_id = 1 WHERE tenant_id IS NULL"))
            
            try:
                db.session.execute(text("ALTER TABLE biz_orders MODIFY COLUMN tenant_id INT NOT NULL"))
                db.session.execute(text("ALTER TABLE biz_orders ADD INDEX idx_tenant_id (tenant_id)"))
                db.session.execute(text("ALTER TABLE biz_orders ADD FOREIGN KEY fk_orders_tenant (tenant_id) REFERENCES sys_tenants(id)"))
            except Exception as e:
                if "Duplicate" not in str(e) and "already exists" not in str(e):
                    raise
            print("✓ 订单表更新成功")
            
            # 5. 为产品表添加字段
            print("\n5. 更新产品表...")
            try:
                db.session.execute(text("ALTER TABLE biz_products ADD COLUMN tenant_id INT COMMENT '租户ID' AFTER id"))
            except Exception as e:
                if "Duplicate column name" not in str(e):
                    raise
                print("  (字段已存在,跳过)")
            
            db.session.execute(text("UPDATE biz_products SET tenant_id = 1 WHERE tenant_id IS NULL"))
            
            try:
                db.session.execute(text("ALTER TABLE biz_products MODIFY COLUMN tenant_id INT NOT NULL"))
                db.session.execute(text("ALTER TABLE biz_products ADD INDEX idx_tenant_id (tenant_id)"))
                db.session.execute(text("ALTER TABLE biz_products ADD FOREIGN KEY fk_products_tenant (tenant_id) REFERENCES sys_tenants(id)"))
            except Exception as e:
                if "Duplicate" not in str(e) and "already exists" not in str(e):
                    raise
            print("✓ 产品表更新成功")
            
            # 6. 为采购表添加字段
            print("\n6. 更新采购表...")
            try:
                db.session.execute(text("ALTER TABLE biz_purchases ADD COLUMN tenant_id INT COMMENT '租户ID' AFTER id"))
            except Exception as e:
                if "Duplicate column name" not in str(e):
                    raise
                print("  (字段已存在,跳过)")
            
            db.session.execute(text("UPDATE biz_purchases SET tenant_id = 1 WHERE tenant_id IS NULL"))
            
            try:
                db.session.execute(text("ALTER TABLE biz_purchases MODIFY COLUMN tenant_id INT NOT NULL"))
                db.session.execute(text("ALTER TABLE biz_purchases ADD INDEX idx_tenant_id (tenant_id)"))
                db.session.execute(text("ALTER TABLE biz_purchases ADD FOREIGN KEY fk_purchases_tenant (tenant_id) REFERENCES sys_tenants(id)"))
            except Exception as e:
                if "Duplicate" not in str(e) and "already exists" not in str(e):
                    raise
            print("✓ 采购表更新成功")
            
            # 7. 为物流表添加字段
            print("\n7. 更新物流表...")
            try:
                db.session.execute(text("ALTER TABLE biz_logistics ADD COLUMN tenant_id INT COMMENT '租户ID' AFTER id"))
            except Exception as e:
                if "Duplicate column name" not in str(e):
                    raise
                print("  (字段已存在,跳过)")
            
            db.session.execute(text("UPDATE biz_logistics SET tenant_id = 1 WHERE tenant_id IS NULL"))
            
            try:
                db.session.execute(text("ALTER TABLE biz_logistics MODIFY COLUMN tenant_id INT NOT NULL"))
                db.session.execute(text("ALTER TABLE biz_logistics ADD INDEX idx_tenant_id (tenant_id)"))
                db.session.execute(text("ALTER TABLE biz_logistics ADD FOREIGN KEY fk_logistics_tenant (tenant_id) REFERENCES sys_tenants(id)"))
            except Exception as e:
                if "Duplicate" not in str(e) and "already exists" not in str(e):
                    raise
            print("✓ 物流表更新成功")
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✓ 数据库迁移完成!")
            print("=" * 60)
            print("\n提示:")
            print("1. 所有表已添加 tenant_id 字段")
            print("2. 现有数据已分配到'默认租户' (ID: 1)")
            print("3. 现有用户已设置为管理员角色")
            print("4. 请重启后端服务以应用更改")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    apply_migration()
