import httpx
import os
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def fetch_live_product_roas(product_id: str) -> str:
    """
    Fetches the live, mathematically exact ROAS (Return on Ad Spend) for a specific product.
    Use this tool to verify ROAS numbers before making marketing campaign decisions.
    Returns a string explaining the current ROAS, or an error if backend is unreachable.
    """
    backend_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8010").rstrip("/")
    api_key = os.getenv("COMMERCE_API_KEY", "")
    url = f"{backend_url}/analytics/product/{product_id}/roas"
    try:
        response = httpx.get(url, headers={"X-API-Key": api_key}, timeout=5.0)
        response.raise_for_status()
        data = response.json()
        return f"Live ROAS for {product_id} is {data.get('roas', 'unknown')}. Total Spend: {data.get('total_spend', 'unknown')}."
    except Exception as e:
        return f"Could not verify live ROAS due to API error: {str(e)}. Use the snapshot data instead."

@tool
def fetch_live_product_inventory(product_id: str) -> str:
    """
    Fetches the live inventory count for a specific product.
    Use this tool to verify if a product is actually out of stock before recommending a restock.
    """
    backend_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8010").rstrip("/")
    api_key = os.getenv("COMMERCE_API_KEY", "")
    url = f"{backend_url}/analytics/inventory/{product_id}"
    try:
        response = httpx.get(url, headers={"X-API-Key": api_key}, timeout=5.0)
        response.raise_for_status()
        data = response.json()
        return f"Live inventory for {product_id} is {data.get('available_stock', 'unknown')} units."
    except Exception as e:
        return f"Could not verify live inventory due to API error: {str(e)}. Use the snapshot data instead."
