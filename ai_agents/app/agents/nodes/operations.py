"""
Operations & Cost Intelligence Agent — COO Persona.
Analyzes logistics performance, RTO rates, delivery delays, and fulfillment
strategy using REAL data from the Orchestrator-enriched snapshot.
"""
import os
import json
from langchain_groq import ChatGroq
from app.agents.state import SystemState
from app.agents.schemas import OperationsInsights


def run_ops_agent(state: SystemState) -> dict:
    """
    COO Persona — Supply Chain & Logistics Optimizer.
    Examines real RTO rates, delivery performance, fulfillment type splits,
    and operational costs to identify where the supply chain is bleeding money.
    """
    from app.db.supabase_client import fetch_recent_context
    from app.utils import get_groq_api_key
    print("⚙️ [Ops Agent] Analyzing logistics, RTO, and fulfillment performance...")

    seller_id = state.get("seller_id")
    snapshot = state.get("snapshot_data", {})

    # Extract real data (handle both global and per-product schemas)
    if "logistics_quality" in snapshot:
        # Product mode
        dashboard_kpis = json.dumps(snapshot.get("profit_and_loss", {}), indent=2, default=str)[:800]
        logistics = json.dumps(snapshot.get("logistics_quality", {}), indent=2, default=str)[:800]
        inventory_alerts = json.dumps(snapshot.get("inventory_health", {}), indent=2, default=str)[:800]
        inventory_status = json.dumps(snapshot.get("inventory_health", {}), indent=2, default=str)[:800]
    else:
        # Global mode
        dashboard_kpis = json.dumps(snapshot.get("dashboard_kpis", {}), indent=2, default=str)[:800]
        logistics = json.dumps(snapshot.get("logistics", [])[:5], indent=2, default=str)[:800]
        inventory_alerts = json.dumps(snapshot.get("inventory_alerts", [])[:5], indent=2, default=str)[:800]
        inventory_status = json.dumps(snapshot.get("inventory_status", [])[:5], indent=2, default=str)[:800]

    try:
        recent_context = fetch_recent_context(seller_id, limit=3)
    except Exception as e:
        print(f"  ⚠️ Could not fetch Supabase context: {e}")
        recent_context = "No historical context available (Supabase unavailable)."

    prompt = f"""You are the Chief Operating Officer (COO) of a D2C coffee brand ("Brew Boulevard") selling across Amazon India, Flipkart, and Shopify in India.

Your focus is fulfillment efficiency, RTO (Return to Origin) reduction, delivery speed, and warehouse operations. RTO is the BIGGEST cost killer for Indian D2C brands — every RTO costs the seller 2x shipping + product damage risk + lost sale.

=== OVERALL KPIs ===
{dashboard_kpis}

=== LOGISTICS & RTO DATA BY MARKETPLACE AND FULFILLMENT TYPE ===
Each row shows: marketplace, total_shipments, rto_count, rto_rate_pct, delivered count, avg_shipping_days, fulfillment_type
{logistics}

=== INVENTORY STATUS (Current Stock Levels) ===
{inventory_status}

=== INVENTORY ALERTS (Low Stock / Stockout) ===
{inventory_alerts}

=== HISTORICAL CONTEXT ===
{recent_context}

YOUR ANALYSIS MUST:
<thinking>
1. Identify the highest RTO rates and calculate the financial hit (RTO count * ~200 INR).
2. Compare FBA/WFS/Assured fulfillment against seller-fulfilled RTO and delivery speeds.
3. Check inventory status for critical out-of-stock risks.
4. Formulate specific operational fixes.
</thinking>

1. **RTO Root Cause Analysis**: Which marketplace + fulfillment_type combination has the WORST RTO rate? Calculate the exact financial cost of RTO for that combination. In India, a typical RTO costs ₹150-300 per order (forward + reverse shipping + packaging damage). Multiply by rto_count to get total RTO cost.

2. **Fulfillment Strategy**: Compare seller-fulfilled vs marketplace-fulfilled (FBA/Flipkart Assured) performance. If seller-fulfilled has significantly higher RTO or slower delivery, recommend switching specific products to marketplace fulfillment. Be specific about WHICH products.

3. **Delivery Speed Impact**: If avg_shipping_days > 4, that's a red flag for customer satisfaction and repeat purchases. Identify which channels are slow and why.

4. **Inventory Operations**: Are any high-demand products running low? Calculate the number of days until stockout based on available_stock and days_of_stock. Prioritize reorder recommendations by revenue impact.

5. **Cost Optimization Actions**: Every recommendation must include:
   - A short description field summarizing the expected outcome
   - The exact problem (e.g., "RTO rate on Flipkart seller-fulfilled is 15.2%")
   - The financial cost (e.g., "Costing ₹45,000/month in wasted shipping")
   - The fix (e.g., "Move top 5 Flipkart SKUs to Flipkart Assured fulfillment")
   - Expected improvement (e.g., "Expected RTO drop to 3-5%, saving ₹35,000/month")

IMPORTANT: Return a single, complete OperationsInsights response. Every action in recommended_actions MUST include ALL required fields: action_name, reason, strategy, description, estimated_impact_percentage, financial_impact_monthly, is_profit_safe, risk_level, difficulty, timeframe. Do NOT omit any field.

Use ONLY the real data provided. Do NOT make up numbers. If a data section is empty, note it and focus on the sections that have data."""

    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            key = get_groq_api_key()
            from app.utils import get_fallback_llm
            llm = get_fallback_llm(api_key=key, temperature=0.0)
            result: OperationsInsights = llm.with_structured_output(OperationsInsights).invoke(prompt)
            return {"ops_insights": result}
        except Exception as e:
            error_str = str(e)
            if attempt < max_retries:
                if "rate_limit_exceeded" in error_str or "429" in error_str:
                    import time
                    print(f"  ⚠️ [Ops Agent] Rate limit hit. Sleeping for 5s... (Attempt {attempt+1})")
                    time.sleep(5)
                    continue
                if "tool_use_failed" in error_str or "missing properties" in error_str:
                    print(f"  ⚠️ [Ops Agent] Retry {attempt + 1}/{max_retries} due to schema validation error...")
                    continue
            print(f"  ❌ [Ops Agent] Failed after {attempt + 1} attempts: {e}")
            return {"ops_insights": None}
