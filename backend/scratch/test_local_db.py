import asyncio
import asyncpg

async def test_local():
    for pw in ["postgres", "root", "admin", "123456", "1234", "Abhilash"]:
        try:
            conn = await asyncpg.connect(host="127.0.0.1", port=5432, user="postgres", password=pw, database="postgres", timeout=2.0)
            print(f"✅ CONNECTED with pw={pw}!", flush=True)
            res = await conn.fetchval("SELECT current_database()")
            print(f"Database: {res}", flush=True)
            tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            print("Tables:", [t['table_name'] for t in tables], flush=True)
            await conn.close()
            return
        except Exception as e:
            print(f"pw={pw} -> {type(e).__name__}: {e}", flush=True)

asyncio.run(test_local())
