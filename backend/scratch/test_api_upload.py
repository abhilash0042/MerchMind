import asyncio
import os
import io
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from datetime import date

client = TestClient(app)

def test_full_upload():
    print("Testing Full Upload API...")
    
    # Need a valid seller_id from the database
    seller_id = None
    
    # We will upload the test_dataset.xlsx
    file_path = "test_dataset.xlsx"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return
        
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # First, let's get or create a seller
    import httpx
    try:
        # We can directly query the DB to get a seller or create one
        import psycopg2
        conn = psycopg2.connect(
            host="aws-1-ap-south-1.pooler.supabase.com",
            port=5432,
            dbname="postgres",
            user="postgres.gwwhksdelequvapksgqx",
            password="Abhilash@142",
            sslmode="require"
        )
        cur = conn.cursor()
        cur.execute("SELECT seller_id FROM sellers LIMIT 1")
        row = cur.fetchone()
        if row:
            seller_id = str(row[0])
            print(f"Using existing seller_id: {seller_id}")
        else:
            print("No seller found. Please create one.")
            return
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error getting seller: {e}")
        return

    # Now post to the endpoint
    print("Uploading file to /upload/full endpoint...")
    response = client.post(
        "/upload/full",
        data={"seller_id": seller_id},
        files={"file": ("test_dataset.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers={"X-API-Key": "dev-api-key"}
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response JSON: {response.json()}")

if __name__ == "__main__":
    test_full_upload()
