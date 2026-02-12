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
    
    # 构建查询 - 添加租户过滤
    query = Purchase.query.filter_by(tenant_id=tenant_id).order_by(desc(Purchase.create_time))
    
    # 搜索功能
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Purchase.purchase_no.like(search_term)) | 
            (Purchase.sku.like(search_term)) |
            (Purchase.product_name.like(search_term)) |
            (Purchase.supplier_company.like(search_term)) |
            (Purchase.logistics_no.like(search_term))
        )

    if start_date:
        query = query.filter(Purchase.create_time >= start_date)
    if end_date:
        if len(end_date) == 10:
            end_date = end_date + ' 23:59:59'
        query = query.filter(Purchase.create_time <= end_date)
    
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
            'logistics_no': p.logistics_no,
            'receiver_address': p.receiver_address,
            
            # New fields
            'receiver_name': p.receiver_name,
            'receiver_phone': p.receiver_phone,
            'unit': p.unit,
            'model': p.model,
            'material_no': p.material_no,
            'buyer_note': p.buyer_note,
            'is_dropship': p.is_dropship,
            'upstream_order_no': p.upstream_order_no,
            'order_batch_no': p.order_batch_no,
            
            # Additional fields
            'shipper_name': p.shipper_name,
            'zip_code': p.zip_code,
            'product_no': p.product_no,
            'offer_id': p.offer_id,
            'category': p.category,
            'agent_name': p.agent_name,
            'agent_contact': p.agent_contact,
            'dropship_provider_id': p.dropship_provider_id,
            'micro_order_no': p.micro_order_no,
            'downstream_channel': p.downstream_channel,
            'order_company_entity': p.order_company_entity,
            'initiator_login_name': p.initiator_login_name,
            'is_auto_pay': p.is_auto_pay
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
