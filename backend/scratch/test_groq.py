import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv("c:\\projects\\commercepulse\\AZURE\\backend\\.env")
groq_api_key = os.getenv("GROQ_API_KEY")
print("API Key exists:", bool(groq_api_key))

async def test_chat():
    messages = [{"role": "user", "content": "Hello!"}]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=10.0
        )
        print("Status:", response.status_code)
        try:
            print(response.json())
        except Exception as e:
            print(response.text)

asyncio.run(test_chat())
