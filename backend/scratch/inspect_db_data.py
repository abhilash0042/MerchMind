import asyncio
import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main():
    from app.db.session import get_db
    
    tables = [
        "sellers",
        "products",
        "orders",
        "inventory_snapshots",
        "pricing_snapshots",
        "traffic_metrics",
        "logistics_metrics"
    ]
    
    async for db in get_db():
        # Check sellers
        print("=== Sellers ===")
        res = await db.execute(text("SELECT * FROM sellers"))
        sellers = res.fetchall()
        for s in sellers:
            print(f"  Seller: {s}")
            
        for table in tables:
            try:
                # Get count
                res_count = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res_count.scalar()
                print(f"\nTable '{table}': {count} rows")
                
                if count > 0:
                    # Check date column if exists
                    try:
                        res_cols = await db.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}'"))
                        cols = [r[0] for r in res_cols.fetchall()]
                        date_cols = [c for c in cols if 'date' in c or 'time' in c]
                        
                        if date_cols:
                            for dc in date_cols:
                                res_dates = await db.execute(text(f"SELECT MIN({dc}), MAX({dc}) FROM {table}"))
                                min_d, max_d = res_dates.fetchone()
                                print(f"  - Date field '{dc}': min={min_d}, max={max_d}")
                        
                        # Show first row
                        res_row = await db.execute(text(f"SELECT * FROM {table} LIMIT 1"))
                        row = res_row.fetchone()
                        print(f"  - First row sample: {row}")
                    except Exception as ex:
                        print(f"  - Error getting details for {table}: {ex}")
            except Exception as e:
                print(f"Error reading table '{table}': {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
