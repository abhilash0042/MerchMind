import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [r[0] for r in res.fetchall()]
        print("Existing tables:", tables)
        
        if "ai_product_analyses" in tables:
            cnt = await db.execute(text("SELECT COUNT(*) FROM ai_product_analyses"))
            print("ai_product_analyses row count:", cnt.scalar())
        else:
            print("ai_product_analyses table does not exist!")

asyncio.run(check())
