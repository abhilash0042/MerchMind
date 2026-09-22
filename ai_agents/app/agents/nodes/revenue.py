"""
Revenue Intelligence Agent — CFO Persona.
Analyzes pricing, margins, discount effectiveness, and stockout revenue impact
using REAL data from the Orchestrator-enriched snapshot.
"""
import os
import json
from langchain_groq import ChatGroq
from app.agents.state import SystemState
from app.agents.schemas import RevenueInsights


def run_revenue_agent(state: SystemState) -> dict:
    """
    CFO Persona — Pricing & Margin Strategist.
    Examines real pricing margins, marketplace commissions, discount patterns,
    and stockout impact to find revenue leaks and growth opportunities.
    """
    from app.db.supabase_client import fetch_recent_context
    print("📈 [Revenue Agent] Analyzing pricing, margins, and revenue leaks...")

    seller_id = state.get("seller_id")
    snapshot = state.get("snapshot_data", {})

    # Extract the real data sections injected by the Orchestrator
    # Handle both Global analysis schema and Per-Product analysis schema
    if "profit_and_loss" in snapshot:
        # We are in Product Analysis mode
        dashboard_kpis = json.dumps(snapshot.get("profit_and_loss", {}), indent=2, default=str)[:800]
        pricing_margins = json.dumps(snapshot.get("pricing_by_marketplace", []), indent=2, default=str)[:800]
        revenue_by_mp = json.dumps(snapshot.get("revenue_by_marketplace", []), indent=2, default=str)[:800]
        inventory_alerts = json.dumps(snapshot.get("inventory_health", {}), indent=2, default=str)[:800]
    else:
        # We are in Global Analysis mode
        dashboard_kpis = json.dumps(snapshot.get("dashboard_kpis", {}), indent=2, default=str)[:800]
        pricing_margins = json.dumps(snapshot.get("pricing_margins", [])[:5], indent=2, default=str)[:800]
        revenue_by_mp = json.dumps(snapshot.get("revenue_by_marketplace", []), indent=2, default=str)[:800]
        inventory_alerts = json.dumps(snapshot.get("inventory_alerts", [])[:5], indent=2, default=str)[:800]

    # Also fetch vector context for historical trends
    try:
        recent_context = fetch_recent_context(seller_id, limit=3)
    except Exception as e:
        print(f"  ⚠️ Could not fetch Supabase context: {e}")
        recent_context = "No historical context available (Supabase unavailable)."

    # Set up structured model inside retry loop below

    prompt = f"""
You are the Chief Financial Officer (CFO) of a D2C (Direct-to-Consumer) brand selling specialty coffee products across Indian marketplaces (Amazon India, Flipkart, and their own Shopify store).

Your job is to analyze the REAL financial data below and identify exactly where this brand is losing money and where they can grow revenue. Be ruthlessly specific — reference actual product names, SKUs, prices, and margins from the data.

=== OVERALL BUSINESS KPIs (Last {snapshot.get('period_days', 30)} days) ===
{dashboard_kpis}

=== REVENUE BY MARKETPLACE ===
{revenue_by_mp}

=== PRODUCT PRICING & MARGINS (Current Snapshot) ===
Each row shows: SKU, product name, marketplace, selling_price, cost_price, MRP, commission_pct, discount_percentage, net_margin, margin_pct
{pricing_margins}

=== STOCKOUT & LOW-STOCK ALERTS ===
Products currently out of stock or below reorder threshold (these represent LOST SALES):
{inventory_alerts}

=== HISTORICAL CONTEXT (from vector DB) ===
{recent_context}

YOUR ANALYSIS MUST:
<thinking>
1. Scan pricing_margins for any row with margin_pct < 15%. Calculate the lost margin value.
2. Check inventory_alerts. If a top product is OOS, calculate daily lost sales (selling_price * avg daily orders).
3. Find products with high discount_percentage where commission is already high.
4. Formulate pricing/discount reduction strategies.
</thinking>

1. **Identify Margin Killers**: Which specific products have margin_pct below 15%? Why? Is it commission, discount, or cost price? For each, calculate the exact margin gap.

2. **Quantify Stockout Revenue Loss**: For each out-of-stock product, estimate the daily revenue being lost based on its historical selling_price and order volume. Stockouts are the #1 silent killer of D2C brands.

3. **Detect Discount Abuse**: Are any products being discounted unnecessarily (i.e., products that would sell at full price)? Calculate how much margin is being wasted on pointless discounts.

4. **Marketplace Commission Analysis**: Compare the effective commission rates across Amazon, Flipkart, and Shopify. Identify products where switching the primary sales channel would significantly boost margin.

5. **Pricing Action Plan**: For each underperforming product, provide a SPECIFIC pricing recommendation with exact numbers (e.g., "Increase BB-CF-005 selling price from ₹349 to ₹399 on Amazon — margin improves from 8.2% to 16.5%").

Be brutally honest. Use actual numbers from the data. Do NOT give generic advice.

IMPORTANT: Every action in recommended_actions MUST include ALL required fields: action_name, reason, strategy, description, estimated_impact_percentage, financial_impact_monthly, is_profit_safe, risk_level, difficulty, timeframe. Do NOT omit any field.
"""

    from app.utils import get_groq_api_key
    
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            key = get_groq_api_key()
            from app.utils import get_fallback_llm
            llm = get_fallback_llm(api_key=key, temperature=0.0)
            from app.agents.tools.analytics_tools import fetch_live_product_inventory
            llm_with_tools = llm.bind_tools([fetch_live_product_inventory])
            
            messages = [{"role": "user", "content": prompt}]
            ai_msg = llm_with_tools.invoke(messages)
            
            # Execute tool if requested
            if getattr(ai_msg, "tool_calls", None):
                messages.append(ai_msg)
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"] == "fetch_live_product_inventory":
                        product_id = tool_call["args"].get("product_id", "")
                        tool_res = fetch_live_product_inventory.invoke({"product_id": product_id})
                        messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["name"], "content": str(tool_res)})
            
            # Now extract the final structured output
            result: RevenueInsights = llm.with_structured_output(RevenueInsights).invoke(messages)
            return {"revenue_insights": result}
        except Exception as e:
            error_str = str(e)
            if attempt < max_retries and ("tool_use_failed" in error_str or "missing properties" in error_str):
                print(f"  ⚠️ [Revenue Agent] Retry {attempt + 1}/{max_retries} due to schema error...")
                continue
            print(f"  ❌ [Revenue Agent] Failed after {attempt + 1} attempts: {e}")
            return {"revenue_insights": None}
