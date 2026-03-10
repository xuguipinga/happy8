from datetime import datetime
from app.extensions import db

class Inventory(db.Model):
    """
    实物库存表
    存储 Model + Spec (型号 + 规格) 对应的当前可用数量
    """
    __tablename__ = 'biz_inventory'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('sys_tenants.id'), nullable=False, index=True, comment='租户ID')
    model = db.Column(db.String(100), index=True, nullable=False, comment='型号 (如 B002)')
    spec = db.Column(db.String(100), index=True, nullable=True, comment='规格/尺寸 (如 20cm)')
    quantity = db.Column(db.Numeric(12, 4), default=0.0, comment='当前库存数量')
    unit = db.Column(db.String(20), default='pcs', comment='单位')
    
    # 冗余字段用于快速取成本，也可以由流水推算
    avg_cost = db.Column(db.Numeric(12, 4), default=0.0, comment='平均入库成本')
    
    status = db.Column(db.String(20), default='NORMAL', comment='库存状态: NORMAL(普通), ADVANCED(高级)')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Inventory {self.model}-{self.spec}: {self.quantity}>'

class StockRecord(db.Model):
    """
    库存变动记录表 (出入库流水)
    用于追踪每一笔库存的去向或来源
    """
    __tablename__ = 'biz_stock_records'

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('sys_tenants.id'), nullable=False, index=True)
    inventory_id = db.Column(db.BigInteger, db.ForeignKey('biz_inventory.id'), nullable=False)
    
    # 关联信息
    order_id = db.Column(db.BigInteger, db.ForeignKey('biz_orders.id'), nullable=True, comment='关联订单ID (出库)')
    purchase_id = db.Column(db.BigInteger, db.ForeignKey('biz_purchases.id'), nullable=True, comment='关联采购单ID (入库)')
    
    record_type = db.Column(db.String(20), nullable=False, comment='类型: IN(入库), OUT(出库), ADJ(调整/报损)')
    change_quantity = db.Column(db.Numeric(12, 4), nullable=False, comment='变动数量')
    balance_quantity = db.Column(db.Numeric(12, 4), comment='变动后余量')
    
    unit_cost = db.Column(db.Numeric(12, 4), comment='本次变动的单价成本')
    remark = db.Column(db.String(255), comment='备注 (如: 报损、样品领取)')
    operator_name = db.Column(db.String(50), comment='操作人姓名')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系映射
    inventory = db.relationship('Inventory', backref=db.backref('records', lazy=True))
    order = db.relationship('Order', backref=db.backref('stock_records', lazy=True))
    purchase = db.relationship('Purchase', backref=db.backref('stock_records', lazy=True))

    def __repr__(self):
        return f'<StockRecord {self.record_type} {self.change_quantity}>'
