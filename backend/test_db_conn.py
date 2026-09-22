import asyncio
import sys
from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings

async def test_conn():
    print(f"Database settings loaded:")
    if settings.DATABASE_URL:
        print(f" - DATABASE_URL is configured.")
    else:
        print(f" - Host: {settings.POSTGRES_HOST}")
        print(f" - Port: {settings.POSTGRES_PORT}")
        print(f" - DB: {settings.POSTGRES_DB}")
        print(f" - User: {settings.POSTGRES_USER}")
    
    print(f"Connecting to: {settings.async_db_url.split('@')[-1]} ...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            row = result.fetchone()
            print("SUCCESS: Connection successful!")
            print(f"PostgreSQL Version: {row[0] if row else 'Unknown'}")
            
            # Check pgvector extension
            vector_check = await conn.execute(text("SELECT extname FROM pg_catalog.pg_extension WHERE extname = 'vector';"))
            vector_row = vector_check.fetchone()
            if vector_row:
                print("SUCCESS: pgvector extension is ENABLED in the database.")
            else:
                print("WARNING: pgvector extension is NOT enabled. Startup will attempt to create it if credentials allow.")
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure app directory is in path
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    asyncio.run(test_conn())
