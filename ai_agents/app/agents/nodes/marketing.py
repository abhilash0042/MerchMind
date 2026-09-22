"""
Marketing & Growth Intelligence Agent — CMO Persona.
Analyzes ad spend efficiency, ROAS, traffic quality, conversion funnels,
and wasted budget using REAL data from the Orchestrator-enriched snapshot.
"""
import os
import json
from langchain_groq import ChatGroq
from app.agents.state import SystemState
from app.agents.schemas import MarketingInsights


def run_marketing_agent(state: SystemState) -> dict:
    """
    CMO Persona — Ad Spend & Growth Optimizer.
    Examines real traffic funnel data, ROAS per product, CTR patterns,
    and conversion rates to kill wasted spend and double down on winners.
    """
    from app.db.supabase_client import fetch_recent_context
    print("📣 [Marketing Agent] Analyzing ad spend, ROAS, and traffic quality...")

    seller_id = state.get("seller_id")
    snapshot = state.get("snapshot_data", {})

    # Extract real data (handle both global and per-product schemas)
    if "advertising_performance" in snapshot:
        # Product mode
        dashboard_kpis = json.dumps(snapshot.get("profit_and_loss", {}), indent=2, default=str)[:800]
        traffic_funnel = json.dumps(snapshot.get("advertising_performance", {}), indent=2, default=str)[:1000]
        revenue_by_mp = json.dumps(snapshot.get("revenue_by_marketplace", []), indent=2, default=str)[:800]
        pricing_margins = json.dumps(snapshot.get("pricing_by_marketplace", []), indent=2, default=str)[:800]
    else:
        # Global mode
        dashboard_kpis = json.dumps(snapshot.get("dashboard_kpis", {}), indent=2, default=str)[:800]
        traffic_funnel = json.dumps(snapshot.get("traffic_funnel", [])[:5], indent=2, default=str)[:1000]
        revenue_by_mp = json.dumps(snapshot.get("revenue_by_marketplace", []), indent=2, default=str)[:800]
        pricing_margins = json.dumps(snapshot.get("pricing_margins", [])[:5], indent=2, default=str)[:800]


    try:
        recent_context = fetch_recent_context(seller_id, limit=3)
    except Exception as e:
        print(f"  ⚠️ Could not fetch Supabase context: {e}")
        recent_context = "No historical context available (Supabase unavailable)."

    # Set up lazy structured model inside retry loop below

    prompt = f"""
You are the Chief Marketing Officer (CMO) of "Brew Boulevard", a D2C specialty coffee brand in India. You manage ad spend across Amazon Sponsored Ads, Flipkart Ads, and Google/Meta ads for the Shopify store.

Your ONLY goal: maximize Return on Ad Spend (ROAS) and eliminate every rupee of wasted advertising budget. You are data-obsessed and will not tolerate spending money on traffic that doesn't convert.

=== OVERALL KPIs ===
{dashboard_kpis}

=== TRAFFIC FUNNEL DATA (Per Product × Per Marketplace) ===
Each row shows: SKU, product_name, category, marketplace, total_impressions, total_clicks, total_sessions, total_orders, ctr_pct (Click-Through Rate), conversion_rate_pct, total_ad_spend, total_revenue_from_ads, roas (Return on Ad Spend)
{traffic_funnel}

=== REVENUE BY MARKETPLACE ===
{revenue_by_mp}

=== PRODUCT PRICING (for context on whether pricing kills conversion) ===
{pricing_margins}

=== HISTORICAL CONTEXT ===
{recent_context}

YOUR ANALYSIS MUST:
<thinking>
1. Calculate ROAS for each row (revenue / ad_spend). Identify any under 2.0.
2. Check CTRs. Below 1.5% is a listing problem.
3. Check Conversion Rates. Below 2% is a page/price problem.
4. Synthesize the total wasted spend.
</thinking>

1. **ROAS Audit — Kill the Losers**: Identify EVERY product × marketplace combination where ROAS < 2.0. For each:
   - Calculate exact wasted spend: total_ad_spend - (total_revenue_from_ads)
   - Recommend: KILL (pause immediately), REDUCE (cut budget 50%), or FIX (listing/pricing issue)
   - Example: "BB-CF-010 on Flipkart: ₹8,500 ad spend → ₹2,100 revenue = ROAS 0.25. KILL this campaign immediately. Saving ₹8,500/month."

2. **CTR Analysis — Listing Quality**: Products with high impressions but low CTR (<1.5%) have a listing problem (bad main image, weak title, or wrong pricing). Identify specific products and recommend what to fix.

3. **Conversion Rate Analysis**: Products with decent CTR but low conversion_rate (<2%) indicate a product page problem (bad reviews, competitor is cheaper, out of stock). Cross-reference with pricing data to diagnose.

4. **Budget Reallocation**: Take the saved budget from killed/reduced campaigns and recommend WHERE to reallocate it. Prioritize products with ROAS > 4.0 and room to scale (not maxed out on impressions).

5. **Total Wasted Spend Calculation**: Sum up ALL wasted/inefficient ad spend across all products. This is your headline number. Break it down by marketplace.

Every recommendation must include:
- The exact product name and marketplace
- Current spend and revenue numbers
- What to do (kill/reduce/scale/fix)
- Expected financial impact

Do NOT give abstract marketing advice. Use the REAL numbers provided.

IMPORTANT: Every action in recommended_actions MUST include ALL required fields: action_name, reason, strategy, description, estimated_impact_percentage, financial_impact_monthly, is_profit_safe, risk_level, difficulty, timeframe. Do NOT omit any field.
"""

    from app.utils import get_groq_api_key, get_fallback_llm
    
    import time
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            key = get_groq_api_key()
            llm = get_fallback_llm(api_key=key, temperature=0.0)
            from app.agents.tools.analytics_tools import fetch_live_product_roas
            llm_with_tools = llm.bind_tools([fetch_live_product_roas])
            
            messages = [{"role": "user", "content": prompt}]
            ai_msg = llm_with_tools.invoke(messages)
            
            # Execute tool if requested
            if getattr(ai_msg, "tool_calls", None):
                messages.append(ai_msg)
                for tool_call in ai_msg.tool_calls:
                    if tool_call["name"] == "fetch_live_product_roas":
                        product_id = tool_call["args"].get("product_id", "")
                        tool_res = fetch_live_product_roas.invoke({"product_id": product_id})
                        messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": tool_call["name"], "content": str(tool_res)})
            
            # Now extract the final structured output
            result: MarketingInsights = llm.with_structured_output(MarketingInsights).invoke(messages)
            return {"marketing_insights": result}
        except Exception as e:
            error_str = str(e)
            if attempt < max_retries:
                if "rate_limit_exceeded" in error_str or "429" in error_str:
                    print(f"  ⚠️ [Marketing Agent] Rate limit hit. Sleeping for 5s... (Attempt {attempt+1})")
                    time.sleep(5)
                    continue
                if "tool_use_failed" in error_str or "missing properties" in error_str:
                    print(f"  ⚠️ [Marketing Agent] Retry {attempt + 1}/{max_retries} due to schema error...")
                    time.sleep(2)
                    continue
            print(f"  ❌ [Marketing Agent] Failed after {attempt + 1} attempts: {e}")
            return {"marketing_insights": None}
