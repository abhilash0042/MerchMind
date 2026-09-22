import asyncio
import pandas as pd
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.services.ingestion import ingest_orders, _normalise_columns, ORDER_COL_MAP
from datetime import date
import sys

async def main():
    print("Testing manual ingestion...")
    df = pd.read_excel('test_dataset.xlsx', sheet_name='Orders')
    
    seller_id = "c592fd56-c939-4448-92ef-930dea943e1d"
    snap_date = date.today()
    
    async with AsyncSessionLocal() as db:
        print("Starting ingest_orders...")
        try:
            res = await ingest_orders(db, df, seller_id, snap_date)
            print(res)
        except Exception as e:
            print("ERROR", str(e))
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
