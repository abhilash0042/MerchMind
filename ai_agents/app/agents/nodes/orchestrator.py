"""
Orchestrator Node — Control Tower.
Fetches REAL aggregated data from the CommercePulse backend analytics API
and injects it into the shared state so every downstream agent has hard numbers.
"""
import os
import re
import httpx
from dotenv import load_dotenv
from app.agents.state import SystemState

# Ensure .env is loaded BEFORE reading env vars
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8010").rstrip("/")
API_KEY = os.getenv("COMMERCE_API_KEY", "")

_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


def _is_valid_uuid(value: str) -> bool:
    """Check if a string is a valid UUID format."""
    return bool(value and _UUID_RE.match(value))


def _fetch(endpoint: str, params: dict) -> dict:
    """Helper to call the backend analytics API synchronously."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    try:
        resp = httpx.get(f"{BACKEND_URL}{endpoint}", params=params, headers=headers, timeout=15.0)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError:
        print(f"  🔴 Orchestrator: Cannot connect to backend at {BACKEND_URL}{endpoint}. Is the backend running?")
        return {}
    except httpx.HTTPStatusError as e:
        print(f"  🔴 Orchestrator: Backend returned {e.response.status_code} for {endpoint}")
        return {}
    except Exception as e:
        print(f"  ⚠️ Orchestrator: Unexpected error fetching {endpoint}: {e}")
        return {}


def run_orchestrator(state: SystemState) -> SystemState:
    """
    Control Tower Node.
    Fetches real aggregated analytics from the backend API and enriches
    the snapshot_data so domain agents have concrete numbers to analyze.
    """
    seller_id = state.get("seller_id", "")
    
    # ── Auto-resolve seller_id for single-seller mode ──
    # If no valid UUID provided, auto-resolve from the backend database
    if not _is_valid_uuid(seller_id):
        print("  🔍 Orchestrator: No valid UUID provided. Attempting to auto-resolve first seller from backend...")
        debug_info = _fetch("/analytics/debug-db", {})
        resolved_id = debug_info.get("active_seller_id")
        if resolved_id and _is_valid_uuid(resolved_id):
            print(f"  ✅ Orchestrator: Auto-resolved Seller ID → {resolved_id}")
            seller_id = resolved_id
        else:
            print("  ⚠️ Orchestrator: Could not auto-resolve seller. Queries may fail.")

    time_start = state.get("time_window_start", "")
    time_end = state.get("time_window_end", "")

    print(f"🚀 [Orchestrator] Fetching LIVE data for Seller {seller_id} ({time_start} → {time_end})")

    # Calculate days for the lookback window
    days = 30  # default
    try:
        from datetime import date
        d_start = date.fromisoformat(time_start)
        d_end = date.fromisoformat(time_end)
        days = max((d_end - d_start).days, 7)
    except Exception:
        pass

    base_params = {"seller_id": seller_id, "days": days}

    # ── 1. Executive Dashboard KPIs ──
    print("  📊 Fetching dashboard KPIs...")
    dashboard = _fetch("/analytics/dashboard", base_params)

    # ── 2. Revenue by Marketplace ──
    print("  💰 Fetching revenue by marketplace...")
    revenue = _fetch("/analytics/revenue", base_params)

    # ── 3. Inventory Alerts (low stock / stockout) ──
    print("  📦 Fetching inventory alerts...")
    inventory_alerts = _fetch("/analytics/inventory/alerts", {"seller_id": seller_id})

    # ── 4. Full Inventory Status ──
    print("  📦 Fetching full inventory status...")
    inventory_status = _fetch("/analytics/inventory/status", {"seller_id": seller_id})

    # ── 5. Pricing & Margins ──
    print("  💲 Fetching pricing margins...")
    pricing = _fetch("/analytics/pricing/margins", {"seller_id": seller_id})

    # ── 6. Traffic Funnel & ROAS ──
    print("  📈 Fetching traffic funnel...")
    traffic = _fetch("/analytics/traffic/funnel", {**base_params, "days": min(days, 30)})

    # ── 7. Logistics & RTO ──
    print("  🚚 Fetching logistics / RTO rate...")
    logistics = _fetch("/analytics/logistics/rto-rate", base_params)

    # ── Enrich the snapshot_data with real numbers ──
    enriched_snapshot = {
        **(state.get("snapshot_data") or {}),
        "dashboard_kpis": dashboard.get("kpis", {}),
        "revenue_by_marketplace": revenue.get("data", []),
        "inventory_alerts": inventory_alerts.get("alerts", []),
        "inventory_alert_count": inventory_alerts.get("alert_count", 0),
        "inventory_status": inventory_status.get("data", []),
        "pricing_margins": pricing.get("data", []),
        "traffic_funnel": traffic.get("data", []),
        "logistics": logistics.get("data", []),
        "period_days": days,
    }

    print(f"  ✅ Orchestrator enriched snapshot with {len(enriched_snapshot)} data sections")

    # Update state with enriched data and resolved seller_id
    state_update = dict(state)
    state_update["seller_id"] = seller_id
    state_update["snapshot_data"] = enriched_snapshot
    return state_update
