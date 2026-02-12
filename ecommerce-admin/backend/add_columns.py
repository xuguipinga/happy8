import sys
import os
from sqlalchemy import text

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app import create_app, db

def add_column_if_not_exists(connection, table_name, column_name, column_type):
    # This is a simplified check. For production, use better schema inspection.
    try:
        # Try to select the column. If it fails, it doesn't exist.
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
            # Wrap in transaction if needed, but some DBs don't support DDL in transaction
            # SQLite does, MySQL mostly implicit commit.
            
            # Logistics
            add_column_if_not_exists(connection, 'biz_logistics', 'service_type', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_logistics', 'warehouse', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_logistics', 'inbound_time', 'DATETIME')
            add_column_if_not_exists(connection, 'biz_logistics', 'outbound_time', 'DATETIME')
            add_column_if_not_exists(connection, 'biz_logistics', 'payment_time', 'DATETIME')
            add_column_if_not_exists(connection, 'biz_logistics', 'customer_order_no', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_logistics', 'sender_name', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_logistics', 'sender_email', 'VARCHAR(150)')

            # Purchase
            add_column_if_not_exists(connection, 'biz_purchases', 'receiver_name', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'receiver_phone', 'VARCHAR(50)')
            add_column_if_not_exists(connection, 'biz_purchases', 'receiver_mobile', 'VARCHAR(50)')
            add_column_if_not_exists(connection, 'biz_purchases', 'unit', 'VARCHAR(20)')
            add_column_if_not_exists(connection, 'biz_purchases', 'model', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'material_no', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'buyer_note', 'TEXT')
            add_column_if_not_exists(connection, 'biz_purchases', 'invoice_title', 'VARCHAR(200)')
            add_column_if_not_exists(connection, 'biz_purchases', 'tax_id', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'invoice_address_phone', 'VARCHAR(255)')
            add_column_if_not_exists(connection, 'biz_purchases', 'invoice_bank_account', 'VARCHAR(255)')
            add_column_if_not_exists(connection, 'biz_purchases', 'invoice_receiver_address', 'TEXT')
            add_column_if_not_exists(connection, 'biz_purchases', 'is_dropship', 'BOOLEAN')
            add_column_if_not_exists(connection, 'biz_purchases', 'upstream_order_no', 'VARCHAR(100)')
            add_column_if_not_exists(connection, 'biz_purchases', 'order_batch_no', 'VARCHAR(100)')

            # Order
            add_column_if_not_exists(connection, 'biz_orders', 'initial_payment', 'DECIMAL(12, 4)')
            add_column_if_not_exists(connection, 'biz_orders', 'balance_payment', 'DECIMAL(12, 4)')
            add_column_if_not_exists(connection, 'biz_orders', 'appointed_delivery_time', 'DATETIME')

            print("Migration completed.")

if __name__ == "__main__":
    migrate()
