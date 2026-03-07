
import os
import sys
from app import create_app, db
from app.models.order import Order

app = create_app()
with app.app_context():
    print("--- SKU Pattern Research ---")
    orders = Order.query.with_entities(Order.sku).distinct().limit(50).all()
    for o in orders:
        if o.sku:
            print(f"SKU: {o.sku}")
    print("--- End of Research ---")
