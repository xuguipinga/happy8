from datetime import datetime
from app.extensions import db

class Logistics(db.Model):
    __tablename__ = 'biz_logistics'

    id = db.Column(db.BigInteger, primary_key=True)
    tracking_no = db.Column(db.String(100), unique=True, index=True, nullable=False, comment='运单号')
    ref_no = db.Column(db.String(100), index=True, comment='参考号/订单号')
    logistics_channel = db.Column(db.String(100), comment='物流渠道')
    order_status = db.Column(db.String(50), comment='订单状态')
    sent_date = db.Column(db.Date, comment='发货日期')
    destination = db.Column(db.String(50), comment='目的地')
    zone = db.Column(db.String(20), comment='分区')
    pre_weight = db.Column(db.Numeric(10, 3), comment='预报重量')
    actual_weight = db.Column(db.Numeric(10, 3), comment='实际重量')
    declared_value = db.Column(db.Numeric(12, 4), comment='申报价值')
    shipping_fee = db.Column(db.Numeric(12, 4), comment='运费')
    discount_fee = db.Column(db.Numeric(12, 4), comment='优惠金额')
    actual_fee = db.Column(db.Numeric(12, 4), comment='实收运费')
    payment_method = db.Column(db.String(50), comment='支付方式')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def __repr__(self):
        return f'<Logistics {self.tracking_no}>'
