import urllib.request
import json

url = 'http://127.0.0.1:8010/sellers/'
data = json.dumps({
    "seller_name": "Brew Boulevard",
    "marketplace": "multi",
    "region": "IN",
    "email": "hello@brewboulevard.in"
}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Other Error:", str(e))
