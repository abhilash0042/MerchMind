import psycopg2
import pandas as pd
from app.services.ingestion import _safe_float

conn = psycopg2.connect(
    host="aws-1-ap-south-1.pooler.supabase.com",
    port=5432,
    dbname="postgres",
    user="postgres.gwwhksdelequvapksgqx",
    password="Abhilash@142",
    sslmode="require"
)
conn.autocommit = True
cur = conn.cursor()

df = pd.read_excel('test_dataset.xlsx', sheet_name='Orders')

# Drop the ON CONFLICT so we can focus purely on INSERT data type validation
insert_query = """
    INSERT INTO orders (
        order_id, external_order_id, seller_id, product_id, marketplace, 
        order_status, quantity, selling_price, discount, tax, shipping_fee, 
        order_date, delivery_date, return_flag, cancellation_reason, 
        customer_name, customer_email, payment_mode, snapshot_date
    ) VALUES (
        gen_random_uuid(), %s, 'c592fd56-c939-4448-92ef-930dea943e1d', NULL, %s, 
        %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, 
        NULL, NULL, NULL, '2026-06-06'
    )
"""

for idx, row in df.iterrows():
    try:
        cur.execute(insert_query, (
            str(row.get("order_id")),
            str(row.get("marketplace")),
            str(row.get("order_status")),
            int(row.get("quantity")) if not pd.isna(row.get("quantity")) else 1,
            _safe_float(row.get("selling_price")),
            _safe_float(row.get("discount")),
            _safe_float(row.get("tax")),
            _safe_float(row.get("shipping_fee")),
            str(row.get("order_date"))[:10],
            None,
            False,
            None
        ))
    except Exception as e:
        print(f"Row {idx} failed: {e}")
        break

cur.close()
conn.close()
