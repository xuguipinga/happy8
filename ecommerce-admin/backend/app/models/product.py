from app.extensions import db

class Product(db.Model):
    __tablename__ = 'biz_products'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('sys_tenants.id'), nullable=False, index=True, comment='租户ID')
    sku = db.Column(db.String(255), unique=True, index=True, nullable=False)
    name = db.Column(db.String(255))
    avg_cost_price = db.Column(db.Numeric(12, 4), default=0)
    latest_purchase_price = db.Column(db.Numeric(12, 4), default=0)
    landed_cost = db.Column(db.Numeric(12, 4), default=0.0, comment='落地成本(含运费)')
    platform_fee_rate = db.Column(db.Numeric(5, 4), default=0.0, comment='平台费率')

    def __repr__(self):
        return f'<Product {self.sku}>'
