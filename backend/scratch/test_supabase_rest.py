import httpx
import os
from dotenv import load_dotenv

load_dotenv("c:/projects/commercepulse/AZURE/ai_agents/.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"Testing Supabase REST endpoint: {url}...")
try:
    resp = httpx.get(
        f"{url}/rest/v1/",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        timeout=8.0
    )
    print(f"Status: {resp.status_code}")
    print("Headers:", resp.headers)
    print("Body:", resp.text[:300])
except Exception as e:
    print(f"Error: {e}")
