from flask import request, jsonify
from app.api import api
from app.extensions import db
from app.models.stock import Inventory, StockRecord
from app.utils.auth_helper import get_user_from_request
from app.utils.inventory_parser import parse_inventory_excel # 导入解析器
from decimal import Decimal
from datetime import datetime

@api.route('/inventory', methods=['GET'])
def get_inventory():
    """获取库存列表"""
    user, error = get_user_from_request()
    if error: return error
    tenant_id = user.tenant_id
    
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    query = Inventory.query.filter_by(tenant_id=tenant_id)
    if search:
        query = query.filter(Inventory.model.ilike(f'%{search}%') | Inventory.spec.ilike(f'%{search}%'))
    
    if status == 'NORMAL':
        query = query.filter(Inventory.quantity > 5)
    elif status == 'LOW':
        query = query.filter(Inventory.quantity > 0, Inventory.quantity <= 5)
    elif status == 'OUT':
        query = query.filter(Inventory.quantity <= 0)
    
    pagination = query.order_by(Inventory.model.asc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'code': 200,
        'data': {
            'items': [{
                'id': item.id,
                'model': item.model,
                'spec': item.spec,
                'status': item.status,
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
    user, error = get_user_from_request()
    if error: return error
    tenant_id = user.tenant_id
    
    data = request.json
    model = data.get('model')
    spec = data.get('spec', '')
    status = data.get('status', 'NORMAL')
    unit = data.get('unit', 'pcs')
    
    def to_decimal(val, default=0):
        try:
            if val is None or str(val).strip() == '':
                return Decimal(str(default))
            return Decimal(str(val))
        except:
            return Decimal(str(default))

    initial_qty = to_decimal(data.get('quantity'))
    avg_cost = to_decimal(data.get('avg_cost'))
    
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
            status=status,
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
                remark='初始化库存',
                operator_name=user.username
            )
            db.session.add(record)
            
        db.session.commit()
        return jsonify({'code': 200, 'message': '创建成功', 'data': {'id': inventory.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

@api.route('/inventory/import', methods=['POST'])
def import_inventory():
    """从 Excel 批量导入库存型号和初现数量"""
    user, error = get_user_from_request()
    if error: return error
    tenant_id = user.tenant_id
    
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '请选择文件'}), 400
        
    clear_existing = request.form.get('clear_existing') == 'true'
    file = request.files['file']
    
    try:
        if clear_existing:
            # 获取该租户的所有库存 ID
            inv_ids = [inv.id for inv in Inventory.query.filter_by(tenant_id=tenant_id).all()]
            if inv_ids:
                # 删除流水记录
                StockRecord.query.filter(StockRecord.inventory_id.in_(inv_ids)).delete(synchronize_session=False)
                # 删除库存主表
                Inventory.query.filter(Inventory.id.in_(inv_ids)).delete(synchronize_session=False)
                db.session.flush()

        items = parse_inventory_excel(file.read())
        count = 0
        new_models = 0
        
        for item in items:
            # 查找或创建
            inv = Inventory.query.filter_by(
                tenant_id=tenant_id, 
                model=item['model'], 
                spec=item['spec']
            ).first()
            
            if not inv:
                inv = Inventory(
                    tenant_id=tenant_id,
                    model=item['model'],
                    spec=item['spec'],
                    quantity=item['quantity'],
                    unit='pcs'
                )
                db.session.add(inv)
                new_models += 1
            else:
                # 如果已存在，则累加数量（初始化导入场景）
                inv.quantity += item['quantity']
            
            db.session.flush() # 确保有 ID 进行记录
            
            # 记录流水
            if item['quantity'] != 0:
                record = StockRecord(
                    tenant_id=tenant_id,
                    inventory_id=inv.id,
                    record_type='IN' if item['quantity'] > 0 else 'OUT',
                    change_quantity=item['quantity'],
                    balance_quantity=inv.quantity,
                    remark='Excel 批量导入',
                    operator_name=user.username
                )
                db.session.add(record)
            
            count += 1
            
        db.session.commit()
        return jsonify({
            'code': 200, 
            'message': f'成功处理 {count} 条数据，新增 {new_models} 个型号'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'解析失败: {str(e)}'}), 500

@api.route('/inventory/adjust', methods=['POST'])
def adjust_inventory():
    """手动调整库存 (入库/出库/报损)"""
    user, error = get_user_from_request()
    if error: return error
    tenant_id = user.tenant_id
    
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
        remark=remark,
        operator_name=user.username
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'code': 200, 'message': '库存调整成功'})

@api.route('/inventory/records', methods=['GET'])
def get_stock_records():
    """获取库存流水记录"""
    user, error = get_user_from_request()
    if error: return error
    tenant_id = user.tenant_id
    
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
                'operator_name': item.operator_name,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for item in pagination.items],
            'total': pagination.total
        }
    })
@api.route('/inventory/<int:id>', methods=['PUT'])
def update_inventory_item(id):
    """手动修改库存信息"""
    user, error = get_user_from_request()
    if error: return error
    tenant_id = user.tenant_id
    
    data = request.json
    inventory = Inventory.query.filter_by(id=id, tenant_id=tenant_id).first()
    if not inventory:
        return jsonify({'code': 404, 'message': '库存项目未找到'}), 404
        
    try:
        # 更新字段
        if 'model' in data: inventory.model = data['model']
        if 'spec' in data: inventory.spec = data['spec']
        if 'unit' in data: inventory.unit = data['unit']
        if 'avg_cost' in data: inventory.avg_cost = Decimal(str(data['avg_cost']))
        
        # 如果直接修改了数量，记录一条流水
        if 'quantity' in data:
            new_qty = Decimal(str(data['quantity']))
            if new_qty != inventory.quantity:
                change = new_qty - inventory.quantity
                record = StockRecord(
                    tenant_id=tenant_id,
                    inventory_id=inventory.id,
                    record_type='ADJ',
                    change_quantity=change,
                    balance_quantity=new_qty,
                    remark='手动修改数量',
                    operator_name=user.username
                )
                db.session.add(record)
                inventory.quantity = new_qty
        
        db.session.commit()
        return jsonify({'code': 200, 'message': '修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

@api.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory_item(id):
    """手动删除库存型号"""
    user, error = get_user_from_request()
    if error: return error
    tenant_id = user.tenant_id
    
    inventory = Inventory.query.filter_by(id=id, tenant_id=tenant_id).first()
    if not inventory:
        return jsonify({'code': 404, 'message': '库存项目未找到'}), 404
        
    try:
        # 删除相关的流水记录
        StockRecord.query.filter_by(inventory_id=id).delete()
        # 删除主表记录
        db.session.delete(inventory)
        db.session.commit()
        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500
