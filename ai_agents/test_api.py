import requests
import json

url = "http://127.0.0.1:8000/api/v1/simulate"

payload = {
    "seller_id": "SLR-1094-APPLE",
    "time_window_start": "2026-02-01",
    "time_window_end": "2026-02-15",
    "snapshot_data": {
        "scenario_event": "Competitor 'TechZone' dropped iPhone 15 prices by 8%.",
        "revenue_metrics": {
            "conversion_rate_drop_pct": 6.0,
            "estimated_revenue_loss_inr": 120000,
            "top_affected_sku": "SKU44-IPHONE15-128GB",
            "price_sensitivity": "High",
            "gross_margin_pct": 18.0
        },
        "operational_metrics": {
            "avg_delivery_delay_increase_days": 2.0,
            "return_rate_increase_pct": 12.0,
            "problematic_warehouse": "BLR-01"
        },
        "market_signals": {
            "recent_reviews_sentiment": "Negative spike",
            "primary_complaint_topic": "Delivery delays and high price compared to TechZone",
            "traffic_volume": "Stable",
            "conversion_volume": "Dropping"
        }
    }
}

headers = {"Content-Type": "application/json"}

print("Triggering API...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Failed to connect to API: {e}")
