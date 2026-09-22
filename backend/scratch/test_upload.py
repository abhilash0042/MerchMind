import httpx
import json

base_url = "http://localhost:8010"
headers = {"X-API-Key": "your-production-api-key"}

# 1. Create a seller
import uuid
r = httpx.post(
    f"{base_url}/sellers/",
    headers=headers,
    json={
        "seller_name": f"Test Seller {uuid.uuid4().hex[:6]}",
        "marketplace": "multi",
        "region": "IN",
        "email": f"test_{uuid.uuid4().hex[:6]}@test.com"
    }
)
if r.status_code != 200:
    print("Failed to create seller:", r.text)
    r.raise_for_status()

seller = r.json()
print("Created seller:", seller["seller_id"])

# 2. Upload the excel file
with open("test_dataset.xlsx", "rb") as f:
    files = {"file": ("test_dataset.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"seller_id": seller["seller_id"]}
    r = httpx.post(f"{base_url}/upload/full", headers=headers, data=data, files=files, timeout=60.0)
    
print("Upload status code:", r.status_code)
print("Upload response:", r.text)
