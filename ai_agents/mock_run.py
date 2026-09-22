import os
import json
from dotenv import load_dotenv

# Ensure we're reading environmental variables (.env in ai_agents dir)
load_dotenv()

from app.agents.graph import engine
from app.agents.state import SystemState

def run_simulation():
    """
    Simulates the "Competitor drops price by 8%" scenario as described in the architecture plan.
    """
    print("================================================")
    print("🚀 COMMERCEPULSE: INITIALIZING SIMULATION")
    print("================================================")
    
    # Check if Groq API key exists, otherwise agents will fail
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY is not set in the environment.")
        print("Please create a .env file in AZURE/ai_agents/ with your free Groq key.")
        return
        
    print("✅ API Key found. Building mock state...\n")
    
    # Step 1: Mock State (The "Data Snapshot")
    initial_state: SystemState = {
        "seller_id": "d3b07384-d990-4493-9c9c-567035467c64",
        "time_window_start": "2026-02-01",
        "time_window_end": "2026-02-15",
        "snapshot_data": {
            "scenario_event": "Competitor 'TechZone' dropped iPhone 15 prices by 8%.",
            "revenue_metrics": {
                "conversion_rate_drop_pct": 6.0,
                "estimated_revenue_loss_inr": 120000,
                "top_affected_sku": "SKU44-IPHONE15-128GB",
                "price_sensitivity": "High",
                "gross_margin_pct": 18.0
            },
            "operational_metrics": {
                "avg_delivery_delay_increase_days": 2.0,
                "return_rate_increase_pct": 12.0,
                "problematic_warehouse": "BLR-01"
            },
            "market_signals": {
                "recent_reviews_sentiment": "Negative spike",
                "primary_complaint_topic": "Delivery delays and high price compared to TechZone",
                "traffic_volume": "Stable",
                "conversion_volume": "Dropping"
            }
        },
        "product_id": None,
        "revenue_insights": None,
        "ops_insights": None,
        "market_insights": None,
        "marketing_insights": None,
        "final_executive_plan": None,
        "product_analysis": None
    }

    # Step 2: Execute Graph
    print("Starting LangGraph execution... (This triggers the 5 Agents)\n")
    
    # The compiled graph accepts a state and returns the final state
    # We use `invoke` to run it synchronously for simulation purposes
    try:
        final_state = engine.invoke(initial_state)
        
        # Step 3: Print Output
        print("\n================================================")
        print("🎯 FINAL EXECUTIVE ACTION PLAN (Synthesizer Output)")
        print("================================================\n")
        
        plan = final_state.get("final_executive_plan")
        if plan:
            # Pretty print the Pydantic model
            print(plan.model_dump_json(indent=2))
        else:
            print("❌ Graph completed, but no Executive Plan was generated.")
            
    except Exception as e:
        print(f"\n❌ Execution failed: {str(e)}")

if __name__ == "__main__":
    run_simulation()
