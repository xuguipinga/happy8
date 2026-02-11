from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = 'sys_users'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('sys_users.id'), nullable=True)
    username = db.Column(db.String(50), unique=True, index=True)
    email = db.Column(db.String(100), unique=True, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 建立反向关系：主账号可以查询所有子账号
    children = db.relationship('User', backref=db.backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<User {self.username}>'
