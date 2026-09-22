import asyncio
from app.db.session import engine
from sqlalchemy import text

async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT product_id, product_name, sku FROM products LIMIT 10"))
        print(res.all())

asyncio.run(run())
