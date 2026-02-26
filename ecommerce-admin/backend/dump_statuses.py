import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app import create_app
from app.models.order import Order
from app.extensions import db

app = create_app()
with app.app_context():
    statuses = [s[0] for s in db.session.query(Order.order_status).distinct().all()]
    with open('statuses_dump.txt', 'w', encoding='utf-8') as f:
        for s in sorted(filter(None, statuses)):
            f.write(f"{s}\n")
    print(f"Dumped {len(statuses)} unique statuses to statuses_dump.txt")
