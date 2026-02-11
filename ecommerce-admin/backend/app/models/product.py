from app.extensions import db

class Product(db.Model):
    __tablename__ = 'biz_products'

    id = db.Column(db.BigInteger, primary_key=True)
    sku = db.Column(db.String(255), unique=True, index=True, nullable=False)
    name = db.Column(db.String(255))
    avg_cost_price = db.Column(db.Numeric(12, 4), default=0)
    latest_purchase_price = db.Column(db.Numeric(12, 4), default=0)
    stock_qty = db.Column(db.Numeric(12, 4), default=0)

    def __repr__(self):
        return f'<Product {self.sku}>'
