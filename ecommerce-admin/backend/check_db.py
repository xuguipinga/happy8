
import os
import sys
from app import create_app, db
from app.models.order import Order
from app.models.user import User
from app.models.tenant import Tenant
from sqlalchemy import func

app = create_app()
with app.app_context():
    print("--- Database Diagnosis ---")
    
    # 1. Total records in biz_orders
    total_count = Order.query.count()
    print(f"Total orders in biz_orders: {total_count}")
    
    # 2. Distribution of tenant_id in biz_orders
    tenant_dist = db.session.query(Order.tenant_id, func.count(Order.id)).group_by(Order.tenant_id).all()
    print(f"Order distribution by tenant_id: {tenant_dist}")
    
    # 3. Tenants in sys_tenants
    tenants = Tenant.query.all()
    print(f"Tenants in sys_tenants: {[(t.id, t.name, t.code) for t in tenants]}")
    
    # 4. Users and their tenant_id
    users = User.query.all()
    print(f"Users: {[(u.id, u.username, u.tenant_id) for u in users]}")
    
    # 5. Distribution of order_status
    status_dist = db.session.query(Order.order_status, func.count(Order.id)).group_by(Order.order_status).all()
    print(f"Order distribution by order_status: {status_dist}")
    
    # 6. Check order_time range for today
    from datetime import date, time, datetime
    today = date.today()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)
    today_count = Order.query.filter(Order.order_time >= start_of_day, Order.order_time <= end_of_day).count()
    print(f"Orders with order_time today ({today}): {today_count}")
    
    # 6. Sample order order_time format
    sample = Order.query.first()
    if sample:
        print(f"Sample order time: {sample.order_time} (Type: {type(sample.order_time)})")
    
    print("--- End of Diagnosis ---")
