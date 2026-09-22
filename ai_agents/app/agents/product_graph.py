from langgraph.graph import StateGraph, END
from app.agents.state import SystemState
from app.agents.nodes.product_orchestrator import run_product_orchestrator
from app.agents.nodes.product_synthesizer import run_product_synthesizer

def build_product_analysis_engine():
    """
    Per-product analysis. Backend already attaches live KPIs; one Groq pass
    is enough. The old 5-agent chain took 2+ minutes per product.
    """
    workflow = StateGraph(SystemState)
    workflow.add_node("product_orchestrator", run_product_orchestrator)
    workflow.add_node("product_synthesizer", run_product_synthesizer)
    workflow.set_entry_point("product_orchestrator")
    workflow.add_edge("product_orchestrator", "product_synthesizer")
    workflow.add_edge("product_synthesizer", END)
    return workflow.compile()
