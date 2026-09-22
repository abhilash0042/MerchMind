"""
Customer & Market Intelligence Agent — Brand Strategist Persona.
Analyzes channel performance, product-market fit, category concentration,
and cancellation patterns using REAL data from the Orchestrator-enriched snapshot.
"""
import os
import json
from langchain_groq import ChatGroq
from app.agents.state import SystemState
from app.agents.schemas import MarketInsights


def run_customer_agent(state: SystemState) -> dict:
    """
    Brand Strategist Persona — Channel & Product Strategy.
    Examines marketplace performance differences, product-market fit gaps,
    category concentration risks, and cancellation patterns.
    """
    from app.db.supabase_client import fetch_recent_context
    print("🎯 [Market Agent] Analyzing channel performance and product-market fit...")

    seller_id = state.get("seller_id")
    snapshot = state.get("snapshot_data", {})

    # Extract real data (handle both global and per-product schemas)
    if "pricing_by_marketplace" in snapshot:
        # Product mode
        dashboard_kpis = json.dumps(snapshot.get("profit_and_loss", {}), indent=2, default=str)[:800]
        revenue_by_mp = json.dumps(snapshot.get("revenue_by_marketplace", []), indent=2, default=str)[:800]
        pricing_margins = json.dumps(snapshot.get("pricing_by_marketplace", []), indent=2, default=str)[:800]
        traffic_funnel = json.dumps(snapshot.get("advertising_performance", {}), indent=2, default=str)[:800]
        inventory_status = json.dumps(snapshot.get("inventory_health", {}), indent=2, default=str)[:800]
    else:
        # Global mode
        dashboard_kpis = json.dumps(snapshot.get("dashboard_kpis", {}), indent=2, default=str)[:800]
        revenue_by_mp = json.dumps(snapshot.get("revenue_by_marketplace", []), indent=2, default=str)[:800]
        pricing_margins = json.dumps(snapshot.get("pricing_margins", [])[:5], indent=2, default=str)[:800]
        traffic_funnel = json.dumps(snapshot.get("traffic_funnel", [])[:5], indent=2, default=str)[:800]
        inventory_status = json.dumps(snapshot.get("inventory_status", [])[:5], indent=2, default=str)[:800]


    try:
        recent_context = fetch_recent_context(seller_id, limit=3)
    except Exception as e:
        print(f"  ⚠️ Could not fetch Supabase context: {e}")
        recent_context = "No historical context available (Supabase unavailable)."

    # Set up lazy structured model inside retry loop below

    prompt = f"""
You are the Chief Brand Strategist of "Brew Boulevard", a D2C specialty coffee brand selling on Amazon India, Flipkart, and their own Shopify store. The brand sells 15 coffee products across categories like Whole Bean, Ground, Cold Brew, Instant, and Drip Bags.

Your focus: Which products sell well WHERE, which channels are underperforming, and what's the strategy to grow the brand's total addressable market.

=== OVERALL KPIs (Last {snapshot.get('period_days', 30)} days) ===
{dashboard_kpis}

=== REVENUE BY MARKETPLACE ===
Shows gross_revenue, net_revenue, total_orders, delivered_orders, cancelled_orders, returned_orders, avg_order_value per marketplace:
{revenue_by_mp}

=== PRODUCT PRICING ACROSS MARKETPLACES ===
Same products may have different prices and margins across channels:
{pricing_margins}

=== TRAFFIC & CONVERSION BY PRODUCT × MARKETPLACE ===
Shows impressions, clicks, sessions, orders, CTR, conversion_rate, ad_spend, revenue_from_ads, ROAS per product per marketplace:
{traffic_funnel}

=== INVENTORY STATUS ===
{inventory_status}

=== HISTORICAL CONTEXT ===
{recent_context}

YOUR ANALYSIS MUST:
<thinking>
First, review the KPIs and Marketplace splits to find the biggest gap in channel performance.
Next, analyze pricing margins vs traffic. Does high traffic translate to high conversion? If not, why?
Then, look for SKUs carrying the bulk of the revenue.
Formulate specific strategies to fix these gaps.
</thinking>

1. **Channel Performance Gap**: Compare Amazon vs Flipkart vs Shopify on revenue, orders, avg_order_value, and cancellation rate. Identify the WEAKEST channel and diagnose WHY it's underperforming (is it traffic? conversion? pricing? inventory?).

2. **Product-Market Fit Analysis**: Which products sell well on one marketplace but poorly on another? This indicates a listing quality, pricing, or visibility problem — not a product problem. Identify the specific SKUs and channels.

3. **Category Concentration Risk**: Is 80%+ of revenue coming from just 2-3 SKUs? If so, that's a dangerous concentration. Identify the dependency and recommend diversification strategies.

4. **Cancellation & Return Pattern**: From the KPIs, analyze cancellation_rate_pct. If it's above 5%, that's a red flag. Hypothesize the most likely cause based on the available data (pricing mismatch? delivery speed? product expectations?).

5. **Growth Strategy**: For each underperforming channel or product, provide a SPECIFIC, AGGRESSIVE strategy:
   - "Launch BB-CF-008 Cold Brew on Flipkart with a ₹50 introductory discount — this product does ₹X/month on Amazon but has zero presence on Flipkart"
   - "Increase Shopify organic traffic by creating coffee brewing guide content — Shopify has the highest margin (0% commission) but lowest traffic"

Reference actual product names, prices, and marketplace data from above. Do NOT give generic advice like "improve customer experience". Be ruthless about protecting margins.

IMPORTANT: Every action in recommended_actions MUST include ALL required fields: action_name, reason, strategy, description, estimated_impact_percentage, financial_impact_monthly, is_profit_safe, risk_level, difficulty, timeframe. Do NOT omit any field.
"""

    from app.utils import get_groq_api_key, get_fallback_llm
    
    import time
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            key = get_groq_api_key()
            llm = get_fallback_llm(api_key=key, temperature=0.1)
            result: MarketInsights = llm.with_structured_output(MarketInsights).invoke(prompt)
            return {"market_insights": result}
        except Exception as e:
            error_str = str(e)
            if attempt < max_retries:
                if "rate_limit_exceeded" in error_str or "429" in error_str:
                    print(f"  ⚠️ [Customer Agent] Rate limit hit. Sleeping for 5s... (Attempt {attempt+1})")
                    time.sleep(5)
                    continue
                if "tool_use_failed" in error_str or "missing properties" in error_str:
                    print(f"  ⚠️ [Customer Agent] Retry {attempt + 1}/{max_retries} due to schema error...")
                    time.sleep(2)
                    continue
            print(f"  ❌ [Customer Agent] Failed after {attempt + 1} attempts: {e}")
            return {"market_insights": None}
