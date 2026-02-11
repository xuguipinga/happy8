from flask import request, jsonify
from app.api import api
from app.models.purchase import Purchase
from app.extensions import db
from sqlalchemy import desc

@api.route('/purchases', methods=['GET'])
def get_purchases():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Purchase.query.order_by(desc(Purchase.create_time))
    
    # 搜索功能
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Purchase.purchase_no.like(search_term)) | 
            (Purchase.sku.like(search_term)) |
            (Purchase.product_name.like(search_term))
        )
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    purchases = pagination.items
    
    data = []
    for p in purchases:
        data.append({
            'id': p.id,
            'purchase_no': p.purchase_no,
            'supplier_company': p.supplier_company,
            'supplier_member': p.supplier_member,
            'buyer_company': p.buyer_company,
            'buyer_member': p.buyer_member,
            'sku': p.sku,
            'product_name': p.product_name,
            'quantity': float(p.quantity) if p.quantity else 0,
            'unit_price': float(p.unit_price) if p.unit_price else 0,
            'goods_amount': float(p.goods_amount) if p.goods_amount else 0,
            'shipping_fee': float(p.shipping_fee) if p.shipping_fee else 0,
            'discount': float(p.discount) if p.discount else 0,
            'actual_payment': float(p.actual_payment) if p.actual_payment else 0,
            'order_status': p.order_status,
            'create_time': p.create_time.isoformat() if p.create_time else None,
            'pay_time': p.pay_time.isoformat() if p.pay_time else None,
            'logistics_company': p.logistics_company,
            'logistics_no': p.logistics_no,
            'receiver_address': p.receiver_address
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
