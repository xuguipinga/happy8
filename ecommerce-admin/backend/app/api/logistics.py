from flask import request, jsonify
from app.api import api
from app.models.logistics import Logistics
from app.extensions import db
from sqlalchemy import desc

@api.route('/logistics', methods=['GET'])
def get_logistics():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Logistics.query.order_by(desc(Logistics.create_time))
    
    # 搜索功能
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Logistics.tracking_no.like(search_term)) | 
            (Logistics.ref_no.like(search_term))
        )
    
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
