from datetime import datetime
from app.extensions import db

class Purchase(db.Model):
    __tablename__ = 'biz_purchases'

    id = db.Column(db.BigInteger, primary_key=True)
    purchase_no = db.Column(db.String(100), unique=True, index=True, nullable=False, comment='采购单号')
    supplier_company = db.Column(db.String(150), comment='供应商公司')
    supplier_member = db.Column(db.String(100), comment='供应商对接人')
    buyer_company = db.Column(db.String(150), comment='采购方公司')
    buyer_member = db.Column(db.String(100), comment='采购员')
    sku = db.Column(db.String(255), db.ForeignKey('biz_products.sku'), index=True, nullable=False, comment='SKU')
    product_name = db.Column(db.String(255), comment='货品标题')
    quantity = db.Column(db.Numeric(12, 4), comment='采购数量')
    unit_price = db.Column(db.Numeric(12, 4), comment='采购单价')
    goods_amount = db.Column(db.Numeric(12, 4), comment='货品总价')
    shipping_fee = db.Column(db.Numeric(12, 4), comment='运费')
    discount = db.Column(db.Numeric(12, 4), comment='折扣')
    actual_payment = db.Column(db.Numeric(12, 4), comment='实付款')
    order_status = db.Column(db.String(50), comment='采购状态')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    pay_time = db.Column(db.DateTime, comment='付款时间')
    logistics_company = db.Column(db.String(100), comment='物流公司')
    logistics_no = db.Column(db.String(100), comment='物流单号')
    receiver_address = db.Column(db.Text, comment='收货地址')

    def __repr__(self):
        return f'<Purchase {self.purchase_no}>'
