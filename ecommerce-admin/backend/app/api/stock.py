from flask import request, jsonify
from app.api import api
from app.extensions import db
from app.models.stock import Inventory, StockRecord
from app.utils.auth_helper import get_tenant_from_request
from decimal import Decimal
from datetime import datetime

@api.route('/inventory', methods=['GET'])
def get_inventory():
    """获取库存列表"""
    tenant_id, error = get_tenant_from_request()
    if error: return error
    
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    query = Inventory.query.filter_by(tenant_id=tenant_id)
    if search:
        query = query.filter(Inventory.model.ilike(f'%{search}%') | Inventory.spec.ilike(f'%{search}%'))
    
    pagination = query.order_by(Inventory.updated_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [{
                'id': item.id,
                'model': item.model,
                'spec': item.spec,
                'quantity': float(item.quantity),
                'unit': item.unit,
                'avg_cost': float(item.avg_cost),
                'updated_at': item.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            } for item in pagination.items],
            'total': pagination.total
        }
    })

@api.route('/inventory', methods=['POST'])
def create_inventory():
    """手动创建新的型号库存项"""
    tenant_id, error = get_tenant_from_request()
    if error: return error
    
    data = request.json
    model = data.get('model')
    spec = data.get('spec', '')
    unit = data.get('unit', 'pcs')
    initial_qty = Decimal(str(data.get('quantity', 0)))
    avg_cost = Decimal(str(data.get('avg_cost', 0)))
    
    if not model:
        return jsonify({'code': 400, 'message': '型号不能为空'}), 400
        
    # 检查是否已存在
    exists = Inventory.query.filter_by(tenant_id=tenant_id, model=model, spec=spec).first()
    if exists:
        return jsonify({'code': 400, 'message': '该型号规格已存在，请使用调整功能'}), 400
        
    try:
        inventory = Inventory(
            tenant_id=tenant_id,
            model=model,
            spec=spec,
            quantity=initial_qty,
            unit=unit,
            avg_cost=avg_cost
        )
        db.session.add(inventory)
        db.session.flush() # 获取 ID
        
        # 如果有初始数量，记录一条流水
        if initial_qty != 0:
            record = StockRecord(
                tenant_id=tenant_id,
                inventory_id=inventory.id,
                record_type='IN' if initial_qty > 0 else 'OUT',
                change_quantity=initial_qty,
                balance_quantity=initial_qty,
                unit_cost=avg_cost,
                remark='初始化库存'
            )
            db.session.add(record)
            
        db.session.commit()
        return jsonify({'code': 200, 'message': '创建成功', 'data': {'id': inventory.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

@api.route('/inventory/adjust', methods=['POST'])
def adjust_inventory():
    """手动调整库存 (入库/出库/报损)"""
    tenant_id, error = get_tenant_from_request()
    if error: return error
    
    data = request.json
    inventory_id = data.get('inventory_id')
    change_qty = Decimal(str(data.get('change_quantity', 0)))
    record_type = data.get('record_type') # IN, OUT, ADJ
    unit_cost = Decimal(str(data.get('unit_cost', 0))) if data.get('unit_cost') else None
    remark = data.get('remark', '')
    
    inventory = Inventory.query.filter_by(id=inventory_id, tenant_id=tenant_id).first()
    if not inventory:
        return jsonify({'code': 404, 'message': '库存项目未找到'}), 404
        
    # 如果是入库，更新平均成本 (加权平均)
    if record_type == 'IN' and unit_cost is not None and change_qty > 0:
        total_value = (inventory.quantity * inventory.avg_cost) + (change_qty * unit_cost)
        new_total_qty = inventory.quantity + change_qty
        if new_total_qty > 0:
            inventory.avg_cost = total_value / new_total_qty
            
    # 更新数量
    inventory.quantity += change_qty
    
    # 记录流水
    record = StockRecord(
        tenant_id=tenant_id,
        inventory_id=inventory.id,
        record_type=record_type,
        change_quantity=change_qty,
        balance_quantity=inventory.quantity,
        unit_cost=unit_cost or inventory.avg_cost,
        remark=remark
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '库存调整成功'})

@api.route('/inventory/records', methods=['GET'])
def get_stock_records():
    """获取库存流水记录"""
    tenant_id, error = get_tenant_from_request()
    if error: return error
    
    inventory_id = request.args.get('inventory_id')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    query = StockRecord.query.filter_by(tenant_id=tenant_id)
    if inventory_id:
        query = query.filter_by(inventory_id=inventory_id)
        
    pagination = query.order_by(StockRecord.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [{
                'id': item.id,
                'inventory_id': item.inventory_id,
                'model': item.inventory.model,
                'spec': item.inventory.spec,
                'record_type': item.record_type,
                'change_quantity': float(item.change_quantity),
                'balance_quantity': float(item.balance_quantity),
                'unit_cost': float(item.unit_cost) if item.unit_cost else 0,
                'order_no': item.order.platform_order_no if item.order else None,
                'purchase_no': item.purchase.purchase_no if item.purchase else None,
                'remark': item.remark,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for item in pagination.items],
            'total': pagination.total
        }
    })
