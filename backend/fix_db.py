
import asyncio
from sqlalchemy import text
from app.db.session import engine

async def fix_schema():
    print("🔍 Checking and fixing database schema...")
    async with engine.begin() as conn:
        # 1. Fix traffic_metrics
        print("   - Updating traffic_metrics...")
        await conn.execute(text("ALTER TABLE traffic_metrics ADD COLUMN IF NOT EXISTS sessions INTEGER DEFAULT 0"))
        await conn.execute(text("ALTER TABLE traffic_metrics ADD COLUMN IF NOT EXISTS page_views INTEGER DEFAULT 0"))
        
        # 2. Fix pricing_snapshots
        print("   - Updating pricing_snapshots...")
        await conn.execute(text("ALTER TABLE pricing_snapshots ADD COLUMN IF NOT EXISTS mrp NUMERIC(12, 2)"))
        
        # 3. Fix logistics_metrics
        print("   - Updating logistics_metrics...")
        await conn.execute(text("ALTER TABLE logistics_metrics ADD COLUMN IF NOT EXISTS expected_delivery DATE"))
        await conn.execute(text("ALTER TABLE logistics_metrics ADD COLUMN IF NOT EXISTS warehouse_id TEXT"))
        
    print("✅ Database schema updated successfully!")

if __name__ == "__main__":
    asyncio.run(fix_schema())
