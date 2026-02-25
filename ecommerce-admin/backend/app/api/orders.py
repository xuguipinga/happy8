from flask import request, jsonify
from app.api import api
from app.models.order import Order
from app.extensions import db
from sqlalchemy import desc
from app.middleware import require_auth
from flask import g

STATUS_MAP = {
    'Pending': ['待买家付款'],
    'Paid': ['待卖家发货'],
    'Shipped': ['待买家确认收货', '发货中'],
    'Completed': ['订单完成'],
    'Cancelled': ['订单关闭']
}

def map_statuses(status_param):
    """将前端传来的英文状态转换为数据库中的中文状态"""
    if not status_param:
        return None
    
    frontend_statuses = [s for s in status_param.split(',') if s]
    db_statuses = []
    for s in frontend_statuses:
        if s in STATUS_MAP:
            db_statuses.extend(STATUS_MAP[s])
        else:
            db_statuses.append(s)
    return db_statuses

@api.route('/orders', methods=['GET'])
@require_auth
def get_orders():
    """获取订单列表 - 自动按租户过滤，并按订单号聚合商品"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 步骤1: 构建包含所有过滤条件的查询
    query = Order.query.filter_by(tenant_id=g.tenant_id)
    
    # 搜索功能
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Order.platform_order_no.like(search_term)) | 
            (Order.buyer_name.like(search_term)) |
            (Order.sku.like(search_term)) |
            (Order.product_name.like(search_term)) |
            (Order.company_name.like(search_term)) |
            (Order.buyer_email.like(search_term))
        )
    
    # 高级筛选: 日期范围
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Order.order_time >= start_dt, Order.order_time <= end_dt)
        except ValueError:
            pass

    # 高级筛选: 订单状态
    status_param = request.args.get('order_status')
    if status_param:
        db_statuses = map_statuses(status_param)
        if db_statuses:
            query = query.filter(Order.order_status.in_(db_statuses))
    
    # 步骤2: 获取满足条件的“唯一订单号”列表，按最新下单时间排序
    from sqlalchemy import func
    
    # 使用子查询找到符合条件的订单ID，再分组统计分页
    subq = query.with_entities(Order.id).subquery()
    stmt = db.session.query(
        Order.platform_order_no,
        func.max(Order.order_time).label('latest_time')
    ).filter(Order.id.in_(subq)) \
     .group_by(Order.platform_order_no) \
     .order_by(desc('latest_time'))
    
    pagination = stmt.paginate(page=page, per_page=per_page, error_out=False)
    paged_order_nos = [item[0] for item in pagination.items]
    
    if not paged_order_nos:
        return jsonify({
            'code': 200,
            'data': {
                'items': [],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        })

    # 步骤3: 获取这些订单号对应的全量明细
    all_order_items = Order.query.filter(
        Order.platform_order_no.in_(paged_order_nos),
        Order.tenant_id == g.tenant_id
    ).order_by(desc(Order.order_time)).all()
    
    # 步骤4: 在内存中以订单号为 Key 进行聚合
    aggregated_map = {no: {
        'platform_order_no': no,
        'items': [],
        'total_quantity': 0,
        'total_cost': 0,
        'total_profit': 0,
        'total_logistics_cost': 0,
        'order_time': None # 待填充
    } for no in paged_order_nos}

    for item in all_order_items:
        order_no = item.platform_order_no
        if order_no not in aggregated_map: continue
        
        group = aggregated_map[order_no]
        
        # 填充订单基础信息 (仅在第一次遇到该订单号时)
        if group['order_time'] is None:
            group.update({
                'order_time': item.order_time.isoformat() if item.order_time else None,
                'buyer_email': item.buyer_email,
                'company_name': item.company_name,
                'buyer_name': item.buyer_name,
                'seller_name': item.seller_name,
                'order_status': item.order_status,
                'order_type': item.order_type,
                'buyer_country': item.buyer_country,
                'shipping_address': item.shipping_address,
                'remark': item.remark,
                'currency': item.currency,
                'order_amount': float(item.order_amount) if item.order_amount else 0,
                'actual_paid': float(item.actual_paid) if item.actual_paid else 0,
                'tax_fee': float(item.tax_fee) if item.tax_fee else 0,
                'shipping_fee_income': float(item.shipping_fee_income) if item.shipping_fee_income else 0,
                'discount_amount': float(item.discount_amount) if item.discount_amount else 0,
                'initial_payment': float(item.initial_payment) if item.initial_payment else 0,
                'balance_payment': float(item.balance_payment) if item.balance_payment else 0,
                'appointed_delivery_time': item.appointed_delivery_time.isoformat() if item.appointed_delivery_time else None,
                'actual_delivery_time': item.actual_delivery_time.isoformat() if item.actual_delivery_time else None,
                'has_attachment': item.has_attachment
            })

        # 添加商品子项
        group['items'].append({
            'id': item.id,
            'product_name': item.product_name,
            'sku': item.sku,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price) if item.unit_price else 0,
            'cost_price': float(item.cost_price) if item.cost_price else 0,
            'logistics_cost': float(item.logistics_cost) if item.logistics_cost else 0,
            'profit': float(item.profit) if item.profit else 0
        })
        
        # 累加统计字段
        group['total_quantity'] += (item.quantity or 0)
        group['total_cost'] += (float(item.cost_price) if item.cost_price else 0)
        group['total_profit'] += (float(item.profit) if item.profit else 0)
        group['total_logistics_cost'] += (float(item.logistics_cost) if item.logistics_cost else 0)

    # 按照分页请求的订单号顺序排序
    final_list = [aggregated_map[no] for no in paged_order_nos if no in aggregated_map]
        
    return jsonify({
        'code': 200,
        'data': {
            'items': final_list,
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
@require_auth
def get_orders_kpi():
    """获取订单KPI统计数据 - 按租户隔离"""
    from sqlalchemy import func
    from datetime import date, time, datetime
    
    tenant_id = g.tenant_id
    # 获取参数
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status_param = request.args.get('order_status')
    
    try:
        # 基础查询（租户隔离）
        # 这里使用 with_entities(Order.id) 是为了后续子查询高效，但统计时我们需要 platform_order_no
        base_query = Order.query.filter(Order.tenant_id == tenant_id)
        
        # 应用全局搜索过滤 (search & status)
        if search:
            search_term = f"%{search}%"
            search_filter = (
                (Order.platform_order_no.like(search_term)) | 
                (Order.buyer_name.like(search_term)) |
                (Order.sku.like(search_term)) |
                (Order.product_name.like(search_term)) |
                (Order.company_name.like(search_term)) |
                (Order.buyer_email.like(search_term))
            )
            base_query = base_query.filter(search_filter)
            
        if status_param:
            db_statuses = map_statuses(status_param)
            if db_statuses:
                base_query = base_query.filter(Order.order_status.in_(db_statuses))

        # --- 1. “本期”统计 (针对日期范围或今日) ---
        if start_date and end_date:
            start_of_period = datetime.strptime(start_date, '%Y-%m-%d')
            end_of_period = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        else:
            today = date.today()
            start_of_period = datetime.combine(today, time.min)
            end_of_period = datetime.combine(today, time.max)
            
        period_query = base_query.filter(Order.order_time >= start_of_period, Order.order_time <= end_of_period)
        
        # 执行本期汇总 (使用子查询避免 group by 导致的 count 偏差)
        period_subq = period_query.with_entities(Order.id).subquery()
        period_stats = db.session.query(
            func.count(Order.platform_order_no.distinct()),
            func.sum(Order.order_amount),
            func.sum(Order.profit)
        ).filter(Order.id.in_(period_subq)).first()
        
        today_orders_count = period_stats[0] or 0
        today_sales = float(period_stats[1]) if period_stats[1] else 0.0
        today_profit = float(period_stats[2]) if period_stats[2] else 0.0
        
        # --- 2. “累计”统计 (仅受搜索和状态过滤，不受日期影响) ---
        total_subq = base_query.with_entities(Order.id).subquery()
        total_stats = db.session.query(
            func.count(Order.platform_order_no.distinct()),
            func.sum(Order.order_amount),
            func.sum(Order.profit)
        ).filter(Order.id.in_(total_subq)).first()
        
        total_orders_count = total_stats[0] or 0
        total_sales = float(total_stats[1]) if total_stats[1] else 0.0
        total_profit = float(total_stats[2]) if total_stats[2] else 0.0
        
        return jsonify({
            'code': 200,
            'data': {
                'today_orders': today_orders_count,
                'today_sales': today_sales,
                'today_profit': today_profit,
                'total_orders': total_orders_count,
                'total_sales': total_sales,
                'total_profit': total_profit
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': str(e)}), 500
