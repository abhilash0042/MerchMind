import asyncio
from app.db.session import engine
from sqlalchemy import text

async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT product_id, COUNT(*) FROM orders GROUP BY product_id"))
        print(res.all())

asyncio.run(run())
