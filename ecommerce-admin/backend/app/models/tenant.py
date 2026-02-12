from datetime import datetime
from app.extensions import db

class Tenant(db.Model):
    """租户模型 - 代表公司/店铺"""
    __tablename__ = 'sys_tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, comment='公司/店铺名称')
    code = db.Column(db.String(50), unique=True, index=True, nullable=False, comment='租户代码')
    contact_person = db.Column(db.String(100), comment='联系人')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    contact_email = db.Column(db.String(100), comment='联系邮箱')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    # 反向关系
    users = db.relationship('User', backref='tenant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Tenant {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
