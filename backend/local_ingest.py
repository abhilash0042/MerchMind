import asyncio
import io
import os
import sys
import pandas as pd
from datetime import date

# Add backend dir to sys.path so app modules load correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.models import Seller
from app.services import ingestion

async def main():
    print("Connecting to Database...")
    async with AsyncSessionLocal() as db:
        # Get or create Brew Boulevard
        result = await db.execute(select(Seller).where(Seller.seller_name == "Brew Boulevard"))
        seller = result.scalar_one_or_none()
        if not seller:
            print("Creating Seller 'Brew Boulevard'...")
            seller = Seller(seller_name="Brew Boulevard", marketplace="multi", region="IN", email="hello@brewboulevard.in")
            db.add(seller)
            await db.commit()
            await db.refresh(seller)
        
        seller_id = str(seller.seller_id)
        print(f"Using Seller ID: {seller_id}")
        
        file_path = "test_dataset.xlsx"
        print(f"Reading {file_path}...")
        
        xl = pd.ExcelFile(file_path, engine="openpyxl")
        sheet_names_lower = {s.strip().lower(): s for s in xl.sheet_names}
        
        DOMAIN_MAP = {
            "orders":    ingestion.ingest_orders,
            "inventory": ingestion.ingest_inventory,
            "pricing":   ingestion.ingest_pricing,
            "traffic":   ingestion.ingest_traffic,
            "logistics": ingestion.ingest_logistics,
        }
        
        snap_date = date.today()
        
        for domain, fn in DOMAIN_MAP.items():
            if domain in sheet_names_lower:
                print(f"Processing sheet: {sheet_names_lower[domain]}...")
                sheet_df = xl.parse(sheet_names_lower[domain])
                res = await fn(db, sheet_df, seller_id, snap_date)
                print(f"Result for {domain}: {res}")
                
        print("Dataset ingested into Supabase successfully.")
        
        # Optionally trigger embeddings
        try:
            from app.services.tasks import _run_embed
            print("Running embeddings locally... (this might take a minute)")
            await _run_embed(seller_id, str(snap_date))
            print("Embeddings completed.")
        except Exception as e:
            print(f"Embeddings error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
