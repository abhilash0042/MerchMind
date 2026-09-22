from langgraph.graph import StateGraph, END
from app.agents.state import SystemState
from app.agents.nodes.orchestrator import run_orchestrator
from app.agents.nodes.synthesizer import run_synthesizer

def build_commerce_pulse_engine():
    """
    Fetch live analytics, then one synthesizer pass.
    Domain agents + critic were 6 sequential Groq calls (~2.5 min).
    """
    workflow = StateGraph(SystemState)
    workflow.add_node("orchestrator", run_orchestrator)
    workflow.add_node("synthesizer", run_synthesizer)
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "synthesizer")
    workflow.add_edge("synthesizer", END)
    return workflow.compile()

engine = build_commerce_pulse_engine()
