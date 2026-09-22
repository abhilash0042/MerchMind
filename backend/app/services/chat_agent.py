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

    @tool
    async def fetch_orders_stats(seller_id: str = "") -> str:
        """Order counts by status (pending, shipped, delivered, cancelled). Use for order pipeline questions."""
        from app.routes.analytics import orders_stats
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await orders_stats(seller_id=sid, days=30, db=db, _scope=sid)
                return f"Order stats: {_to_json(res)}"
        except Exception as e:
            return f"Could not fetch order stats: {str(e)}."

    @tool
    async def fetch_revenue_by_category(seller_id: str = "") -> str:
        """Revenue grouped by product category. Use for category mix / which categories sell best."""
        from app.routes.analytics import revenue_by_category
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                res = await revenue_by_category(seller_id=sid, days=30, db=db, _scope=sid)
                return f"Revenue by category: {_to_json(res)}"
        except Exception as e:
            return f"Could not fetch category revenue: {str(e)}."

    @tool
    async def fetch_business_overview(seller_id: str = "") -> str:
        """Catch-all for any business question. Returns KPIs, marketplace revenue, inventory alerts, and ads ROAS."""
        from app.routes.analytics import dashboard, revenue_summary, inventory_alerts, traffic_funnel
        from app.db.session import AsyncSessionLocal
        sid = seller_id or default_seller_id
        try:
            async with AsyncSessionLocal() as db:
                kpis = await dashboard(seller_id=sid, days=30, db=db, _scope=sid)
                revenue = await revenue_summary(seller_id=sid, days=30, db=db, _scope=sid)
                inventory = await inventory_alerts(seller_id=sid, db=db, _scope=sid)
                ads = await traffic_funnel(seller_id=sid, days=30, db=db, _scope=sid)
            payload = {
                "kpis": kpis,
                "revenue": revenue,
                "inventory_alerts": inventory,
                "ads": ads,
            }
            return "Business overview: " + _to_json(payload, limit=12)
        except Exception as e:
            return f"Could not fetch business overview: {str(e)}."

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
        fetch_orders_stats,
        fetch_revenue_by_category,
        fetch_business_overview,
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


def _openrouter_key() -> str:
    return (settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY") or "").strip()


def _build_openrouter_llm(or_key: str):
    from langchain_openai import ChatOpenAI

    headers = {
        "HTTP-Referer": "http://127.0.0.1:4000",
        "X-Title": "CommercePulse AI Assistant",
    }
    primary_model = (settings.OPENROUTER_CHAT_MODEL or "openai/gpt-4o-mini").strip()
    fallback_model = (settings.OPENROUTER_FALLBACK_MODEL or "google/gemini-2.0-flash-001").strip()
    models = [primary_model]
    if fallback_model and fallback_model not in models:
        models.append(fallback_model)
    return [
        ChatOpenAI(
            model=model,
            api_key=or_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
            max_tokens=1600,
            default_headers=headers,
        )
        for model in models
    ]


def _build_groq_llms():
    api_keys = _collect_api_keys()
    if not api_keys:
        return []
    primary_model = _resolve_groq_model(settings.GROQ_CHAT_MODEL, "openai/gpt-oss-20b")
    fallback_model = _resolve_groq_model(settings.GROQ_FALLBACK_MODEL, "openai/gpt-oss-120b")
    llms = [
        ChatGroq(
            api_key=api_keys[0],
            model=primary_model,
            temperature=0.2,
            max_tokens=1200,
        )
    ]
    second_key = api_keys[1] if len(api_keys) > 1 else api_keys[0]
    if fallback_model != primary_model or second_key != api_keys[0]:
        llms.append(
            ChatGroq(
                api_key=second_key,
                model=fallback_model,
                temperature=0.2,
                max_tokens=1200,
            )
        )
    return llms


_skip_openrouter = False


def _is_quota_error(exc: Exception) -> bool:
    s = str(exc).lower()
    return any(
        token in s
        for token in (
            "key limit exceeded",
            "insufficient credits",
            "status code 403",
            "error code: 403",
            "rate limit",
            "429",
        )
    )


def _make_agent(llm, tools):
    try:
        return create_agent(model=llm, tools=tools)
    except TypeError:
        return create_agent(llm, tools)


class ChatAgentWrapper:
    """
    Adapter providing an .ainvoke interface matching what ai.py expects:
    input dict: {"input": str, "chat_history": list, "context_str": str}
    output dict: {"output": str}
    """
    def __init__(self, agent_runner, system_template: str, fallback_runner=None):
        self.agent_runner = agent_runner
        self.fallback_runner = fallback_runner
        self.system_template = system_template

    async def _run(self, runner, inputs: dict):
        user_input = inputs.get("input", "")
        chat_history = inputs.get("chat_history", [])
        context_str = inputs.get("context_str", "")

        sys_text = self.system_template.replace("{context_str}", context_str)
        messages = [SystemMessage(content=sys_text)] + list(chat_history) + [HumanMessage(content=user_input)]

        res = await runner.ainvoke({"messages": messages})
        final_msg = res["messages"][-1]
        output_text = final_msg.content if hasattr(final_msg, "content") else str(final_msg)
        if isinstance(output_text, list):
            output_text = "".join(
                (p.get("text", "") if isinstance(p, dict) else str(p)) for p in output_text
            )
        return {"output": output_text}

    async def ainvoke(self, inputs: dict):
        global _skip_openrouter
        try:
            return await self._run(self.agent_runner, inputs)
        except Exception as exc:
            if self.fallback_runner and _is_quota_error(exc):
                logger.warning("Primary chat LLM failed (%s); retrying on Groq", exc)
                _skip_openrouter = True
                return await self._run(self.fallback_runner, inputs)
            raise


def get_chat_agent(seller_id: str = ""):
    tools = _build_tools(seller_id)
    groq_llms = _build_groq_llms()
    groq_llm = None
    if groq_llms:
        groq_llm = groq_llms[0] if len(groq_llms) == 1 else groq_llms[0].with_fallbacks(groq_llms[1:])

    system_prompt = """You are CommercePulse, a senior ecommerce business analyst for this seller. You MUST answer every business question with live numbers from tools. Never refuse a commerce question. Never say you cannot access data if a tool exists.

LIVE SNAPSHOT:
{context_str}

Tool routing (call one or more before answering):
- Unsure / general / "how is business" / strategy → fetch_business_overview
- KPIs / revenue / orders / cancellations / returns → fetch_dashboard_kpis
- Order pipeline / pending / delivered / cancelled counts → fetch_orders_stats
- Marketplace split / AOV / channel mix → fetch_revenue_by_marketplace
- Category mix → fetch_revenue_by_category
- Top products / SKU ranking → fetch_all_products_metrics
- One product (name, SKU, or product_id) → fetch_product_metrics
- Inventory / low stock / stockouts / reorder → fetch_inventory_alerts
- Ads / ROAS / spend / CTR / marketing → fetch_ad_performance
- Logistics / RTO / delivery days / shipping → fetch_logistics_performance
- Customers / top buyers / VIP → fetch_top_customers
- Margins / pricing / profitability → fetch_pricing_margins
- Payouts / Razorpay / settlements / UTR / MDR / unmatched cash → fetch_payments_summary

Rules:
1. Always call at least one tool. If the question is vague, call fetch_business_overview.
2. Never invent numbers. If a tool is empty, say the dataset has no rows for that window and suggest Data Import.
3. Quote ₹ amounts, units, and percentages from tool results. Name marketplaces and SKUs.
4. Keep answers under 220 words: 3–6 bullets, then one recommended next action.
5. For strategy / what-if questions, ground advice in the live metrics, then give a practical action.
6. If the user asks something non-business, briefly redirect and still offer a KPI snapshot.
"""

    or_key = _openrouter_key()
    use_openrouter = (not _skip_openrouter) and or_key.startswith("sk-or-")

    groq_agent = _make_agent(groq_llm, tools) if groq_llm is not None else None

    if use_openrouter:
        or_llms = _build_openrouter_llm(or_key)
        or_llm = or_llms[0] if len(or_llms) == 1 else or_llms[0].with_fallbacks(or_llms[1:])
        return ChatAgentWrapper(_make_agent(or_llm, tools), system_prompt, groq_agent)

    if groq_agent is None:
        raise ValueError(
            "No chat API key found. Set OPENROUTER_API_KEY (sk-or-...) or GROQ_API_KEY in backend/.env."
        )
    return ChatAgentWrapper(groq_agent, system_prompt)
