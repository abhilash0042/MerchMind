import os
import json
from typing import Dict, Any
from app.agents.state import SystemState

def run_product_orchestrator(state: SystemState) -> dict:
    """
    Orchestrator node for Per-Product Analysis.
    Takes the product_data provided in the state and structures it for the synthesizer.
    """ 
    seller_id = state.get("seller_id")
    product_id = state.get("product_id")
    raw_snapshot = state.get("snapshot_data", {})
    
    print(f"🧠 [Product Orchestrator] Gathering data for product {product_id}...")
    
    # 1. Structure the raw snapshot into proper business intelligence sections
    enriched_snapshot = {
        "product_identity": {
            "product_name": raw_snapshot.get("product_name"),
            "sku": raw_snapshot.get("sku"),
            "category": raw_snapshot.get("category"),
            "sub_category": raw_snapshot.get("sub_category"),
            "brand": raw_snapshot.get("brand"),
            "primary_marketplace": raw_snapshot.get("marketplace"),
        },
        "profit_and_loss": {
            "total_revenue": raw_snapshot.get("total_revenue", 0),
            "total_orders": raw_snapshot.get("total_orders", 0),
            "avg_order_value": raw_snapshot.get("avg_order_value", 0),
            "discounted_orders": raw_snapshot.get("discounted_orders", 0),
            "total_discount_given": raw_snapshot.get("total_discount_given", 0),
            "total_shipping_collected": raw_snapshot.get("total_shipping_collected", 0),
            "total_returns": raw_snapshot.get("total_returns", 0),
            "return_rate_pct": raw_snapshot.get("return_rate_pct", 0),
        },
        "pricing_by_marketplace": raw_snapshot.get("pricing_by_marketplace", []),
        "revenue_by_marketplace": raw_snapshot.get("revenue_by_marketplace", []),
        "advertising_performance": {
            "total_ad_spend": raw_snapshot.get("total_ad_spend", 0),
            "total_ad_revenue": raw_snapshot.get("total_ad_revenue", 0),
            "roas": raw_snapshot.get("roas", 0),
            "total_impressions": raw_snapshot.get("total_impressions", 0),
            "total_clicks": raw_snapshot.get("total_clicks", 0),
            "ctr_pct": raw_snapshot.get("ctr_pct", 0),
            "cost_per_click": raw_snapshot.get("cost_per_click", 0),
        },
        "inventory_health": {
            "stock_level": raw_snapshot.get("stock_level", 0),
            "reserved_stock": raw_snapshot.get("reserved_stock", 0),
            "reorder_threshold": raw_snapshot.get("reorder_threshold", 0),
            "days_of_stock": raw_snapshot.get("days_of_stock", 0),
        },
        "logistics_quality": {
            "rto_count": raw_snapshot.get("rto_count", 0),
            "rto_rate_pct": raw_snapshot.get("rto_rate_pct", 0),
            "avg_delivery_days": raw_snapshot.get("avg_delivery_days", 0),
        },
        "historical_context": ""
    }
    return {"snapshot_data": enriched_snapshot}
