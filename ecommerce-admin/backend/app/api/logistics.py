from flask import request, jsonify
from app.api import api
from app.models.logistics import Logistics
from app.extensions import db
from sqlalchemy import desc

@api.route('/logistics', methods=['GET'])
def get_logistics():
    """获取物流列表 - 自动按租户过滤"""
    from app.utils.auth_helper import get_tenant_from_request
    
    # 获取租户上下文
    tenant_id, error = get_tenant_from_request()
    if error:
        return error
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询 - 添加租户过滤
    query = Logistics.query.filter_by(tenant_id=tenant_id).order_by(desc(Logistics.create_time))
    
    # 搜索功能
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Logistics.tracking_no.like(search_term)) | 
            (Logistics.ref_no.like(search_term)) |
            (Logistics.customer_order_no.like(search_term)) |
            (Logistics.ordering_account.like(search_term))
        )
        
    if start_date:
        query = query.filter(Logistics.sent_date >= start_date)
    if end_date:
        if len(end_date) == 10:
            end_date = end_date + ' 23:59:59'
        query = query.filter(Logistics.sent_date <= end_date)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    
    data = []
    for item in items:
        data.append({
            'id': item.id,
            'tracking_no': item.tracking_no,
            'ref_no': item.ref_no,
            'logistics_channel': item.logistics_channel,
            'order_status': item.order_status,
            'sent_date': item.sent_date.isoformat() if item.sent_date else None,
            'destination': item.destination,
            'zone': item.zone,
            'pre_weight': float(item.pre_weight) if item.pre_weight else 0,
            'actual_weight': float(item.actual_weight) if item.actual_weight else 0,
            'declared_value': float(item.declared_value) if item.declared_value else 0,
            'shipping_fee': float(item.shipping_fee) if item.shipping_fee else 0,
            'discount_fee': float(item.discount_fee) if item.discount_fee else 0,
            'actual_fee': float(item.actual_fee) if item.actual_fee else 0,
            'payment_method': item.payment_method,
            
            # New fields
            'service_type': item.service_type,
            'warehouse': item.warehouse,
            'inbound_time': item.inbound_time.isoformat() if item.inbound_time else None,
            'outbound_time': item.outbound_time.isoformat() if item.outbound_time else None,
            'payment_time': item.payment_time.isoformat() if item.payment_time else None,
            'customer_order_no': item.customer_order_no,
            'sender_name': item.sender_name,
            'sender_email': item.sender_email,
            'ordering_account': item.ordering_account,
            
            'create_time': item.create_time.isoformat() if item.create_time else None
        })
        
    return jsonify({
        'code': 200,
        'data': {
            'items': data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })
