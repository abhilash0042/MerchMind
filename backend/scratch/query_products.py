"""Get all distinct SKUs from the products table."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

async def main():
    from app.db.session import get_db
    async for db in get_db():
        r = await db.execute(text("SELECT sku, product_name FROM products ORDER BY sku"))
        rows = r.fetchall()
        print(f"Total products: {len(rows)}")
        for row in rows:
            print(f"  {row[0]} - {row[1]}")

asyncio.run(main())
