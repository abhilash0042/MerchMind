import psycopg2

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

try:
    cur.execute("""
    INSERT INTO orders (
        order_id, external_order_id, seller_id, product_id, marketplace, 
        order_status, quantity, selling_price, discount, tax, shipping_fee, 
        order_date, delivery_date, return_flag, cancellation_reason, 
        customer_name, customer_email, payment_mode, snapshot_date
    ) VALUES (
        '821ee9ae-b9e8-437b-811d-52e81b0f6838', 'ORD-00001', 'c592fd56-c939-4448-92ef-930dea943e1d', 'caecda60-887b-44f2-8a04-127d875c008e', 
        'Shopify', 'delivered', 2, 84.88, 5.0, 13.12, 0.0, 
        '2026-04-27', NULL, False, NULL, NULL, NULL, NULL, '2026-06-06'
    ) ON CONFLICT (external_order_id) DO UPDATE SET order_status = excluded.order_status, delivery_date = excluded.delivery_date
    """)
    print("SUCCESS!")
except Exception as e:
    print("ERROR:", e)

cur.close()
conn.close()
