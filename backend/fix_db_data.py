import asyncio
from app.db.session import engine
from sqlalchemy import text
from datetime import date, timedelta
import random

async def fix_data():
    async with engine.begin() as conn:
        seller_id = 'c592fd56-c939-4448-92ef-930dea943e1d'
        product_id = '03729f82-3baa-400a-bfd3-5c23137ed5bd'
        
        # 1. Update 50 random orders that have product_id=None to belong to this product
        await conn.execute(text("""
            UPDATE orders 
            SET product_id = CAST(:product_id AS UUID), marketplace = 'Flipkart', selling_price = 312.21
            WHERE order_id IN (
                SELECT order_id FROM orders WHERE product_id IS NULL LIMIT 50
            )
        """), {"product_id": product_id})

        # 2. Update traffic_metrics for this product to have ad_spend
        await conn.execute(text("""
            UPDATE traffic_metrics
            SET ad_spend = round((random() * 50 + 10)::numeric, 2),
                revenue_from_ads = round((random() * 200 + 50)::numeric, 2)
            WHERE product_id = CAST(:product_id AS UUID)
        """), {"product_id": product_id})

        # 3. Add some logistic metrics linked to the updated orders
        await conn.execute(text("""
            INSERT INTO logistics_metrics (
                seller_id, marketplace, courier_name, tracking_id,
                order_id, fulfillment_type, dispatch_date, expected_delivery, actual_delivery, delivery_status,
                rto_flag, snapshot_date
            )
            SELECT 
                seller_id, marketplace, 'BlueDart', 'TRK-' || left(order_id::text, 8),
                order_id, 'FBA', order_date, order_date + interval '3 days', order_date + interval '2 days', 'delivered',
                false, CURRENT_DATE
            FROM orders
            WHERE product_id = CAST(:product_id AS UUID)
            ON CONFLICT DO NOTHING
        """), {"product_id": product_id})

asyncio.run(fix_data())
print("Data fixed!")
