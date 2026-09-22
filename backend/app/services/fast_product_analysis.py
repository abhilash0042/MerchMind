"""Instant product analysis from live KPIs. Optional short Groq polish."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _f(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def build_product_analysis(product_data: dict) -> dict:
    name = product_data.get("product_name") or product_data.get("sku") or "This product"
    sku = product_data.get("sku") or ""
    revenue = _f(product_data.get("total_revenue"))
    orders = _f(product_data.get("total_orders"))
    returns = _f(product_data.get("total_returns"))
    return_rate = _f(product_data.get("return_rate_pct"))
    roas = _f(product_data.get("roas"))
    ad_spend = _f(product_data.get("total_ad_spend"))
    stock = _f(product_data.get("stock_level"))
    reorder = _f(product_data.get("reorder_threshold"))
    days_stock = _f(product_data.get("days_of_stock"))
    discount = _f(product_data.get("total_discount_given"))

    pricing = product_data.get("pricing_by_marketplace") or []
    margins = [_f(p.get("margin_pct")) for p in pricing if p.get("margin_pct") is not None]
    avg_margin = sum(margins) / len(margins) if margins else 0.0
    best_mp = None
    if pricing:
        best_mp = max(pricing, key=lambda p: _f(p.get("margin_pct")))

    score = 50.0
    if avg_margin >= 30:
        score += 15
    elif avg_margin >= 15:
        score += 8
    elif avg_margin < 10:
        score -= 15
    if roas >= 3:
        score += 12
    elif ad_spend > 0 and roas < 1.5:
        score -= 12
    if return_rate <= 5:
        score += 8
    elif return_rate >= 15:
        score -= 12
    if reorder and stock <= reorder:
        score -= 10
    if revenue <= 0:
        score -= 10
    score = max(5.0, min(95.0, round(score, 1)))

    if score >= 80:
        verdict = "Strong Performer"
    elif score >= 50:
        verdict = "Growth Opportunity"
    elif revenue <= 0:
        verdict = "Needs Review"
    else:
        verdict = "At Risk"

    strengths = []
    if avg_margin >= 20:
        strengths.append({
            "title": "Healthy unit economics",
            "detail": f"{name} averages {avg_margin:.1f}% margin after cost and commission.",
            "impact": "High",
            "metric_value": f"Margin: {avg_margin:.1f}%",
        })
    if roas >= 3:
        strengths.append({
            "title": "Efficient paid acquisition",
            "detail": f"ROAS is {roas:.2f} on ₹{ad_spend:,.0f} ad spend.",
            "impact": "High",
            "metric_value": f"ROAS: {roas:.2f}",
        })
    if return_rate <= 5:
        strengths.append({
            "title": "Low return leakage",
            "detail": f"Return rate is {return_rate:.1f}% across {int(orders)} orders.",
            "impact": "Medium",
            "metric_value": f"Returns: {return_rate:.1f}%",
        })
    if not strengths:
        strengths.append({
            "title": "Catalog presence",
            "detail": f"{name} ({sku}) is live with ₹{revenue:,.0f} recorded revenue.",
            "impact": "Low",
            "metric_value": f"Revenue: ₹{revenue:,.0f}",
        })

    weaknesses = []
    if ad_spend > 0 and roas < 2:
        weaknesses.append({
            "title": "Weak ad efficiency",
            "detail": f"ROAS {roas:.2f} on ₹{ad_spend:,.0f} spend is below a 2.0 floor.",
            "impact": "High",
            "metric_value": f"ROAS: {roas:.2f}",
        })
    if reorder and stock <= reorder:
        weaknesses.append({
            "title": "Stock at or below reorder",
            "detail": f"Available stock is {int(stock)} vs reorder {int(reorder)} ({days_stock:.0f} days of stock).",
            "impact": "High",
            "metric_value": f"Stock: {int(stock)}",
        })
    if return_rate >= 10:
        weaknesses.append({
            "title": "High return rate",
            "detail": f"{return_rate:.1f}% of fulfilled orders came back ({int(returns)} returns).",
            "impact": "High",
            "metric_value": f"Return rate: {return_rate:.1f}%",
        })
    if discount > 0 and revenue > 0 and discount / max(revenue, 1) > 0.12:
        weaknesses.append({
            "title": "Discount erosion",
            "detail": f"₹{discount:,.0f} discounts vs ₹{revenue:,.0f} revenue.",
            "impact": "Medium",
            "metric_value": f"Discounts: ₹{discount:,.0f}",
        })
    if not weaknesses:
        weaknesses.append({
            "title": "Thin performance sample",
            "detail": "Not enough stress signals to flag a leak; keep watching ROAS, stock, and returns weekly.",
            "impact": "Low",
            "metric_value": f"Orders: {int(orders)}",
        })

    recs = []
    if ad_spend > 0 and roas < 2:
        recs.append({
            "action_name": "Pause inefficient ads",
            "reason": f"ROAS {roas:.2f} is below 2.0 on ₹{ad_spend:,.0f} spend.",
            "strategy": "Pause the lowest-ROAS campaign for 7 days and shift budget to the best marketplace listing.",
            "description": f"Cut wasted spend on {name} until ROAS is above 2.0.",
            "estimated_impact_percentage": 8.0,
            "financial_impact_monthly": round(ad_spend * 0.3, 0),
            "is_profit_safe": True,
            "risk_level": "Low",
            "difficulty": "Low",
            "timeframe": "Immediate",
        })
    if reorder and stock <= reorder:
        recs.append({
            "action_name": "Restock before stockout",
            "reason": f"Stock {int(stock)} is at or below reorder {int(reorder)}.",
            "strategy": "Place a replenishment PO this week sized for 30 days of cover.",
            "description": f"Restock {sku or name} to avoid lost sales.",
            "estimated_impact_percentage": 10.0,
            "financial_impact_monthly": round(revenue * 0.15, 0) if revenue else 0,
            "is_profit_safe": True,
            "risk_level": "Low",
            "difficulty": "Medium",
            "timeframe": "This Week",
        })
    if best_mp and _f(best_mp.get("margin_pct")) >= 20:
        mp = best_mp.get("marketplace") or "primary channel"
        recs.append({
            "action_name": f"Push volume on {mp}",
            "reason": f"{mp} currently shows the strongest margin ({_f(best_mp.get('margin_pct')):.1f}%).",
            "strategy": f"Move ad budget and inventory toward {mp} for 14 days.",
            "description": f"Concentrate growth on {mp} for {name}.",
            "estimated_impact_percentage": 6.0,
            "financial_impact_monthly": round(revenue * 0.08, 0) if revenue else 0,
            "is_profit_safe": True,
            "risk_level": "Low",
            "difficulty": "Low",
            "timeframe": "This Week",
        })
    if not recs:
        recs.append({
            "action_name": "Hold price, watch weekly KPIs",
            "reason": "No acute leak in ROAS, stock, or returns.",
            "strategy": "Review ROAS, margin, and stock every Monday; act only if ROAS < 2 or stock hits reorder.",
            "description": f"Keep {name} stable and monitor the dashboard weekly.",
            "estimated_impact_percentage": 2.0,
            "financial_impact_monthly": 0,
            "is_profit_safe": True,
            "risk_level": "Low",
            "difficulty": "Low",
            "timeframe": "This Week",
        })

    mp_summary = "No marketplace split available."
    splits = product_data.get("revenue_by_marketplace") or []
    if splits:
        parts = [f"{s.get('marketplace')}: ₹{_f(s.get('revenue')):,.0f}" for s in splits]
        mp_summary = "Revenue mix — " + "; ".join(parts) + "."

    return {
        "product_health_score": score,
        "performance_verdict": verdict,
        "primary_observation": (
            f"{name} has ₹{revenue:,.0f} revenue, {avg_margin:.1f}% avg margin, "
            f"ROAS {roas:.2f}, and {return_rate:.1f}% returns."
        ),
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "root_causes": [
            {
                "cause": weaknesses[0]["detail"],
                "linked_weakness": weaknesses[0]["title"],
                "evidence": weaknesses[0].get("metric_value") or "",
            }
        ],
        "recommendations": recs[:4],
        "cross_marketplace_summary": mp_summary,
        "confidence_score": 0.72 if orders else 0.45,
    }
