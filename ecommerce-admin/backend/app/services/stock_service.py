from decimal import Decimal
from app.extensions import db
from app.models.stock import Inventory, StockRecord
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.stock_record_repository import StockRecordRepository

class StockService:
    @classmethod
    def get_inventory_list(cls, tenant_id, search=None, status=None, page=1, per_page=20, sort_by='model', sort_order='ascending'):
        query = InventoryRepository.find_by_tenant(tenant_id, search, status)
        
        # 排序逻辑
        if sort_by == 'model':
            if sort_order == 'ascending':
                query = query.order_by(Inventory.model.asc(), Inventory.spec.asc())
            else:
                query = query.order_by(Inventory.model.desc(), Inventory.spec.desc())
        elif sort_by == 'updated_at':
            query = query.order_by(Inventory.updated_at.asc() if sort_order == 'ascending' else Inventory.updated_at.desc())
        
        return query.paginate(page=page, per_page=per_page)

    @classmethod
    def create_inventory(cls, tenant_id, data, operator_name):
        model = data.get('model')
        spec = data.get('spec', '')
        
        if not model:
            raise ValueError("型号不能为空")
            
        exists = InventoryRepository.find_by_model_and_spec(tenant_id, model, spec)
        if exists:
            raise ValueError("该型号规格已存在")
            
        initial_qty = Decimal(str(data.get('quantity', 0)))
        avg_cost = Decimal(str(data.get('avg_cost', 0)))
        
        inventory = Inventory(
            tenant_id=tenant_id,
            model=model,
            spec=spec,
            status=data.get('status', 'NORMAL'),
            quantity=initial_qty,
            unit=data.get('unit', 'pcs'),
            avg_cost=avg_cost,
            image_url=data.get('image_url')
        )
        
        db.session.add(inventory)
        db.session.flush()
        
        if initial_qty != 0:
            record = StockRecord(
                tenant_id=tenant_id,
                inventory_id=inventory.id,
                record_type='IN' if initial_qty > 0 else 'OUT',
                change_quantity=initial_qty,
                balance_quantity=initial_qty,
                unit_cost=avg_cost,
                remark='初始化库存',
                operator_name=operator_name
            )
            db.session.add(record)
            
        db.session.commit()
        return inventory

    @classmethod
    def adjust_inventory(cls, tenant_id, inventory_id, change_qty, record_type, operator_name, unit_cost=None, remark=''):
        inventory = InventoryRepository.get_by_id(inventory_id)
        if not inventory or inventory.tenant_id != tenant_id:
            raise ValueError("库存项目未找到")
            
        change_qty = Decimal(str(change_qty))
        if record_type == 'IN' and unit_cost is not None and change_qty > 0:
            unit_cost = Decimal(str(unit_cost))
            total_value = (inventory.quantity * inventory.avg_cost) + (change_qty * unit_cost)
            new_total_qty = inventory.quantity + change_qty
            if new_total_qty > 0:
                inventory.avg_cost = total_value / new_total_qty
        
        inventory.quantity += change_qty
        
        record = StockRecord(
            tenant_id=tenant_id,
            inventory_id=inventory.id,
            record_type=record_type,
            change_quantity=change_qty,
            balance_quantity=inventory.quantity,
            unit_cost=unit_cost or inventory.avg_cost,
            remark=remark,
            operator_name=operator_name
        )
        
        db.session.add(record)
        db.session.commit()
        return inventory

    @classmethod
    def get_stock_records(cls, tenant_id, inventory_id=None, page=1, per_page=20):
        query = StockRecordRepository.find_by_inventory(tenant_id, inventory_id)
        return query.paginate(page=page, per_page=per_page)

    @classmethod
    def update_inventory(cls, tenant_id, inventory_id, data, operator_name):
        inventory = InventoryRepository.get_by_id(inventory_id)
        if not inventory or inventory.tenant_id != tenant_id:
            raise ValueError("库存项目未找到")
            
        if 'model' in data: inventory.model = data['model']
        if 'spec' in data: inventory.spec = data['spec']
        if 'unit' in data: inventory.unit = data['unit']
        if 'avg_cost' in data: inventory.avg_cost = Decimal(str(data['avg_cost']))
        if 'image_url' in data: inventory.image_url = data['image_url']
        
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
                    operator_name=operator_name
                )
                db.session.add(record)
                inventory.quantity = new_qty
        
        db.session.commit()
        return inventory

    @classmethod
    def delete_inventory(cls, tenant_id, inventory_id):
        inventory = InventoryRepository.get_by_id(inventory_id)
        if not inventory or inventory.tenant_id != tenant_id:
            raise ValueError("库存项目未找到")
            
        StockRecord.query.filter_by(inventory_id=inventory_id).delete()
        db.session.delete(inventory)
        db.session.commit()

    @classmethod
    def import_inventory(cls, tenant_id, file_content, clear_existing, operator_name, import_mode='all'):
        from app.utils.inventory_parser import parse_inventory_excel
        
        if clear_existing:
            inv_ids = [inv.id for inv in Inventory.query.filter_by(tenant_id=tenant_id).all()]
            if inv_ids:
                StockRecord.query.filter(StockRecord.inventory_id.in_(inv_ids)).delete(synchronize_session=False)
                Inventory.query.filter(Inventory.id.in_(inv_ids)).delete(synchronize_session=False)
                db.session.flush()

        items = parse_inventory_excel(file_content)
        count = 0
        new_models = 0
        
        for item in items:
            invs = Inventory.query.filter_by(
                tenant_id=tenant_id, 
                model=item['model'], 
                spec=item['spec']
            ).all()
            
            if not invs:
                invs = Inventory.query.filter_by(
                    tenant_id=tenant_id,
                    model=item['model']
                ).all()
            
            if not invs:
                # 根据导入模式设置字段
                qty_to_set = item['quantity'] if import_mode in ['all', 'only_data'] else 0
                avg_cost_to_set = item.get('avg_cost', 0) if import_mode in ['all', 'only_data'] else 0
                image_url_to_set = item.get('image_url') if import_mode in ['all', 'only_image'] else None

                inv = Inventory(
                    tenant_id=tenant_id,
                    model=item['model'],
                    spec=item['spec'],
                    quantity=qty_to_set,
                    unit='pcs',
                    avg_cost=avg_cost_to_set,
                    image_url=image_url_to_set
                )
                db.session.add(inv)
                new_models += 1
                db.session.flush()
                if qty_to_set != 0:
                    record = StockRecord(
                        tenant_id=tenant_id,
                        inventory_id=inv.id,
                        record_type='IN' if qty_to_set > 0 else 'OUT',
                        change_quantity=qty_to_set,
                        balance_quantity=inv.quantity,
                        remark='Excel 批量导入' + (f' ({import_mode})' if import_mode != 'all' else ''),
                        operator_name=operator_name
                    )
                    db.session.add(record)
            else:
                for inv in invs:
                    # 仅在模式包含 data 时更新数量和成本
                    if import_mode in ['all', 'only_data'] and item['quantity'] != 0:
                        inv.quantity += item['quantity']
                        record = StockRecord(
                            tenant_id=tenant_id,
                            inventory_id=inv.id,
                            record_type='IN' if item['quantity'] > 0 else 'OUT',
                            change_quantity=item['quantity'],
                            balance_quantity=inv.quantity,
                            remark='Excel 批量导入 (同步数据)',
                            operator_name=operator_name
                        )
                        db.session.add(record)
                    
                    # 仅在模式包含 image 时更新图片
                    if import_mode in ['all', 'only_image'] and item.get('image_url'):
                        inv.image_url = item.get('image_url')
                    
                    # 仅在模式包含 data 时更新平均成本
                    if import_mode in ['all', 'only_data'] and item.get('avg_cost'):
                        inv.avg_cost = item.get('avg_cost')
                db.session.flush()
            count += 1
            
        db.session.commit()
        return count, new_models
