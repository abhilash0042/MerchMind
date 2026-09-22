import asyncio
from app.db.session import engine
from sqlalchemy import text

async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM pricing_snapshots WHERE product_id='03729f82-3baa-400a-bfd3-5c23137ed5bd'"))
        print(res.mappings().all())

asyncio.run(run())
