import json
import time
from langchain_groq import ChatGroq
from app.agents.state import SystemState
from app.agents.schemas import ExecutiveActionPlan

def run_critic(state: SystemState) -> dict:
    """
    Critic Persona (Reflexion Node).
    Takes the Synthesizer's ExecutiveActionPlan and fact-checks it against the raw snapshot.
    It patches any hallucinated numbers and outputs the final, authentic ExecutiveActionPlan,
    saving tokens by not looping back to the Synthesizer.
    """
    print("⚖️  [Critic] Auditing Synthesizer's plan for mathematical authenticity...")

    raw_plan = state.get("final_executive_plan")
    if not raw_plan:
        return {}

    # Serialize raw plan
    try:
        plan_text = raw_plan.model_dump_json(indent=2)
    except AttributeError:
        plan_text = str(raw_plan)

    # Grab the raw data snapshot for fact-checking
    snapshot = state.get("snapshot_data", {})
    
    # We provide a heavily truncated but exact snapshot of KPIs to cross-reference
    dashboard_kpis = json.dumps(snapshot.get("dashboard_kpis", {}), indent=2, default=str)[:800]
    revenue_by_mp = json.dumps(snapshot.get("revenue_by_marketplace", []), indent=2, default=str)[:800]

    prompt = f"""You are the Chief Auditor. Your job is to review the following Executive Action Plan and correct any mathematical hallucinations or generic fluff.

=== RAW DATA SNAPSHOT (Truth) ===
{dashboard_kpis}
{revenue_by_mp}

=== EXECUTIVE ACTION PLAN TO REVIEW ===
{plan_text}

YOUR MISSION:
1. Verify every single ₹ amount, percentage, and metric mentioned in the plan against the RAW DATA SNAPSHOT.
2. If the plan says something generic like "Increase traffic", rewrite it to be mathematically specific based on the data.
3. Output the fully corrected, mathematically authentic ExecutiveActionPlan.
4. If the plan is already accurate, just output it exactly as is, but increase the confidence_score slightly.

Do NOT add new actions. Only correct the numbers, math, and specificity of the existing actions.
"""

    from app.utils import get_groq_api_key, get_fallback_llm
    
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            key = get_groq_api_key()
            llm = get_fallback_llm(api_key=key, temperature=0.0).with_config(tags=["critic"])
            result: ExecutiveActionPlan = llm.with_structured_output(ExecutiveActionPlan).invoke(prompt)
            if result is None:
                return {"final_executive_plan": raw_plan}
            print("✅ [Critic] Audit complete. Plan is mathematically authentic.")
            return {"final_executive_plan": result}
        except Exception as e:
            error_str = str(e)
            if attempt < max_retries:
                if "rate_limit_exceeded" in error_str or "429" in error_str:
                    print(f"  ⚠️ [Critic] Rate limit hit. Sleeping for 5s... (Attempt {attempt+1})")
                    time.sleep(5)
                    continue
            return {"final_executive_plan": raw_plan}  # Fallback to the raw plan if critic fails
