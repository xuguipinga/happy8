from flask import request, jsonify
from app.api import api
from app.models.order import Order
from app.extensions import db
from sqlalchemy import desc

@api.route('/orders', methods=['GET'])
def get_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Order.query.order_by(desc(Order.order_time))
    
    # 搜索功能
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Order.platform_order_no.like(search_term)) | 
            (Order.buyer_name.like(search_term)) |
            (Order.sku.like(search_term))
        )
    
    # 高级筛选: 日期范围
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        from datetime import datetime
        try:
            # 假设前端传的是 YYYY-MM-DD
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Order.order_time >= start_dt, Order.order_time <= end_dt)
        except ValueError:
            pass # 忽略格式错误的日期

    # 高级筛选: 订单状态 (支持多选，逗号分隔)
    status_param = request.args.get('order_status')
    if status_param:
        statuses = status_param.split(',')
        # 过滤空字符串
        statuses = [s for s in statuses if s]
        if statuses:
            query = query.filter(Order.order_status.in_(statuses))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items
    
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'platform_order_no': order.platform_order_no,
            'order_time': order.order_time.isoformat() if order.order_time else None,
            'buyer_email': order.buyer_email,
            'company_name': order.company_name,
            'buyer_name': order.buyer_name,
            'seller_name': order.seller_name,
            'product_name': order.product_name,
            'sku': order.sku,
            'quantity': order.quantity,
            'unit_price': float(order.unit_price) if order.unit_price else 0,
            'order_amount': float(order.order_amount) if order.order_amount else 0,
            'shipping_fee_income': float(order.shipping_fee_income) if order.shipping_fee_income else 0,
            'discount_amount': float(order.discount_amount) if order.discount_amount else 0,
            'actual_paid': float(order.actual_paid) if order.actual_paid else 0,
            'order_status': order.order_status,
            'order_type': order.order_type,
            'has_attachment': order.has_attachment,
            'actual_delivery_time': order.actual_delivery_time.isoformat() if order.actual_delivery_time else None,
            'buyer_country': order.buyer_country,
            'tax_fee': float(order.tax_fee) if order.tax_fee else 0,
            'shipping_address': order.shipping_address,
            'remark': order.remark,
            'currency': order.currency,
            'cost_price': float(order.cost_price) if order.cost_price else 0,
            'logistics_cost': float(order.logistics_cost) if order.logistics_cost else 0,
            'profit': float(order.profit) if order.profit else 0
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

@api.route('/orders/recalculate-profit', methods=['POST'])
def recalculate_profit():
    """重新计算所有订单的利润"""
    from app.services.profit_service import ProfitService
    try:
        result = ProfitService.recalculate_all_profits()
        if result['success']:
            return jsonify({
                'code': 200,
                'message': f"成功重新计算 {result['count']} 条订单的利润数据"
            })
        else:
            return jsonify({'code': 500, 'message': result['message']}), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@api.route('/orders/kpi', methods=['GET'])
def get_orders_kpi():
    """获取订单KPI统计数据"""
    from sqlalchemy import func
    from datetime import datetime, date, time
    
    try:
        # 获取今日起止时间 (假设服务器时间为准，或考虑时区)
        # 这里简单使用服务器本地时间
        today = date.today()
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)
        
        # 1. 今日订单数
        today_orders_count = Order.query.filter(Order.order_time >= start_of_day, Order.order_time <= end_of_day).count()
        
        # 2. 今日销售额 (sum order_amount)
        today_sales_result = db.session.query(func.sum(Order.order_amount)).filter(
            Order.order_time >= start_of_day, 
            Order.order_time <= end_of_day
        ).scalar()
        today_sales = float(today_sales_result) if today_sales_result else 0.0
        
        # 3. 今日毛利 (sum profit)
        today_profit_result = db.session.query(func.sum(Order.profit)).filter(
            Order.order_time >= start_of_day, 
            Order.order_time <= end_of_day
        ).scalar()
        today_profit = float(today_profit_result) if today_profit_result else 0.0
        
        # 4. 累计订单数
        total_orders_count = Order.query.count()
        
        return jsonify({
            'code': 200,
            'data': {
                'today_orders': today_orders_count,
                'today_sales': today_sales,
                'today_profit': today_profit,
                'total_orders': total_orders_count
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500
