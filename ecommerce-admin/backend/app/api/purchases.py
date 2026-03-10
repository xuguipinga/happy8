from flask import request, jsonify
from app.api import api
from app.models.purchase import Purchase
from app.extensions import db
from sqlalchemy import desc

@api.route('/purchases', methods=['GET'])
def get_purchases():
    """获取采购列表 - 自动按租户过滤"""
    from app.utils.auth_helper import get_tenant_from_request
    
    # 获取租户上下文
    tenant_id, error = get_tenant_from_request()
    if error:
        return error
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'create_time')
    sort_order = request.args.get('sort_order', 'descending')
    
    # 构建查询 - 添加租户过滤
    query = Purchase.query.filter_by(tenant_id=tenant_id)
    
    # 搜索功能
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if search:
        search_term = f"%{search}%"
        # We need to join PurchaseItem to search its fields, and use distinct to prevent duplicate Parents
        query = query.outerjoin(PurchaseItem, Purchase.id == PurchaseItem.purchase_id).filter(
            (Purchase.purchase_no.like(search_term)) | 
            (PurchaseItem.sku.like(search_term)) |
            (PurchaseItem.product_name.like(search_term)) |
            (Purchase.supplier_company.like(search_term)) |
            (Purchase.logistics_no.like(search_term))
        ).distinct()

    if start_date:
        query = query.filter(Purchase.create_time >= start_date)
    if end_date:
        if len(end_date) == 10:
            end_date = end_date + ' 23:59:59'
        query = query.filter(Purchase.create_time <= end_date)
        
    # 应用排序
    if sort_by == 'create_time':
        query = query.order_by(Purchase.create_time.asc() if sort_order == 'ascending' else Purchase.create_time.desc())
    elif sort_by == 'purchase_no':
        query = query.order_by(Purchase.purchase_no.asc() if sort_order == 'ascending' else Purchase.purchase_no.desc())
    elif sort_by == 'actual_payment':
        query = query.order_by(Purchase.actual_payment.asc() if sort_order == 'ascending' else Purchase.actual_payment.desc())
    else:
        query = query.order_by(Purchase.create_time.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    purchases = pagination.items
    
    data = []
    for p in purchases:
        purchase_items = []
        for item in p.items:
            purchase_items.append({
                'id': item.id,
                'sku': item.sku,
                'product_name': item.product_name,
                'model': item.model,
                'material_no': item.material_no,
                'product_no': item.product_no,
                'offer_id': item.offer_id,
                'quantity': float(item.quantity) if item.quantity else 0,
                'unit_price': float(item.unit_price) if item.unit_price else 0,
                'goods_amount': float(item.goods_amount) if item.goods_amount else 0
            })
            
        data.append({
            'id': p.id,
            'purchase_no': p.purchase_no,
            'supplier_company': p.supplier_company,
            'supplier_member': p.supplier_member,
            'buyer_company': p.buyer_company,
            'buyer_member': p.buyer_member,
            'sku': p.sku,
            'quantity': float(p.quantity) if p.quantity else 0,
            'goods_amount': float(p.goods_amount) if p.goods_amount else 0,
            'shipping_fee': float(p.shipping_fee) if p.shipping_fee else 0,
            'discount': float(p.discount) if p.discount else 0,
            'actual_payment': float(p.actual_payment) if p.actual_payment else 0,
            'order_status': p.order_status,
            'create_time': p.create_time.isoformat() if p.create_time else None,
            'pay_time': p.pay_time.isoformat() if p.pay_time else None,
            'logistics_company': p.logistics_company,
            'logistics_no': p.logistics_no,
            'receiver_address': p.receiver_address,
            'receiver_name': p.receiver_name,
            'receiver_phone': p.receiver_phone,
            'unit': p.unit,
            'buyer_note': p.buyer_note,
            'is_dropship': p.is_dropship,
            'upstream_order_no': p.upstream_order_no,
            'order_batch_no': p.order_batch_no,
            'shipper_name': p.shipper_name,
            'zip_code': p.zip_code,
            'category': p.category,
            'agent_name': p.agent_name,
            'agent_contact': p.agent_contact,
            'dropship_provider_id': p.dropship_provider_id,
            'micro_order_no': p.micro_order_no,
            'downstream_channel': p.downstream_channel,
            'order_company_entity': p.order_company_entity,
            'initiator_login_name': p.initiator_login_name,
            'is_auto_pay': p.is_auto_pay,
            'items': purchase_items
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
