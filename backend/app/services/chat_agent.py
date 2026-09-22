import os
import logging
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

import json
from decimal import Decimal
from datetime import date, datetime

def _custom_json_encoder(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _build_tools(default_seller_id: str):
    @tool
    async def fetch_live_product_roas(product_id: str) -> str:
        """Fetches live ROAS (Return on Ad Spend) for a specific product."""
        from app.routes.analytics import product_roas
        from app.db.session import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                res = await product_roas(product_id=product_id, db=db)
                return (
                    f"Live ROAS for {product_id} is {res.get('roas', 'unknown')}. "
                    f"Total Spend: {res.get('total_spend', 'unknown')}."
                )
        except Exception as e:
            return f"Could not verify live ROAS due to database error: {str(e)}."

    @tool
    async def fetch_live_product_inventory(product_id: str) -> str:
        """Fetches live inventory count for a specific product."""
        from app.routes.analytics import product_inventory
        from app.db.session import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                res = await product_inventory(product_id=product_id, db=db)
                return f"Live inventory for {product_id} is {res.get('available_stock', 'unknown')} units."
        except Exception as e:
            return f"Could not verify live inventory due to database error: {str(e)}."

    @tool
    async def fetch_product_metrics(product_id: str, seller_id: str = "") -> str:
        """Fetches live revenue, AOV, ROAS, returns, and inventory for one product."""
        from app.routes.analytics import product_metrics_detailed
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await product_metrics_detailed(
                    product_id=product_id, seller_id=sid, db=db, _scope=sid
                )
                return f"Live comprehensive product metrics: {json.dumps(res, default=_custom_json_encoder)}"
        except Exception as e:
            return f"Could not fetch product metrics due to database error: {str(e)}."

    @tool
    async def fetch_all_products_metrics(seller_id: str = "") -> str:
        """Fetches catalog metrics: name, SKU, revenue, orders, ROAS, stock. Use for top products."""
        from app.routes.analytics import products_list
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await products_list(seller_id=sid, db=db, _scope=sid)
                return f"All products metrics: {json.dumps(res.get('data', []), default=_custom_json_encoder)}"
        except Exception as e:
            return f"Could not fetch all products metrics due to database error: {str(e)}."

    @tool
    async def fetch_payments_summary(seller_id: str = "") -> str:
        """Brew Boulevard Razorpay settlements: match rate, unmatched coffee GMV, exceptions. Use for payouts, STL, UTR, MDR, bank credits."""
        from app.routes.payments import latest_summary
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await latest_summary(seller_id=sid, db=db, _scope=sid)
                return f"Payments reconciliation: {json.dumps(res, default=_custom_json_encoder)}"
        except Exception as e:
            return f"Could not fetch payments summary: {str(e)}."

    return [
        fetch_live_product_roas,
        fetch_live_product_inventory,
        fetch_product_metrics,
        fetch_all_products_metrics,
        fetch_payments_summary,
    ]


def _collect_api_keys():
    """Collect Groq keys from Settings (loaded from .env) and process environment."""
    keys = []
    for k in (
        settings.GROQ_API_KEY,
        settings.GROQ_API_KEY_2,
        settings.GROQ_API_KEY_3,
        settings.FALLBACK_GROQ_API_KEY,
        os.getenv("GROQ_API_KEY"),
        os.getenv("GROQ_API_KEY_2"),
        os.getenv("GROQ_API_KEY_3"),
        os.getenv("FALLBACK_GROQ_API_KEY"),
    ):
        if k and k not in keys:
            keys.append(k)
    return keys


class ChatAgentWrapper:
    """
    Adapter providing an .ainvoke interface matching what ai.py expects:
    input dict: {"input": str, "chat_history": list, "context_str": str}
    output dict: {"output": str}
    """
    def __init__(self, agent_runner, system_template: str):
        self.agent_runner = agent_runner
        self.system_template = system_template

    async def ainvoke(self, inputs: dict):
        user_input = inputs.get("input", "")
        chat_history = inputs.get("chat_history", [])
        context_str = inputs.get("context_str", "")

        sys_text = self.system_template.replace("{context_str}", context_str)
        messages = [SystemMessage(content=sys_text)] + list(chat_history) + [HumanMessage(content=user_input)]

        res = await self.agent_runner.ainvoke({"messages": messages})
        final_msg = res["messages"][-1]
        output_text = final_msg.content if hasattr(final_msg, "content") else str(final_msg)
        if isinstance(output_text, list):
            output_text = "".join(
                (p.get("text", "") if isinstance(p, dict) else str(p)) for p in output_text
            )
        return {"output": output_text}


def get_chat_agent(seller_id: str = ""):
    api_keys = _collect_api_keys()
    if not api_keys:
        raise ValueError("No Groq API keys found. Set GROQ_API_KEY in backend/.env.")

    primary_model = settings.GROQ_CHAT_MODEL or "llama-3.1-8b-instant"
    primary_key = api_keys[0]

    primary_llm = ChatGroq(
        api_key=primary_key,
        model=primary_model,
        temperature=0.2,
        max_tokens=700,
    )

    tools = _build_tools(seller_id)

    system_prompt = """You are an elite, highly aggressive Senior Business Analyst & Strategist for a D2C brand named "Brew Boulevard". 
Your job is to answer the user's questions strictly based on their real data.
Be concise, highly professional, use bullet points if needed, and reference actual Rs amounts, percentages, and units.

Here is the LIVE DATA context for Brew Boulevard:
{context_str}

If the user asks about a specific product, and you have its product_id, USE YOUR TOOLS to fetch live metrics, inventory, or ROAS for it before answering.

Rules:
1. Do not hallucinate metrics. Assume the LIVE DATA provided is the most current and relevant data for the user's query.
2. Be aggressive about growth and protecting margins. Focus on profitability, ROAS optimization, and high-impact actions.
3. Keep responses under 200 words unless explaining a complex multi-step strategy.
4. Always reference actual financial numbers (Rs amounts) to back up your claims.
5. Provide extremely actionable, data-driven advice for D2C scaling.
6. If the user asks about a specific product, USE your `fetch_product_metrics` tool to get the full picture, do NOT just guess.
If the user asks about payouts, Razorpay, settlements, UTR, STL batches, MDR, GST on fees, unmatched cash, or bank credits, USE `fetch_payments_summary`.
8. If the user asks about overall product metrics, top selling products, or general catalog queries, USE the `fetch_all_products_metrics` tool to get the full product catalog metrics before answering. Use the Seller ID from the context.
"""

    try:
        agent = create_agent(model=primary_llm, tools=tools)
    except TypeError:
        agent = create_agent(primary_llm, tools)
    except Exception:
        logger.exception("create_agent failed")
        raise
    return ChatAgentWrapper(agent, system_prompt)
