import asyncio
from sqlalchemy import text
from app.db.session import engine, Base

async def init_db():
    print("Initializing CommercePulse Database...")
    
    # ── Step 1: Check pgvector availability in the DB ──
    pgvector_ok = False
    async with engine.connect() as conn:
        try:
            result = await conn.execute(
                text("SELECT 1 FROM pg_available_extensions WHERE name='vector'")
            )
            row = result.fetchone()
            if row:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await conn.commit()
                pgvector_ok = True
                print("pgvector extension ready.")
            else:
                print("[SKIP] pgvector extension not installed in this postgres — skipping embedding tables.")
        except Exception as e:
            print(f"[SKIP] pgvector check failed: {e}")

    # ── Step 2: Remove embedding tables from metadata if pgvector missing ──
    from app.models.models import (
        Seller, Product, Order, InventorySnapshot, PricingSnapshot,
        TrafficMetric, LogisticsMetric, ProductEmbedding, InsightEmbedding, AIProductAnalysis
    )
    
    skip_tables = set()
    if not pgvector_ok:
        skip_tables = {"product_embeddings", "insight_embeddings"}
        print(f"  Skipping tables: {skip_tables}")

    # Create tables, skipping embedding tables if needed
    async with engine.begin() as conn:
        print("Creating tables...")
        try:
            tables_to_create = [
                t for t in Base.metadata.sorted_tables
                if t.name not in skip_tables
            ]
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn,
                    tables=tables_to_create,
                    checkfirst=True
                )
            )
            print(f"Tables created successfully: {[t.name for t in tables_to_create]}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to create tables: {e}")
            return

    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    asyncio.run(init_db())
