import httpx
import asyncio
import os

# Bug 9 Fix: was hardcoded to HuggingFace Space URL — script never worked against local dev backend.
# Now reads from environment, defaulting to localhost:8010 for local development.
API_URL = os.environ.get("COMMERCEPULSE_API_URL", "http://localhost:8010")
API_KEY = os.environ.get("COMMERCEPULSE_API_KEY", "dev-api-key")
FILE_PATH = os.environ.get("DATASET_PATH", os.path.join(os.path.dirname(__file__), "..", "sample_data", "brew_boulevard_demo.xlsx"))

async def main():
    headers = {"X-API-Key": API_KEY}
    
    async with httpx.AsyncClient() as client:
        # 1. Get Sellers
        resp = await client.get(f"{API_URL}/sellers/", headers=headers)
        
        if resp.status_code != 200:
            print("Failed to get sellers. Status:", resp.status_code, resp.text)
            return

        sellers = resp.json()
        seller_id = None
        
        if isinstance(sellers, list):
            for s in sellers:
                if s.get("seller_name") == "Brew Boulevard":
                    seller_id = s.get("seller_id")
                    break
        else:
            print("Unexpected response format:", sellers)
            return
        
        # 2. Create if not found
        if not seller_id:
            print("Creating Brew Boulevard seller...")
            resp = await client.post(f"{API_URL}/sellers/", json={
                "seller_name": "Brew Boulevard",
                "marketplace": "multi",
                "region": "IN",
                "email": "hello@brewboulevard.in"
            }, headers=headers)
            seller_id = resp.json().get("seller_id")
            
        print(f"Using Seller ID: {seller_id}")
        
        # 3. Upload dataset
        print(f"Uploading {FILE_PATH}...")
        with open(FILE_PATH, "rb") as f:
            files = {
                'file': ('test_dataset.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {
                'seller_id': seller_id
            }
            upload_resp = await client.post(
                f"{API_URL}/upload/full",
                data=data,
                files=files,
                headers=headers,
                timeout=120.0
            )
            print("Upload Status:", upload_resp.status_code)
            try:
                print("Response:", upload_resp.json())
            except:
                print("Response Text:", upload_resp.text)

if __name__ == "__main__":
    asyncio.run(main())
