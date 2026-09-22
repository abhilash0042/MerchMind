import requests
try:
    r = requests.get("http://127.0.0.1:8001/")
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text}")
except Exception as e:
    print(f"Failed to reach 127.0.0.1:8001: {e}")

try:
    r = requests.get("http://localhost:8001/")
    print(f"Status Localhost: {r.status_code}")
    print(f"Body Localhost: {r.text}")
except Exception as e:
    print(f"Failed to reach localhost:8001: {e}")
