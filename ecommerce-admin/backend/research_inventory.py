
import os
import sys
from app import create_app, db
from app.models.stock import Inventory

app = create_app()
with app.app_context():
    print("--- Inventory Model Research ---")
    models = Inventory.query.with_entities(Inventory.model).distinct().all()
    for m in models:
        print(f"Model: {m.model}")
    print("--- End of Research ---")
