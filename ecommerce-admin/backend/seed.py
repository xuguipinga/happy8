from app import create_app, db
from app.models.user import User
from app.models.tenant import Tenant
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    # 1. 确保存在默认租户
    default_tenant = Tenant.query.filter_by(code='DEFAULT').first()
    if not default_tenant:
        default_tenant = Tenant(
            name='默认租户',
            code='DEFAULT',
            is_active=True
        )
        db.session.add(default_tenant)
        db.session.flush() # 获取 ID
        print("[INFO] Default tenant created.")
    
    # 2. 检查是否存在管理员
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            phone='13800138000',
            password_hash=generate_password_hash('123456'),
            tenant_id=default_tenant.id,
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        print("[SUCCESS] Admin user created! Account: admin / Password: 123456")
    else:
        print("[INFO] Admin user already exists.")
    
    db.session.commit()
