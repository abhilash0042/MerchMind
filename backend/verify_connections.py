import asyncio
import os
import httpx
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("--- 🩺 CommercePulse System Diagnostics ---")
    
    # 1. Test PostgreSQL/Supabase
    print(f"\n[1] Testing Database Connection ({settings.async_db_url.split('@')[-1] if '@' in settings.async_db_url else 'DB'})")
    try:
        engine = create_async_engine(settings.async_db_url, echo=False)
        async with engine.connect() as conn:
            from sqlalchemy import text
            res = await conn.execute(text("SELECT current_database(), current_date"))
            row = res.fetchone()
            print(f"✅ DB Success! Connected to: {row[0]} on {row[1]}")
    except Exception as e:
        print(f"❌ DB Failed: {e}")

    # 2. Test Redis
    print(f"\n[2] Testing Redis Connection ({settings.REDIS_URL})")
    try:
        r = redis.from_url(settings.REDIS_URL)
        pong = await r.ping()
        if pong:
            print("✅ Redis Success! Received PONG.")
        else:
            print("⚠️ Redis connected but no PONG received.")
        await r.aclose()
    except Exception as e:
        print(f"❌ Redis Failed: {e}")

    # 3. Test Groq API Key
    print("\n[3] Checking GROQ_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"✅ Groq API Key configured (starts with: {groq_key[:8]}...)")
    else:
        print("❌ Groq API Key NOT configured in environment.")

    # 4. Test AI Agents API
    ai_url = settings.AI_AGENTS_URL
    print(f"\n[4] Testing AI Agents API Connection ({ai_url}/health)")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{ai_url}/docs") # AI Agents doesn't have /health yet, use /docs
            if resp.status_code == 200:
                print("✅ AI Agents API Success! Accessible.")
            else:
                print(f"⚠️ AI Agents API returned status: {resp.status_code}")
    except httpx.ConnectError:
        print(f"❌ AI Agents API Failed: Connection Refused (port 8001).")
    except Exception as e:
        print(f"❌ AI Agents API Failed: {e}")

    # 5. Test Main Ingestion API Health
    main_url = "http://localhost:8000"
    print(f"\n[5] Testing Main Ingestion API Health ({main_url}/health)")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{main_url}/health")
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Main API Success! Status: {data.get('status')}, Celery: {data.get('celery')}")
            else:
                print(f"⚠️ Main API returned status: {resp.status_code}")
    except httpx.ConnectError:
        print(f"❌ Main API Failed: Connection Refused (port 8000).")
    except Exception as e:
        print(f"❌ Main API Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
