import asyncio
import httpx
import os
import pandas as pd
import io

async def test_upload():
    # Create a simple Excel file in memory
    df_orders = pd.DataFrame({
        "order id": ["123"],
        "marketplace": ["Amazon"],
        "sku": ["TEST-SKU"],
        "status": ["Delivered"],
        "quantity": [1],
        "selling price": [100.0],
        "order date": ["2023-01-01"]
    })
    
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df_orders.to_excel(writer, sheet_name="Orders", index=False)
    
    excel_buf.seek(0)

    url = "http://localhost:8002/upload/full"
    files = {
        'file': ('test.xlsx', excel_buf.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data = {
        'seller_id': '11111111-1111-1111-1111-111111111111'
    }
    headers = {
        'X-API-Key': 'your-production-api-key'
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, data=data, files=files, headers=headers)
            print("Status:", resp.status_code)
            print("Body:", resp.text)
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    asyncio.run(test_upload())
