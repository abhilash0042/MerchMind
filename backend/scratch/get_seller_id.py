import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def get_seller():
    try:
        async with AsyncSessionLocal() as db:
            res = await db.execute(text('SELECT seller_id FROM sellers LIMIT 1'))
            row = res.scalar()
            if row:
                print(f"FOUND_SELLER_ID:{row}")
            else:
                print("NO_SELLER_FOUND")
    except Exception as e:
        print(f"DB_ERROR:{e}")

if __name__ == "__main__":
    asyncio.run(get_seller())
