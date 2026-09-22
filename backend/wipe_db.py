import asyncio
from sqlalchemy import text
from app.db.session import engine

async def wipe():
    print("🧹 Wiping old dummy data...")
    async with engine.begin() as conn:
        try:
            # Cascade ensures all related records are deleted
            await conn.execute(text('TRUNCATE sellers, products, orders, inventory_snapshots, pricing_snapshots, traffic_metrics, logistics_metrics, product_embeddings, insight_embeddings CASCADE'))
            print("🔥 Database Wiped! Ready for Brew Boulevard fresh start.")
        except Exception as e:
            print(f"❌ Error wiping database: {e}")

if __name__ == "__main__":
    asyncio.run(wipe())
