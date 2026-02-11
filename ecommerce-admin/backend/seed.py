from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 检查是否存在管理员
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            phone='13800138000',
            password_hash=generate_password_hash('123456'),
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("[SUCCESS] Admin user created! Account: admin / Password: 123456")
    else:
        print("[INFO] Admin user already exists.")
