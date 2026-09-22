"""Verify final product state."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text

async def main():
    from app.db.session import get_db
    async for db in get_db():
        r = await db.execute(text("SELECT COUNT(*) FROM products"))
        print(f"Total products: {r.scalar()}")
        
        r = await db.execute(text("SELECT sku, product_name, category FROM products ORDER BY sku"))
        rows = r.fetchall()
        for row in rows:
            print(f"  {row[0]:12s} | {row[1]:45s} | {row[2]}")

        # Check for remaining SKU-* data in other tables
        for table in ["orders", "inventory_snapshots", "pricing_snapshots", "traffic_metrics", "logistics_metrics"]:
            try:
                r2 = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                cnt = r2.scalar()
                print(f"  {table}: {cnt} rows")
            except:
                pass

asyncio.run(main())
