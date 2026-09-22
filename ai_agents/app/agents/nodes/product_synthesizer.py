import os
import json
from langchain_groq import ChatGroq
from app.agents.state import SystemState
from app.agents.schemas import ProductAnalysisResult

def run_product_synthesizer(state: SystemState) -> dict:
    """
    Synthesizer Node for Per-Product Analysis.
    Takes insights from all domain agents and synthesizes them into a final product report.
    """
    print("🧠 [Product Synthesizer] Compiling per-product executive summary...")
    
    product_id = state.get("product_id")
    raw_snapshot = state.get("snapshot_data", {})
    
    # Extract domain insights
    rev_insights = state.get("revenue_insights")
    ops_insights = state.get("ops_insights")
    marketing_insights = state.get("marketing_insights")
    market_insights = state.get("market_insights")
    
    def model_to_json(model_obj):
        if not model_obj: return "None"
        try:
            if hasattr(model_obj, "model_dump_json"):
                return model_obj.model_dump_json(indent=2)
            else:
                return str(model_obj)
        except Exception:
            return str(model_obj)
    
    prompt = f"""
You are a senior business strategist hired by the seller to give a brutally honest product performance review.
Your analysis will be read by the seller (a small D2C business owner). They need ACTIONABLE intelligence, not generic MBA-speak.

=== FULL PRODUCT DATA ===

PRODUCT IDENTITY:
{json.dumps(raw_snapshot.get('product_identity', {}), indent=2, default=str)[:800]}

PROFIT & LOSS STATEMENT:
{json.dumps(raw_snapshot.get('profit_and_loss', {}), indent=2, default=str)[:800]}

PRICING BY MARKETPLACE (per-unit economics per channel):
{json.dumps(raw_snapshot.get('pricing_by_marketplace', []), indent=2, default=str)[:800]}

REVENUE SPLIT BY MARKETPLACE:
{json.dumps(raw_snapshot.get('revenue_by_marketplace', []), indent=2, default=str)[:800]}

ADVERTISING PERFORMANCE (Paid Acquisition):
{json.dumps(raw_snapshot.get('advertising_performance', {}), indent=2, default=str)[:800]}

INVENTORY HEALTH:
{json.dumps(raw_snapshot.get('inventory_health', {}), indent=2, default=str)[:800]}

LOGISTICS & DELIVERY QUALITY:
{json.dumps(raw_snapshot.get('logistics_quality', {}), indent=2, default=str)[:800]}

=== DEPARTMENT HEAD REPORTS ===
[CFO / Revenue Report]:
{model_to_json(rev_insights)}

[COO / Operations Report]:
{model_to_json(ops_insights)}

[CMO / Marketing Report]:
{model_to_json(marketing_insights)}

[Brand Strategist Report]:
{model_to_json(market_insights)}

Use the product data above as the source of truth. Department reports may be empty — still produce a complete analysis from the P&L, ads, inventory, and marketplace splits.

=== YOUR ANALYSIS TASKS ===
You MUST analyze the data like a real business owner looking at their own P&L:

1. PRODUCT HEALTH SCORE (0-100):
   - Calculate based on: margin health (is net profit per unit good?), ad efficiency (ROAS > 3?), return rate (< 5% good), inventory velocity (days_of_stock < 60 good), channel diversification.

2. PRIMARY OBSERVATION: One hard-hitting sentence. Reference actual numbers. Example: "This product generates Rs 1.5L revenue but 40% of orders are discounted, eroding Rs 20K in potential margin monthly."

3. STRENGTHS (2-3 items): What's genuinely working? 
   - Fill out the structured SWOTItem fields.
   - `title`: Short headline.
   - `detail`: 2-3 sentence explanation citing ACTUAL NUMBERS from the P&L and pricing data.
   - `impact`: 'High', 'Medium', or 'Low'.
   - `metric_value`: The key metric (e.g. 'ROAS: 4.79' or 'Margin: 52%').

4. WEAKNESSES (2-3 items): Where is money leaking? Be specific.
   - Fill out the structured SWOTItem fields.
   - Identify a specific financial leak. The `detail` MUST include the Rs amount being lost and the marketplace where it's happening.

5. ROOT CAUSES (2-3 items): WHY do the weaknesses exist? These MUST be different from weaknesses.
   - Fill out the structured RootCauseItem fields.
   - `linked_weakness`: You MUST reference the title of the specific weakness this root cause explains.
   - `cause`: Explain the deep systemic reason (e.g., 'Platform commission of 15% combined with 10% mandatory discount makes the Rs 499 selling price yield only Rs 167 net profit').
   - `evidence`: The specific data calculation that proves this cause.

6. CROSS MARKETPLACE SUMMARY: Compare channels head-to-head. Which marketplace should get more budget? Which should be cut? Use the per-marketplace revenue and pricing data.

7. RECOMMENDATIONS: Give 2-4 concrete actions the seller can take THIS WEEK. Each must include:
   - Exactly what to do and on which marketplace
   - The financial impact (use actual numbers from the data)
   - Why it's safe or risky

CRITICAL RULES:
- Reference actual numbers from the data (Rs values, percentages, units).
- Do NOT repeat the same insight in multiple sections.
- Think like a seller counting every rupee, not a consultant writing a report.
"""

    import time
    from app.agents.schemas import ProductAnalysisResult
    from app.utils import get_groq_api_key
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            key = get_groq_api_key()
            from app.utils import get_fallback_llm
            llm = get_fallback_llm(api_key=key, temperature=0.1)
            structured_llm = llm.with_structured_output(ProductAnalysisResult)
            
            result = structured_llm.invoke(prompt)
            print("✅ [Product Synthesizer] Analysis complete.")
            return {"product_analysis": result}
        except Exception as e:
            print(f"Error in Product Synthesizer (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            print(f"Product Synthesizer failed after {max_retries} attempts.")
            raise
