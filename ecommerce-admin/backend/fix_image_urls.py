import os
from app import create_app, db
from app.models.stock import Inventory

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def fix_urls():
    with app.app_context():
        items = Inventory.query.filter(Inventory.image_url.like('/uploads/%')).all()
        print(f"Found {len(items)} items to fix.")
        for item in items:
            item.image_url = f"/api{item.image_url}"
        db.session.commit()
        print("Done.")

if __name__ == '__main__':
    fix_urls()
