import os
import json
from dotenv import load_dotenv

load_dotenv()

from app.agents.graph import engine
from app.agents.state import SystemState

def run_test():
    """
    Integration test for the CommercePulse AI Agent pipeline.
    Uses an empty seller_id so the Orchestrator auto-resolves the real UUID
    from the backend database (single-seller mode).
    """
    print("--- 🤖 CommercePulse AI Integration Test ---")
    
    # seller_id is intentionally empty — the Orchestrator will auto-resolve
    # the first valid seller UUID from the database
    initial_state: SystemState = {
        "seller_id": "",
        "time_window_start": "2026-02-01",
        "time_window_end": "2026-02-15",
        "snapshot_data": {
            "scenario_event": "Test event: Sales dropped by 5%",
            "revenue_metrics": {"conversion_rate_drop_pct": 5.0},
            "operational_metrics": {"avg_delivery_delay_increase_days": 1.0},
            "market_signals": {"recent_reviews_sentiment": "Stable"}
        },
        "product_id": None,
        "revenue_insights": None,
        "ops_insights": None,
        "market_insights": None,
        "marketing_insights": None,
        "final_executive_plan": None,
        "product_analysis": None
    }
    
    try:
        final_state = engine.invoke(initial_state)
        plan = final_state.get("final_executive_plan")
        if plan:
            print("✅ AI Success! Plan generated.")
            print(json.dumps(plan.model_dump(), indent=2, ensure_ascii=False))
        else:
            print("❌ AI Failed: Plan was empty.")
    except Exception as e:
        print(f"❌ AI Error: {e}")

if __name__ == "__main__":
    run_test()
