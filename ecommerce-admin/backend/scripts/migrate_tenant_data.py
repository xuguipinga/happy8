"""
数据迁移脚本 - 多租户数据分配
用于将现有数据分配到不同的租户
"""
from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.order import Order
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.logistics import Logistics
from datetime import datetime


def create_default_tenant():
    """创建默认租户(如果不存在)"""
    tenant = Tenant.query.filter_by(code='DEFAULT').first()
    if not tenant:
        tenant = Tenant(
            name='默认租户',
            code='DEFAULT',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(tenant)
        db.session.commit()
        print(f"✓ 创建默认租户: {tenant.name} (ID: {tenant.id})")
    else:
        print(f"✓ 默认租户已存在: {tenant.name} (ID: {tenant.id})")
    return tenant


def assign_users_to_default_tenant(tenant_id):
    """将所有用户分配到默认租户"""
    users = User.query.filter_by(tenant_id=None).all()
    count = 0
    for user in users:
        user.tenant_id = tenant_id
        user.role = 'admin'  # 现有用户默认为管理员
        count += 1
    
    db.session.commit()
    print(f"✓ 已将 {count} 个用户分配到租户 {tenant_id}")


def assign_data_to_default_tenant(tenant_id):
    """将所有业务数据分配到默认租户"""
    
    # 订单
    orders = Order.query.filter_by(tenant_id=None).all()
    for order in orders:
        order.tenant_id = tenant_id
    order_count = len(orders)
    
    # 产品
    products = Product.query.filter_by(tenant_id=None).all()
    for product in products:
        product.tenant_id = tenant_id
    product_count = len(products)
    
    # 采购
    purchases = Purchase.query.filter_by(tenant_id=None).all()
    for purchase in purchases:
        purchase.tenant_id = tenant_id
    purchase_count = len(purchases)
    
    # 物流
    logistics = Logistics.query.filter_by(tenant_id=None).all()
    for log in logistics:
        log.tenant_id = tenant_id
    logistics_count = len(logistics)
    
    db.session.commit()
    
    print(f"✓ 已分配业务数据到租户 {tenant_id}:")
    print(f"  - 订单: {order_count}")
    print(f"  - 产品: {product_count}")
    print(f"  - 采购: {purchase_count}")
    print(f"  - 物流: {logistics_count}")


def migrate_data():
    """执行数据迁移"""
    print("=" * 60)
    print("开始多租户数据迁移...")
    print("=" * 60)
    
    # 1. 创建默认租户
    tenant = create_default_tenant()
    
    # 2. 分配用户
    assign_users_to_default_tenant(tenant.id)
    
    # 3. 分配业务数据
    assign_data_to_default_tenant(tenant.id)
    
    print("=" * 60)
    print("✓ 数据迁移完成!")
    print("=" * 60)
    print("\n提示:")
    print("1. 所有现有数据已分配到'默认租户'")
    print("2. 所有现有用户已设置为管理员角色")
    print("3. 如需创建新租户,请使用管理界面或API")
    print("4. 新注册用户将自动创建独立租户")


if __name__ == '__main__':
    from run import app
    with app.app_context():
        migrate_data()
