import os
import sys
import io

# ── Force UTF-8 encoding on Windows (cp1252 can't handle emoji chars) ──
# This must happen BEFORE any other imports that might print unicode.
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from dotenv import load_dotenv

# Ensure environment variables (.env) are loaded (agents dir, then backend as local fallback)
from pathlib import Path as _Path
_here = _Path(__file__).resolve().parent
load_dotenv(_here / ".env")
load_dotenv(_here.parent / "backend" / ".env")


from app.agents.graph import engine
from app.agents.state import SystemState

app = FastAPI(
    title="CommercePulse AI Agents API",
    description="REST API for triggering the multi-agent LangGraph workflows."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "online", "service": "AI Agents", "engine": "LangGraph"}

class SimulationRequest(BaseModel):
    seller_id: str
    time_window_start: str
    time_window_end: str
    snapshot_data: Dict[str, Any]

@app.post("/api/v1/simulate")
async def run_simulation(request: SimulationRequest):
    """
    Executes the 5-Agent LangGraph scenario based on standard JSON input.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")
        
    initial_state: SystemState = {
        "seller_id": request.seller_id,
        "time_window_start": request.time_window_start,
        "time_window_end": request.time_window_end,
        "snapshot_data": request.snapshot_data,
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
        
        # Extract the Pydantic plan object output from the Synthesizer
        plan = final_state.get("final_executive_plan")
        if plan:
            if hasattr(plan, "model_dump"):
                plan_data = plan.model_dump()
            elif hasattr(plan, "dict"):
                plan_data = plan.dict()
            else:
                plan_data = plan

            return {
                "status": "success", 
                "seller_id": request.seller_id,
                "executive_plan": plan_data
            }
        else:
            return {"status": "partial", "message": "Graph completed but no executive plan was generated."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/simulate/stream")
async def run_simulation_stream(request: SimulationRequest):
    """
    Executes the 5-Agent LangGraph scenario and streams the output from the Synthesizer.
    """
    from fastapi.responses import StreamingResponse
    import json
    
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")
        
    initial_state: SystemState = {
        "seller_id": request.seller_id,
        "time_window_start": request.time_window_start,
        "time_window_end": request.time_window_end,
        "snapshot_data": request.snapshot_data,
        "product_id": None,
        "revenue_insights": None,
        "ops_insights": None,
        "market_insights": None,
        "marketing_insights": None,
        "final_executive_plan": None,
        "product_analysis": None
    }
    
    async def generate():
        # Using astreams to get streaming events from langgraph
        try:
            async for event in engine.astream_events(initial_state, version="v2"):
                # We specifically want to stream the chat model tokens from the synthesizer node
                if event["event"] == "on_chat_model_stream":
                    # Check if this event came from our synthesizer node
                    tags = event.get("tags", [])
                    if "synthesizer" in tags or event["name"] == "ChatGroq":
                        chunk = event["data"]["chunk"]
                        if chunk.content:
                            yield f"data: {json.dumps({'content': chunk.content})}\n\n"
                            
            # Send a final 'done' event
            yield f"data: {json.dumps({'status': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(generate(), media_type="text/event-stream")

class WhatIfRequest(BaseModel):
    seller_id: str
    scenario: str

@app.post("/api/v1/simulate/whatif")
async def run_whatif_stream(request: WhatIfRequest):
    """
    Executes a custom 'What-If' hypothetical scenario and streams the output from the Synthesizer.
    This bypasses standard automated snapshot triggers.
    """
    from fastapi.responses import StreamingResponse
    from datetime import date as _date, timedelta
    import json
    
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")
        
    today = _date.today()
    # Create the state with the custom scenario injected into snapshot data
    initial_state: SystemState = {
        "seller_id": request.seller_id,
        "time_window_start": str(today - timedelta(days=7)),
        "time_window_end": str(today),
        "snapshot_data": {"user_hypothetical_scenario": request.scenario},
        "revenue_insights": None,
        "ops_insights": None,
        "market_insights": None,
        "marketing_insights": None,
        "final_executive_plan": None,
        "product_id": None,
        "product_analysis": None
    }
    
    async def generate():
        try:
            async for event in engine.astream_events(initial_state, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    tags = event.get("tags", [])
                    if "synthesizer" in tags or event["name"] == "ChatGroq":
                        chunk = event["data"]["chunk"]
                        if chunk.content:
                            yield f"data: {json.dumps({'content': chunk.content})}\n\n"
            yield f"data: {json.dumps({'status': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(generate(), media_type="text/event-stream")

from app.agents.product_graph import build_product_analysis_engine
product_engine = build_product_analysis_engine()

class ProductAnalysisRequest(BaseModel):
    seller_id: str
    product_id: str
    product_data: Dict[str, Any]

@app.post("/api/v1/analyze/product")
async def analyze_product(request: ProductAnalysisRequest):
    """
    Executes the Per-Product LangGraph scenario.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set.")
        
    initial_state: SystemState = {
        "seller_id": request.seller_id,
        "product_id": request.product_id,
        "time_window_start": "",
        "time_window_end": "",
        "snapshot_data": request.product_data,
        "revenue_insights": None,
        "ops_insights": None,
        "market_insights": None,
        "marketing_insights": None,
        "final_executive_plan": None,
        "product_analysis": None
    }
    
    try:
        final_state = product_engine.invoke(initial_state)
        
        # Extract the ProductAnalysisResult object
        analysis = final_state.get("product_analysis")
        if analysis:
            if hasattr(analysis, "model_dump"):
                analysis_data = analysis.model_dump()
            elif hasattr(analysis, "dict"):
                analysis_data = analysis.dict()
            else:
                analysis_data = analysis

            return {
                "status": "success", 
                "product_id": request.product_id,
                "result": analysis_data
            }
        else:
            return {"status": "partial", "message": "Graph completed but no product analysis was generated."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Can run this file directly via `python main.py`
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8002")))
