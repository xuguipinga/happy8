import sys
import os

# Add project route
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import app
from app.extensions import db
from sqlalchemy import text

def apply_manual_link_migration():
    """应用手动关联采购单功能迁移"""
    with app.app_context():
        print("=" * 60)
        print("Starting Manual Link Migration...")
        print("=" * 60)
        
        try:
            # 1. 创建关联表
            print("\n1. Create biz_order_purchase_links table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS biz_order_purchase_links (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    tenant_id INT NOT NULL,
                    order_id BIGINT NOT NULL,
                    purchase_id BIGINT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES sys_tenants(id),
                    FOREIGN KEY (order_id) REFERENCES biz_orders(id),
                    FOREIGN KEY (purchase_id) REFERENCES biz_purchases(id),
                    UNIQUE INDEX idx_order_purchase (order_id, purchase_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Order-Purchase M:N mapping'
            """))
            print("Done: biz_order_purchase_links created")
            
            db.session.commit()
            print("\n" + "=" * 60)
            print("Success: Manual Link migration complete!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\nError during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    apply_manual_link_migration()
