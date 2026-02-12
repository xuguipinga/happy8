from datetime import datetime
from app.extensions import db

class Logistics(db.Model):
    __tablename__ = 'biz_logistics'

    id = db.Column(db.BigInteger, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('sys_tenants.id'), nullable=False, index=True, comment='租户ID')
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
    
    # 新增字段 - 完善信息
    service_type = db.Column(db.String(100), comment='服务类型')
    warehouse = db.Column(db.String(100), comment='仓库')
    inbound_time = db.Column(db.DateTime, comment='入库时间')
    outbound_time = db.Column(db.DateTime, comment='出库时间')
    payment_time = db.Column(db.DateTime, comment='支付时间')
    customer_order_no = db.Column(db.String(100), comment='客户订单号')
    sender_name = db.Column(db.String(100), comment='发件人姓名')
    sender_email = db.Column(db.String(150), comment='发件人邮件')
    ordering_account = db.Column(db.String(100), comment='下单账号')

    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def __repr__(self):
        return f'<Logistics {self.tracking_no}>'
