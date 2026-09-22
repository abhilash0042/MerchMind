import asyncio
import asyncpg
import ssl

async def test_ssl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    pw = "Abhilash@142"
    ref = "gwwhksdelequvapksgqx"
    
    for port in [5432, 6543]:
        for host in ["aws-1-ap-south-1.pooler.supabase.com", "aws-0-ap-south-1.pooler.supabase.com"]:
            print(f"Connecting to {host}:{port} with ssl...", flush=True)
            try:
                conn = await asyncpg.connect(
                    host=host,
                    port=port,
                    user=f"postgres.{ref}",
                    password=pw,
                    database="postgres",
                    ssl=ctx,
                    timeout=8.0
                )
                print(f"✅ CONNECTED to {host}:{port}!", flush=True)
                res = await conn.fetchval("SELECT current_database()")
                print("Database:", res, flush=True)
                await conn.close()
                return
            except Exception as e:
                print(f"Failed {host}:{port}: {e}", flush=True)

asyncio.run(test_ssl())
