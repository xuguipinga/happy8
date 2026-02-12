from datetime import datetime
from app.extensions import db

class Order(db.Model):
    __tablename__ = 'biz_orders'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('sys_tenants.id'), nullable=False, index=True, comment='租户ID')
    platform_order_no = db.Column(db.String(100), unique=True, index=True, nullable=False, comment='平台订单号')
    order_time = db.Column(db.DateTime, comment='下单时间')
    buyer_email = db.Column(db.String(150), index=True, comment='买家邮箱')
    company_name = db.Column(db.String(150), comment='公司名称')
    buyer_name = db.Column(db.String(100), comment='买家姓名')
    seller_name = db.Column(db.String(100), comment='卖家账号')
    product_name = db.Column(db.String(255), comment='商品名称')
    sku = db.Column(db.String(255), db.ForeignKey('biz_products.sku'), index=True, comment='SKU')
    quantity = db.Column(db.Integer, comment='数量')
    currency = db.Column(db.String(10), comment='币种')
    # 金额字段使用 Decimal (Numeric)
    # 金额字段使用 Decimal (Numeric) - 统一高精度 12,4
    unit_price = db.Column(db.Numeric(12, 4), comment='单价')
    order_amount = db.Column(db.Numeric(12, 4), comment='订单总额')
    shipping_fee_income = db.Column(db.Numeric(12, 4), comment='运费收入')
    discount_amount = db.Column(db.Numeric(12, 4), comment='折扣金额')
    actual_paid = db.Column(db.Numeric(12, 4), default=0.0, comment='实付金额')
    order_status = db.Column(db.String(50), comment='状态')
    order_type = db.Column(db.String(50), comment='订单类型')
    has_attachment = db.Column(db.Boolean, comment='是否有合同')
    actual_delivery_time = db.Column(db.DateTime, comment='实际发货时间')
    buyer_country = db.Column(db.String(50), comment='买家国家')
    tax_fee = db.Column(db.Numeric(12, 4), comment='税费')
    shipping_address = db.Column(db.Text, comment='收货地址')
    remark = db.Column(db.Text, comment='备注')
    
    # 新增字段 - 完善信息
    initial_payment = db.Column(db.Numeric(12, 4), comment='预付款')
    balance_payment = db.Column(db.Numeric(12, 4), comment='尾款')
    appointed_delivery_time = db.Column(db.DateTime, comment='约定发货时间')
    
    # 成本与利润分析字段
    cost_price = db.Column(db.Numeric(12, 4), default=0.0, comment='采购成本')
    logistics_cost = db.Column(db.Numeric(12, 4), default=0.0, comment='物流支出')
    profit = db.Column(db.Numeric(12, 4), comment='毛利')
    profit_rate = db.Column(db.Numeric(10, 4), default=0.0, comment='利润率')

    def __repr__(self):
        return f'<Order {self.platform_order_no}>'
