import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())

from app import create_app, db

def add_column_if_not_exists(connection, table_name, column_name, column_type):
    try:
        connection.execute(text(f"SELECT {column_name} FROM {table_name} LIMIT 1"))
        print(f"Column {column_name} already exists in {table_name}.")
    except Exception:
        print(f"Adding column {column_name} to {table_name}...")
        try:
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            print(f"Successfully added {column_name}.")
        except Exception as e:
            print(f"Failed to add {column_name}: {e}")

def migrate():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as connection:
            # Logistics
            add_column_if_not_exists(connection, 'biz_logistics', 'ordering_account', 'VARCHAR(100)')

            # Purchase
            add_column_if_not_exists(connection, 'biz_purchases', 'shipper_name', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'zip_code', 'VARCHAR(20)')
            add_column_if_not_exists(connection, 'biz_purchases', 'product_no', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'offer_id', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'category', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'agent_name', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'agent_contact', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'dropship_provider_id', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'micro_order_no', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'downstream_channel', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'order_company_entity', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'initiator_login_name', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'is_auto_pay', 'VARCHAR(100)')

            print("Migration v2 completed.")

if __name__ == "__main__":
    migrate()
