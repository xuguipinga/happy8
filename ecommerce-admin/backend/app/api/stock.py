from flask import request
from app.api import api
from app.services.stock_service import StockService
from app.common.responses import success_response, error_response
from app.utils.auth_helper import get_user_from_request
from app.utils.image_helper import compress_image

@api.route('/inventory', methods=['GET'])
def get_inventory():
    """获取库存列表"""
    user, error = get_user_from_request()
    if error: return error
    
    pagination = StockService.get_inventory_list(
        tenant_id=user.tenant_id,
        search=request.args.get('search', ''),
        status=request.args.get('status', ''),
        series=request.args.get('series', ''),
        page=int(request.args.get('page', 1)),
        per_page=int(request.args.get('per_page', 20)),
        sort_by=request.args.get('sort_by', 'model'),
        sort_order=request.args.get('sort_order', 'ascending')
    )
    
    items = [{
        'id': item.id,
        'model': item.model,
        'spec': item.spec,
        'series': item.series,
        'status': item.status,
        'image_url': item.image_url,
        'quantity': float(item.quantity),
        'unit': item.unit,
        'avg_cost': float(item.avg_cost),
        'updated_at': item.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    } for item in pagination.items]
    
    return success_response({'items': items, 'total': pagination.total})
    
@api.route('/inventory/series', methods=['GET'])
def get_inventory_series():
    """获取所有唯一的系列名称"""
    user, error = get_user_from_request()
    if error: return error
    
    series_list = StockService.get_unique_series(user.tenant_id)
    return success_response(series_list)

@api.route('/inventory', methods=['POST'])
def create_inventory():
    """手动创建新的型号库存项"""
    user, error = get_user_from_request()
    if error: return error
    
    try:
        inventory = StockService.create_inventory(
            tenant_id=user.tenant_id,
            data=request.json,
            operator_name=user.username
        )
        return success_response({'id': inventory.id}, message="创建成功")
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(str(e), code=500)

@api.route('/inventory/import', methods=['POST'])
def import_inventory():
    """从 Excel 批量导入库存型号和初现数量"""
    user, error = get_user_from_request()
    if error: return error
    
    if 'file' not in request.files:
        return error_response('请选择文件')
        
    clear_existing = request.form.get('clear_existing') == 'true'
    import_mode = request.form.get('import_mode', 'all')
    file = request.files['file']
    
    try:
        count, new_models = StockService.import_inventory(
            tenant_id=user.tenant_id,
            file_content=file.read(),
            clear_existing=clear_existing,
            operator_name=user.username,
            import_mode=import_mode
        )
        return success_response(message=f'成功处理 {count} 条数据，新增 {new_models} 个型号')
    except Exception as e:
        return error_response(f'解析失败: {str(e)}', code=500)

@api.route('/inventory/adjust', methods=['POST'])
def adjust_inventory():
    """手动调整库存 (入库/出库/报损)"""
    user, error = get_user_from_request()
    if error: return error
    
    data = request.json
    try:
        StockService.adjust_inventory(
            tenant_id=user.tenant_id,
            inventory_id=data.get('inventory_id'),
            change_qty=data.get('change_quantity', 0),
            record_type=data.get('record_type'),
            operator_name=user.username,
            unit_cost=data.get('unit_cost'),
            remark=data.get('remark', '')
        )
        return success_response(message='库存调整成功')
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(str(e), code=500)

@api.route('/inventory/records', methods=['GET'])
def get_stock_records():
    """获取库存流水记录"""
    user, error = get_user_from_request()
    if error: return error
    
    pagination = StockService.get_stock_records(
        tenant_id=user.tenant_id,
        inventory_id=request.args.get('inventory_id'),
        page=int(request.args.get('page', 1)),
        per_page=int(request.args.get('per_page', 20))
    )
    
    items = [{
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
    } for item in pagination.items]
    
    return success_response({'items': items, 'total': pagination.total})

@api.route('/inventory/<int:id>', methods=['PUT'])
def update_inventory_item(id):
    """手动修改库存信息"""
    user, error = get_user_from_request()
    if error: return error
    
    try:
        StockService.update_inventory(
            tenant_id=user.tenant_id,
            inventory_id=id,
            data=request.json,
            operator_name=user.username
        )
        return success_response(message='修改成功')
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(str(e), code=500)

@api.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory_item(id):
    """手动删除库存型号"""
    user, error = get_user_from_request()
    if error: return error
    
    try:
        StockService.delete_inventory(user.tenant_id, id)
        return success_response(message='删除成功')
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(str(e), code=500)

@api.route('/inventory/upload', methods=['POST'])
def upload_inventory_image():
    """上传库存图片并压缩"""
    user, error = get_user_from_request()
    if error: return error
    
    if 'file' not in request.files:
        return error_response('没有文件')
        
    file = request.files['file']
    if file.filename == '':
        return error_response('未选择文件')
        
    try:
        url = compress_image(file)
        return success_response({'url': url}, message='上传成功')
    except Exception as e:
        return error_response(str(e), code=500)
