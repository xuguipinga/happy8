import sys
import os

# Add project route
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import app
from app.extensions import db
from sqlalchemy import text

def apply_stock_migration():
    """应用库存与财务模块迁移"""
    with app.app_context():
        print("=" * 60)
        print("开始应用库存与财务模块数据库迁移...")
        print("=" * 60)
        
        try:
            # 1. Create Inventory Main Table
            print("\n1. Create biz_inventory table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS biz_inventory (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    tenant_id INT NOT NULL COMMENT 'tenant_id',
                    model VARCHAR(100) NOT NULL COMMENT 'model (B002)',
                    spec VARCHAR(100) COMMENT 'spec (20cm)',
                    quantity DECIMAL(12, 4) DEFAULT 0.0 COMMENT 'quantity',
                    unit VARCHAR(20) DEFAULT 'pcs' COMMENT 'unit',
                    avg_cost DECIMAL(12, 4) DEFAULT 0.0 COMMENT 'avg_cost',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_tenant_model (tenant_id, model),
                    INDEX idx_model_spec (model, spec),
                    FOREIGN KEY (tenant_id) REFERENCES sys_tenants(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='inventory'
            """))
            print("Done: biz_inventory created")
            
            # 2. Create Stock Records Table
            print("\n2. Create biz_stock_records table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS biz_stock_records (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    tenant_id INT NOT NULL,
                    inventory_id BIGINT NOT NULL,
                    order_id BIGINT COMMENT 'order_id',
                    purchase_id BIGINT COMMENT 'purchase_id',
                    record_type VARCHAR(20) NOT NULL COMMENT 'type: IN, OUT, ADJ',
                    change_quantity DECIMAL(12, 4) NOT NULL COMMENT 'change',
                    balance_quantity DECIMAL(12, 4) COMMENT 'balance',
                    unit_cost DECIMAL(12, 4) COMMENT 'unit_cost',
                    remark VARCHAR(255) COMMENT 'remark',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES sys_tenants(id),
                    FOREIGN KEY (inventory_id) REFERENCES biz_inventory(id),
                    FOREIGN KEY (order_id) REFERENCES biz_orders(id),
                    FOREIGN KEY (purchase_id) REFERENCES biz_purchases(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='stock record'
            """))
            print("Done: biz_stock_records created")
            
            # 3. Update products table
            print("\n3. Update biz_products table...")
            try:
                db.session.execute(text("""
                    ALTER TABLE biz_products 
                    ADD COLUMN landed_cost DECIMAL(12, 4) DEFAULT 0.0 COMMENT 'landed_cost' AFTER latest_purchase_price,
                    ADD COLUMN platform_fee_rate DECIMAL(5, 4) DEFAULT 0.0 COMMENT 'platform_fee_rate' AFTER landed_cost
                """))
                print("Done: biz_products columns added")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("  (字段已存在, 跳过)")
                else:
                    raise
            
            db.session.commit()
            print("Success: Inventory and financial migration complete!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\nError during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    apply_stock_migration()
