from datetime import datetime
from app.extensions import db

class Purchase(db.Model):
    __tablename__ = 'biz_purchases'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('sys_tenants.id'), nullable=False, index=True, comment='租户ID')
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

    # 新增字段 - 完善信息
    receiver_name = db.Column(db.String(100), comment='收货人姓名')
    receiver_phone = db.Column(db.String(50), comment='联系电话')
    receiver_mobile = db.Column(db.String(50), comment='联系手机')
    unit = db.Column(db.String(20), comment='单位')
    model = db.Column(db.String(100), comment='型号')
    material_no = db.Column(db.String(100), comment='物料编号')
    buyer_note = db.Column(db.Text, comment='买家留言')
    
    invoice_title = db.Column(db.String(200), comment='发票抬头')
    tax_id = db.Column(db.String(100), comment='纳税人识别号')
    invoice_address_phone = db.Column(db.String(255), comment='发票地址电话')
    invoice_bank_account = db.Column(db.String(255), comment='发票开户行及账号')
    invoice_receiver_address = db.Column(db.Text, comment='发票收票地址')
    
    is_dropship = db.Column(db.Boolean, comment='是否代发')
    upstream_order_no = db.Column(db.String(100), comment='下游订单号')
    order_batch_no = db.Column(db.String(100), comment='下单批次号')
    
    # 更多完善字段
    shipper_name = db.Column(db.String(100), comment='发货方')
    zip_code = db.Column(db.String(20), comment='邮编')
    product_no = db.Column(db.String(100), comment='货号')
    offer_id = db.Column(db.String(100), comment='Offer ID')
    category = db.Column(db.String(100), comment='货品种类')
    agent_name = db.Column(db.String(100), comment='代理商姓名')
    agent_contact = db.Column(db.String(100), comment='代理商联系方式')
    dropship_provider_id = db.Column(db.String(100), comment='代发服务商id')
    micro_order_no = db.Column(db.String(100), comment='微商订单号')
    downstream_channel = db.Column(db.String(100), comment='下游渠道')
    order_company_entity = db.Column(db.String(100), comment='下单公司主体')
    initiator_login_name = db.Column(db.String(100), comment='发起人登录名')
    is_auto_pay = db.Column(db.String(100), comment='是否发起免密支付')

    def __repr__(self):
        return f'<Purchase {self.purchase_no}>'
