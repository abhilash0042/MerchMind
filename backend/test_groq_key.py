import httpx
import asyncio

async def test_groq():
    key = "gsk_Qqdkdvu8D8OC5JPC0gB9WGdyb3FYA8f2sfp4zG1pmPuayypc9BH"
    print(f"Testing key: {key[:8]}...{key[-4:]} (len={len(key)})")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": "Say hello"}],
                "max_tokens": 10,
            },
            timeout=15.0
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text[:300]}")

asyncio.run(test_groq())
