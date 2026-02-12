"""
清理不需要的数据库字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import app
from app.extensions import db
from sqlalchemy import text

def cleanup_database():
    """清理不需要的字段"""
    with app.app_context():
        print("=" * 60)
        print("开始清理数据库...")
        print("=" * 60)
        
        try:
            # 1. 删除产品表不需要的字段
            print("\n1. 清理产品表...")
            try:
                db.session.execute(text("""
                    ALTER TABLE biz_products 
                    DROP COLUMN IF EXISTS keywords
                """))
                db.session.execute(text("""
                    ALTER TABLE biz_products 
                    DROP COLUMN IF EXISTS name_en
                """))
                db.session.execute(text("""
                    ALTER TABLE biz_products 
                    DROP COLUMN IF EXISTS name_cn
                """))
                print("✓ 产品表清理完成")
            except Exception as e:
                print(f"  产品表清理: {str(e)}")
            
            # 2. 删除订单表不需要的字段
            print("\n2. 清理订单表...")
            try:
                db.session.execute(text("""
                    ALTER TABLE biz_orders 
                    DROP COLUMN IF EXISTS matched_product_id
                """))
                db.session.execute(text("""
                    ALTER TABLE biz_orders 
                    DROP COLUMN IF EXISTS match_confidence
                """))
                db.session.execute(text("""
                    ALTER TABLE biz_orders 
                    DROP COLUMN IF EXISTS needs_manual_review
                """))
                db.session.execute(text("""
                    ALTER TABLE biz_orders 
                    DROP COLUMN IF EXISTS total_cost
                """))
                print("✓ 订单表清理完成")
            except Exception as e:
                print(f"  订单表清理: {str(e)}")
            
            # 3. 删除SKU映射表(如果存在)
            print("\n3. 删除SKU映射表...")
            try:
                db.session.execute(text("DROP TABLE IF EXISTS biz_sku_mappings"))
                print("✓ SKU映射表删除完成")
            except Exception as e:
                print(f"  SKU映射表删除: {str(e)}")
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✓ 数据库清理完成!")
            print("=" * 60)
            print("\n已删除字段:")
            print("产品表: keywords, name_en, name_cn")
            print("订单表: matched_product_id, match_confidence, needs_manual_review, total_cost")
            print("已删除表: biz_sku_mappings")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 清理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    cleanup_database()
