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


def _to_json(payload, limit: int | None = None) -> str:
    data = payload
    if isinstance(payload, dict):
        data = dict(payload)
        for key in ("data", "alerts"):
            if isinstance(data.get(key), list) and limit:
                data[key] = data[key][:limit]
    elif isinstance(payload, list) and limit:
        data = payload[:limit]
    return json.dumps(data, default=_custom_json_encoder)


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
        """Razorpay settlements: match rate, unmatched GMV, exceptions. Use for payouts, STL, UTR, MDR, bank credits."""
        from app.routes.payments import latest_summary
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await latest_summary(seller_id=sid, db=db, _scope=sid)
                return f"Payments reconciliation: {_to_json(res)}"
        except Exception as e:
            return f"Could not fetch payments summary: {str(e)}."

    @tool
    async def fetch_dashboard_kpis(seller_id: str = "") -> str:
        """Overall KPIs: revenue, orders, cancellations, returns, low stock, RTO, ROAS. Use for overview / how is business doing."""
        from app.routes.analytics import dashboard
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await dashboard(seller_id=sid, days=30, db=db, _scope=sid)
                return f"Dashboard KPIs: {_to_json(res)}"
        except Exception as e:
            return f"Could not fetch dashboard KPIs: {str(e)}."

    @tool
    async def fetch_revenue_by_marketplace(seller_id: str = "") -> str:
        """Revenue, orders, AOV, discounts by marketplace. Use for channel mix and revenue trend questions."""
        from app.routes.analytics import revenue_summary
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await revenue_summary(seller_id=sid, days=30, db=db, _scope=sid)
                return f"Revenue by marketplace: {_to_json(res)}"
        except Exception as e:
            return f"Could not fetch revenue: {str(e)}."

    @tool
    async def fetch_inventory_alerts(seller_id: str = "") -> str:
        """Low-stock and stockout SKUs. Use for inventory, reorder, stockout questions."""
        from app.routes.analytics import inventory_alerts
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await inventory_alerts(seller_id=sid, db=db, _scope=sid)
                return f"Inventory alerts: {_to_json(res, limit=20)}"
        except Exception as e:
            return f"Could not fetch inventory alerts: {str(e)}."

    @tool
    async def fetch_ad_performance(seller_id: str = "") -> str:
        """Ads funnel: impressions, CTR, conversion, ad spend, ROAS by SKU. Use for ads, ROAS, marketing spend."""
        from app.routes.analytics import traffic_funnel
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await traffic_funnel(seller_id=sid, days=30, db=db, _scope=sid)
                return f"Ad / traffic performance: {_to_json(res, limit=20)}"
        except Exception as e:
            return f"Could not fetch ad performance: {str(e)}."

    @tool
    async def fetch_logistics_performance(seller_id: str = "") -> str:
        """RTO rate, delivery counts, shipping days by marketplace. Use for logistics, RTO, delivery SLAs."""
        from app.routes.analytics import logistics_rto_rate
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await logistics_rto_rate(seller_id=sid, days=30, db=db, _scope=sid)
                return f"Logistics / RTO: {_to_json(res)}"
        except Exception as e:
            return f"Could not fetch logistics: {str(e)}."

    @tool
    async def fetch_top_customers(seller_id: str = "") -> str:
        """Top customers by spend. Use for customers, repeat buyers, VIP accounts."""
        from app.routes.analytics import customers_summary
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await customers_summary(seller_id=sid, limit=15, db=db, _scope=sid)
                return f"Top customers: {_to_json(res, limit=15)}"
        except Exception as e:
            return f"Could not fetch customers: {str(e)}."

    @tool
    async def fetch_pricing_margins(seller_id: str = "") -> str:
        """Selling price, cost, commission, margin % by SKU. Use for margin, pricing, profitability."""
        from app.routes.analytics import pricing_margins
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await pricing_margins(seller_id=sid, db=db, _scope=sid)
                return f"Pricing / margins: {_to_json(res, limit=20)}"
        except Exception as e:
            return f"Could not fetch margins: {str(e)}."

    return [
        fetch_live_product_roas,
        fetch_live_product_inventory,
        fetch_product_metrics,
        fetch_all_products_metrics,
        fetch_payments_summary,
        fetch_dashboard_kpis,
        fetch_revenue_by_marketplace,
        fetch_inventory_alerts,
        fetch_ad_performance,
        fetch_logistics_performance,
        fetch_top_customers,
        fetch_pricing_margins,
    ]


# Groq retired several Llama 3.x models; remap stale .env values automatically.
_DEPRECATED_GROQ_MODELS = {
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
}


def _resolve_groq_model(preferred: str, default: str) -> str:
    model = (preferred or "").strip() or default
    if model in _DEPRECATED_GROQ_MODELS:
        return default
    return model


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

    primary_model = _resolve_groq_model(settings.GROQ_CHAT_MODEL, "openai/gpt-oss-20b")
    fallback_model = _resolve_groq_model(settings.GROQ_FALLBACK_MODEL, "openai/gpt-oss-120b")
    primary_key = api_keys[0]
    fallback_key = api_keys[1] if len(api_keys) > 1 else primary_key

    primary_llm = ChatGroq(
        api_key=primary_key,
        model=primary_model,
        temperature=0.2,
        max_tokens=700,
    )
    fallback_llm = ChatGroq(
        api_key=fallback_key,
        model=fallback_model,
        temperature=0.2,
        max_tokens=700,
    )
    llm = primary_llm.with_fallbacks([fallback_llm])

    tools = _build_tools(seller_id)

    system_prompt = """You are the Brew Boulevard AI Business Analyst. Answer EVERY business question using live tools plus the snapshot below. Never say you cannot access data if a tool exists.

LIVE SNAPSHOT:
{context_str}

Always pick the right tool before answering (you may call more than one):
- Overview / how is business / KPIs → fetch_dashboard_kpis
- Revenue / marketplace split / AOV → fetch_revenue_by_marketplace
- Top products / SKU performance → fetch_all_products_metrics
- One product (name, SKU, or product_id) → fetch_product_metrics
- Inventory / low stock / stockouts → fetch_inventory_alerts
- Ads / ROAS / spend / CTR → fetch_ad_performance
- Logistics / RTO / delivery days → fetch_logistics_performance
- Customers / top buyers → fetch_top_customers
- Margins / pricing / profitability → fetch_pricing_margins
- Payouts / Razorpay / settlements / UTR / MDR / unmatched cash → fetch_payments_summary

Rules:
1. Never invent numbers. If a tool returns empty, say so and suggest Data Import.
2. Quote rupees, units, and percentages from the tool results.
3. Keep answers under 180 words with bullets and one recommended action.
4. If the question is unclear, still answer with dashboard KPIs and ask a short follow-up.
"""

    try:
        agent = create_agent(model=llm, tools=tools)
    except TypeError:
        agent = create_agent(llm, tools)
    except Exception:
        logger.exception("create_agent failed")
        raise
    return ChatAgentWrapper(agent, system_prompt)
