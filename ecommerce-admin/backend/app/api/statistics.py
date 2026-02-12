"""
统计API - 采购、订单、物流分模块统计
"""
from flask import request, jsonify, g
from app.api import api
from app.models.purchase import Purchase
from app.models.order import Order
from app.models.logistics import Logistics
from app.extensions import db
from app.middleware import require_auth
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from decimal import Decimal


@api.route('/statistics/purchases', methods=['GET'])
@require_auth
def get_purchase_statistics():
    period = request.args.get('period', 'month')  # day/week/month/quarter/year
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')
    
    query = Purchase.query.filter_by(tenant_id=g.tenant_id)
    
    # 搜索功能 - 与 list API 保持一致
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Purchase.purchase_no.like(search_term)) | 
            (Purchase.sku.like(search_term)) |
            (Purchase.product_name.like(search_term)) |
            (Purchase.supplier_company.like(search_term)) |
            (Purchase.logistics_no.like(search_term))
        )
    
    # 日期过滤
    if start_date:
        query = query.filter(Purchase.create_time >= start_date)
    if end_date:
        if len(end_date) == 10:  # YYYY-MM-DD
            end_date = end_date + ' 23:59:59'
        query = query.filter(Purchase.create_time <= end_date)
    
    # 按时间维度分组
    if period == 'day':
        date_format = func.date(Purchase.create_time)
        group_by = date_format
    elif period == 'week':
        date_format = func.concat(
            func.year(Purchase.create_time), 
            '-W', 
            func.lpad(func.week(Purchase.create_time), 2, '0')
        )
        group_by = func.yearweek(Purchase.create_time)
    elif period == 'month':
        date_format = func.date_format(Purchase.create_time, '%Y-%m')
        group_by = func.date_format(Purchase.create_time, '%Y-%m')
    elif period == 'quarter':
        date_format = func.concat(
            func.year(Purchase.create_time),
            '-Q',
            func.quarter(Purchase.create_time)
        )
        group_by = func.concat(
            func.year(Purchase.create_time),
            func.quarter(Purchase.create_time)
        )
    else:  # year
        date_format = func.year(Purchase.create_time)
        group_by = func.year(Purchase.create_time)
    
    # 聚合查询
    results = db.session.query(
        date_format.label('date'),
        func.sum(Purchase.actual_payment).label('purchase_amount'),
        func.sum(Purchase.shipping_fee).label('logistics_fee'),
        func.sum(Purchase.actual_payment + func.coalesce(Purchase.shipping_fee, 0)).label('total_cost'),
        func.sum(Purchase.quantity).label('quantity'),
        func.count(Purchase.id).label('purchase_count')
    ).filter(
        Purchase.tenant_id == g.tenant_id
    )
    
    if start_date:
        results = results.filter(Purchase.create_time >= start_date)
    if end_date:
        if len(end_date) == 10:
            end_date = end_date + ' 23:59:59'
        results = results.filter(Purchase.create_time <= end_date)
    
    if search:
        search_term = f"%{search}%"
        results = results.filter(
            (Purchase.purchase_no.like(search_term)) | 
            (Purchase.sku.like(search_term)) |
            (Purchase.product_name.like(search_term)) |
            (Purchase.supplier_company.like(search_term)) |
            (Purchase.logistics_no.like(search_term))
        )
    
    results = results.group_by(group_by).order_by(group_by).all()
    
    # 格式化数据
    data = []
    for row in results:
        purchase_amount = float(row.purchase_amount or 0)
        logistics_fee = float(row.logistics_fee or 0)
        total_cost = float(row.total_cost or 0)
        quantity = float(row.quantity or 0)
        purchase_count = row.purchase_count or 0
        
        data.append({
            'date': str(row.date),
            'purchase_amount': purchase_amount,
            'logistics_fee': logistics_fee,
            'total_cost': total_cost,
            'quantity': quantity,
            'purchase_count': purchase_count,
            'avg_price': purchase_amount / quantity if quantity > 0 else 0
        })
    
    return jsonify({
        'code': 200,
        'data': {
            'period': period,
            'items': data
        }
    }), 200


@api.route('/statistics/orders', methods=['GET'])
@require_auth
def get_order_statistics():
    period = request.args.get('period', 'month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')
    
    query = Order.query.filter_by(tenant_id=g.tenant_id)
    
    # 按时间维度分组
    if period == 'day':
        date_format = func.date(Order.order_time)
        group_by = date_format
    elif period == 'week':
        date_format = func.concat(
            func.year(Order.order_time), 
            '-W', 
            func.lpad(func.week(Order.order_time), 2, '0')
        )
        group_by = func.yearweek(Order.order_time)
    elif period == 'month':
        date_format = func.date_format(Order.order_time, '%Y-%m')
        group_by = func.date_format(Order.order_time, '%Y-%m')
    elif period == 'quarter':
        date_format = func.concat(
            func.year(Order.order_time),
            '-Q',
            func.quarter(Order.order_time)
        )
        group_by = func.concat(
            func.year(Order.order_time),
            func.quarter(Order.order_time)
        )
    else:  # year
        date_format = func.year(Order.order_time)
        group_by = func.year(Order.order_time)
    
    # 聚合查询
    results = db.session.query(
        date_format.label('date'),
        func.sum(Order.order_amount).label('order_amount'),
        func.sum(Order.quantity).label('quantity'),
        func.count(Order.id).label('order_count')
    ).filter(
        Order.tenant_id == g.tenant_id
    )
    
    if start_date:
        results = results.filter(Order.order_time >= start_date)
    if end_date:
        if len(end_date) == 10:
            end_date = end_date + ' 23:59:59'
        results = results.filter(Order.order_time <= end_date)
    
    if search:
        search_term = f"%{search}%"
        results = results.filter(
            (Order.platform_order_no.like(search_term)) | 
            (Order.buyer_name.like(search_term)) |
            (Order.sku.like(search_term)) |
            (Order.product_name.like(search_term)) |
            (Order.company_name.like(search_term)) |
            (Order.buyer_email.like(search_term))
        )
    
    results = results.group_by(group_by).order_by(group_by).all()
    
    # 格式化数据
    data = []
    for row in results:
        order_amount = float(row.order_amount or 0)
        quantity = float(row.quantity or 0)
        order_count = row.order_count or 0
        
        data.append({
            'date': str(row.date),
            'order_amount': order_amount,
            'quantity': quantity,
            'order_count': order_count,
            'avg_order_amount': order_amount / order_count if order_count > 0 else 0
        })
    
    return jsonify({
        'code': 200,
        'data': {
            'period': period,
            'items': data
        }
    }), 200


@api.route('/statistics/logistics', methods=['GET'])
@require_auth
def get_logistics_statistics():
    """物流统计"""
    period = request.args.get('period', 'month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')
    
    # 按时间维度分组
    if period == 'day':
        date_format = func.date(Logistics.sent_date)
        group_by = date_format
    elif period == 'week':
        date_format = func.concat(
            func.year(Logistics.sent_date), 
            '-W', 
            func.lpad(func.week(Logistics.sent_date), 2, '0')
        )
        group_by = func.yearweek(Logistics.sent_date)
    elif period == 'month':
        date_format = func.date_format(Logistics.sent_date, '%Y-%m')
        group_by = func.date_format(Logistics.sent_date, '%Y-%m')
    elif period == 'quarter':
        date_format = func.concat(
            func.year(Logistics.sent_date),
            '-Q',
            func.quarter(Logistics.sent_date)
        )
        group_by = func.concat(
            func.year(Logistics.sent_date),
            func.quarter(Logistics.sent_date)
        )
    else:  # year
        date_format = func.year(Logistics.sent_date)
        group_by = func.year(Logistics.sent_date)
    
    # 聚合查询
    results = db.session.query(
        date_format.label('date'),
        func.sum(Logistics.shipping_fee).label('shipping_fee'),
        func.count(Logistics.id).label('shipment_count')
    ).filter(
        Logistics.tenant_id == g.tenant_id
    )
    
    if start_date:
        results = results.filter(Logistics.sent_date >= start_date)
    if end_date:
        if len(end_date) == 10:
            end_date_val = end_date + ' 23:59:59'
        else:
            end_date_val = end_date
        results = results.filter(Logistics.sent_date <= end_date_val)
    
    if search:
        search_term = f"%{search}%"
        results = results.filter(
            (Logistics.tracking_no.like(search_term)) | 
            (Logistics.ref_no.like(search_term)) |
            (Logistics.customer_order_no.like(search_term)) |
            (Logistics.ordering_account.like(search_term))
        )
    
    results = results.group_by(group_by).order_by(group_by).all()
    
    # 格式化数据
    data = []
    for row in results:
        shipping_fee = float(row.shipping_fee or 0)
        shipment_count = row.shipment_count or 0
        
        data.append({
            'date': str(row.date),
            'shipping_fee': shipping_fee,
            'shipment_count': shipment_count,
            'avg_shipping_fee': shipping_fee / shipment_count if shipment_count > 0 else 0
        })
    
    return jsonify({
        'code': 200,
        'data': {
            'period': period,
            'items': data
        }
    }), 200


@api.route('/statistics/profit', methods=['GET'])
@require_auth
def get_profit_statistics():
    """综合盈亏分析"""
    period = request.args.get('period', 'month')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search')
    
    # 获取各模块统计数据
    # 这里简化处理,实际应该调用上面的函数或复用查询逻辑
    
    # 采购数据
    purchase_query = _get_period_query(Purchase, Purchase.create_time, period, start_date, end_date, g.tenant_id, search)
    purchase_results = purchase_query.with_entities(
        _get_date_format(Purchase.create_time, period).label('date'),
        func.sum(Purchase.actual_payment + func.coalesce(Purchase.shipping_fee, 0)).label('purchase_cost')
    ).group_by(_get_group_by(Purchase.create_time, period)).all()
    
    # 订单数据
    order_query = _get_period_query(Order, Order.order_time, period, start_date, end_date, g.tenant_id, search)
    order_results = order_query.with_entities(
        _get_date_format(Order.order_time, period).label('date'),
        func.sum(Order.order_amount).label('revenue'),
        func.count(Order.id).label('order_count')
    ).group_by(_get_group_by(Order.order_time, period)).all()
    
    # 物流数据
    logistics_query = _get_period_query(Logistics, Logistics.sent_date, period, start_date, end_date, g.tenant_id, search)
    logistics_results = logistics_query.with_entities(
        _get_date_format(Logistics.sent_date, period).label('date'),
        func.sum(Logistics.shipping_fee).label('logistics_cost')
    ).group_by(_get_group_by(Logistics.sent_date, period)).all()
    
    # 合并数据
    data_dict = {}
    
    for row in purchase_results:
        date = str(row.date)
        data_dict[date] = {
            'date': date,
            'purchase_cost': float(row.purchase_cost or 0),
            'revenue': 0,
            'logistics_cost': 0,
            'order_count': 0
        }
    
    for row in order_results:
        date = str(row.date)
        if date not in data_dict:
            data_dict[date] = {'date': date, 'purchase_cost': 0, 'logistics_cost': 0}
        data_dict[date]['revenue'] = float(row.revenue or 0)
        data_dict[date]['order_count'] = row.order_count or 0
    
    for row in logistics_results:
        date = str(row.date)
        if date not in data_dict:
            data_dict[date] = {'date': date, 'purchase_cost': 0, 'revenue': 0, 'order_count': 0}
        data_dict[date]['logistics_cost'] = float(row.logistics_cost or 0)
    
    # 计算利润
    data = []
    total_revenue = 0
    total_cost = 0
    
    for date in sorted(data_dict.keys()):
        item = data_dict[date]
        revenue = item['revenue']
        cost = item['purchase_cost'] + item['logistics_cost']
        profit = revenue - cost
        profit_rate = (profit / revenue * 100) if revenue > 0 else 0
        
        total_revenue += revenue
        total_cost += cost
        
        data.append({
            'date': date,
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
            'profit_rate': round(profit_rate, 2),
            'order_count': item['order_count']
        })
    
    total_profit = total_revenue - total_cost
    avg_profit_rate = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return jsonify({
        'code': 200,
        'data': {
            'period': period,
            'items': data,
            'summary': {
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'avg_profit_rate': round(avg_profit_rate, 2)
            }
        }
    }), 200


def _get_date_format(time_field, period):
    """获取日期格式化表达式"""
    if period == 'day':
        return func.date(time_field)
    elif period == 'week':
        return func.concat(func.year(time_field), '-W', func.lpad(func.week(time_field), 2, '0'))
    elif period == 'month':
        return func.date_format(time_field, '%Y-%m')
    elif period == 'quarter':
        return func.concat(func.year(time_field), '-Q', func.quarter(time_field))
    else:
        return func.year(time_field)


def _get_group_by(time_field, period):
    """获取分组表达式"""
    if period == 'day':
        return func.date(time_field)
    elif period == 'week':
        return func.yearweek(time_field)
    elif period == 'month':
        return func.date_format(time_field, '%Y-%m')
    elif period == 'quarter':
        return func.concat(func.year(time_field), func.quarter(time_field))
    else:
        return func.year(time_field)


def _get_period_query(model, time_field, period, start_date, end_date, tenant_id, search=None):
    """获取时间段查询"""
    query = model.query.filter_by(tenant_id=tenant_id)
    if start_date:
        query = query.filter(time_field >= start_date)
    if end_date:
        if len(end_date) == 10:
            end_date = end_date + ' 23:59:59'
        query = query.filter(time_field <= end_date) # 修复了这里之前可能的 Order.created_at 错误
    
    if search:
        search_term = f"%{search}%"
        if model == Purchase:
            query = query.filter(
                (Purchase.purchase_no.like(search_term)) | 
                (Purchase.sku.like(search_term)) |
                (Purchase.product_name.like(search_term)) |
                (Purchase.supplier_company.like(search_term)) |
                (Purchase.logistics_no.like(search_term))
            )
        elif model == Order:
            query = query.filter(
                (Order.platform_order_no.like(search_term)) | 
                (Order.buyer_name.like(search_term)) |
                (Order.sku.like(search_term)) |
                (Order.product_name.like(search_term)) |
                (Order.company_name.like(search_term)) |
                (Order.buyer_email.like(search_term))
            )
        elif model == Logistics:
            query = query.filter(
                (Logistics.tracking_no.like(search_term)) | 
                (Logistics.ref_no.like(search_term)) |
                (Logistics.customer_order_no.like(search_term)) |
                (Logistics.ordering_account.like(search_term))
            )
            
    return query
