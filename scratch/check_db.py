import asyncio
import httpx

async def run():
    async with httpx.AsyncClient() as client:
        res = await client.get('http://localhost:8000/sellers/')
        sellers = res.json()
        if not sellers:
            print("No sellers found!")
            return
        seller_id = sellers[0]['seller_id']
        print(f"Seller ID: {seller_id}")
        
        res = await client.get(f'http://localhost:8000/analytics/dashboard?seller_id={seller_id}&days=3650')
        print("Dashboard (10 years):", res.json())
        
        res = await client.get(f'http://localhost:8000/analytics/orders/stats?seller_id={seller_id}&days=3650')
        print("Orders Stats (10 years):", res.json())
        
        res = await client.get(f'http://localhost:8000/analytics/orders/list?seller_id={seller_id}')
        data = res.json().get('data', [])
        print("Orders count in list:", len(data))
        if data:
            print("Sample order:", data[0])

asyncio.run(run())
