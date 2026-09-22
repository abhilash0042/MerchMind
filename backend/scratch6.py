import asyncio
from app.db.session import engine
from sqlalchemy import text

async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'orders'"))
        print(res.all())
        res2 = await conn.execute(text("SELECT * FROM orders LIMIT 2"))
        print(res2.mappings().all())

asyncio.run(run())
