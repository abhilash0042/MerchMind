import asyncio
from app.db.session import engine
from sqlalchemy import text

async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT count(*) FROM orders WHERE product_id='03729f82-3baa-400a-bfd3-5c23137ed5bd'"))
        print("Orders count:", res.scalar())
        res = await conn.execute(text("SELECT count(*) FROM traffic_metrics WHERE product_id='03729f82-3baa-400a-bfd3-5c23137ed5bd'"))
        print("Traffic count:", res.scalar())

asyncio.run(run())
