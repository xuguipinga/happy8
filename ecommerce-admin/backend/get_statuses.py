import sys
import os

# Add the project root to sys.path to import app
sys.path.append(os.getcwd())

from app import create_app
from app.models.order import Order
from app.extensions import db

app = create_app()
with app.app_context():
    statuses = [s[0] for s in db.session.query(Order.order_status).distinct().all()]
    print("Unique Statuses in Database:")
    for s in statuses:
        print(f"'{s}'")
