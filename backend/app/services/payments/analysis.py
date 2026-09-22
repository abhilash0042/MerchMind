"""Brew Boulevard payments analysis — cash waterfall, tier funnel, ML-style insights."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    PaymentBankRow,
    PaymentCanonical,
    PaymentException,
    PaymentLedgerRow,
    PaymentMatchGroup,
    PaymentMatchMember,
    PaymentReconRun,
    PaymentSettlementRow,
)


def _r(paise: int) -> float:
    return round((paise or 0) / 100.0, 2)


async def compute_payment_analysis(
    db: AsyncSession,
    seller_id: str,
    run: Optional[PaymentReconRun] = None,
) -> Dict[str, Any]:
    seller_uuid = UUID(seller_id)

    ledger_rows = list(
        (await db.execute(select(PaymentLedgerRow).where(PaymentLedgerRow.seller_id == seller_uuid)))
        .scalars()
        .all()
    )
    settlement_rows = list(
        (await db.execute(select(PaymentSettlementRow).where(PaymentSettlementRow.seller_id == seller_uuid)))
        .scalars()
        .all()
    )
    bank_rows = list(
        (await db.execute(select(PaymentBankRow).where(PaymentBankRow.seller_id == seller_uuid)))
        .scalars()
        .all()
    )

    gross_paise = sum(r.amount_paise for r in ledger_rows)
    fee_paise = sum(r.fee_amount_paise for r in settlement_rows)
    gst_paise = sum(r.gst_on_fee_paise for r in settlement_rows)
    net_settlement_paise = sum(r.net_amount_paise for r in settlement_rows)
    bank_paise = sum(r.credit_amount_paise for r in bank_rows)

    analysis: Dict[str, Any] = {
        "has_ledger": len(ledger_rows) > 0,
        "ledger_count": len(ledger_rows),
        "settlement_count": len(settlement_rows),
        "bank_count": len(bank_rows),
        "cash_waterfall": {
            "gross_gmv_rupees": _r(gross_paise),
            "razorpay_fees_rupees": _r(fee_paise),
            "gst_on_fees_rupees": _r(gst_paise),
            "net_settlement_rupees": _r(net_settlement_paise),
            "bank_credited_rupees": _r(bank_paise),
            "fee_drag_pct": round((fee_paise + gst_paise) / max(gross_paise, 1) * 100, 2),
            "bank_vs_net_gap_rupees": _r(bank_paise - net_settlement_paise),
        },
        "tier_funnel": None,
        "exception_breakdown": [],
        "insights": [],
        "predictions": [],
        "risk_board": _risk_board(ledger_rows),
    }

    if not run:
        analysis["insights"] = _insights_no_run(analysis)
        return analysis

    matched_ledger_paise = 0
    exception_ledger_paise = 0
    exc_codes: Counter = Counter()

    if run.id:
        matched_canon_ids = set(
            (
                await db.execute(
                    select(PaymentMatchMember.canonical_id).where(
                        PaymentMatchMember.group_id.in_(
                            select(PaymentMatchGroup.id).where(PaymentMatchGroup.run_id == run.id)
                        )
                    )
                )
            )
            .scalars()
            .all()
        )
        ledger_canons = list(
            (
                await db.execute(
                    select(PaymentCanonical).where(
                        PaymentCanonical.run_id == run.id,
                        PaymentCanonical.source == "ledger",
                    )
                )
            )
            .scalars()
            .all()
        )
        for c in ledger_canons:
            if c.id in matched_canon_ids:
                matched_ledger_paise += c.amount_paise
            else:
                exception_ledger_paise += c.amount_paise

        exc_rows = (
            await db.execute(
                select(PaymentException).where(PaymentException.run_id == run.id)
            )
        ).scalars().all()
        for e in exc_rows:
            exc_codes[e.reason_code] += 1

    tiers = {
        "exact": run.exact_matches or 0,
        "fuzzy": run.fuzzy_matches or 0,
        "ai_assisted": run.ai_matches or 0,
        "exceptions": run.exception_count or 0,
    }
    total_decisions = sum(tiers.values()) or 1

    analysis["tier_funnel"] = {
        **tiers,
        "match_rate": float(run.match_rate or 0),
        "record_count": run.record_count,
        "stages": [
            {
                "name": "Tier 1 — Exact",
                "count": tiers["exact"],
                "pct_of_total": round(tiers["exact"] / total_decisions * 100, 1),
                "method": "Deterministic order_ref = ledger key",
            },
            {
                "name": "Tier 2 — Fuzzy + fee math",
                "count": tiers["fuzzy"],
                "pct_of_total": round(tiers["fuzzy"] / total_decisions * 100, 1),
                "method": "2% MDR + 18% GST window, date lag, ref similarity",
            },
            {
                "name": "Tier 3 — AI-assisted",
                "count": tiers["ai_assisted"],
                "pct_of_total": round(tiers["ai_assisted"] / total_decisions * 100, 1),
                "method": "Model scores ambiguous ledger ↔ STL pairs",
            },
            {
                "name": "Exceptions",
                "count": tiers["exceptions"],
                "pct_of_total": round(tiers["exceptions"] / total_decisions * 100, 1),
                "method": "NO_COUNTERPART / AMOUNT_MISMATCH / DUPLICATE",
            },
        ],
    }

    analysis["exception_breakdown"] = [
        {"reason_code": code, "count": count}
        for code, count in exc_codes.most_common()
    ]

    analysis["matched_gmv_rupees"] = _r(matched_ledger_paise)
    analysis["unsettled_gmv_rupees"] = _r(exception_ledger_paise)

    analysis["insights"] = _build_insights(analysis, run)
    analysis["predictions"] = _build_predictions(analysis, run)
    return analysis


def _insights_no_run(analysis: Dict[str, Any]) -> List[str]:
    if not analysis["has_ledger"]:
        return [
            "Import Brew Boulevard orders or click Build cash from orders to create a Razorpay ledger.",
            "Payments analysis compares coffee GMV (ledger) to Razorpay net payouts and bank UTR credits.",
        ]
    return [
        f"Ledger has {analysis['ledger_count']} coffee orders worth ₹{analysis['cash_waterfall']['gross_gmv_rupees']:,.0f} gross.",
        "Run recon to match Razorpay STL and bank UTRs. SKU risk scores below already flag refunds and marketplace GMV that will not hit Razorpay.",
    ]


def _build_insights(analysis: Dict[str, Any], run: PaymentReconRun) -> List[str]:
    wf = analysis["cash_waterfall"]
    insights: List[str] = []
    mr = float(run.match_rate or 0) * 100

    insights.append(
        f"Match rate **{mr:.1f}%** — {run.exact_matches} exact, {run.fuzzy_matches} fuzzy, "
        f"{run.ai_matches} AI-assisted, {run.exception_count} still open."
    )
    insights.append(
        f"Razorpay fee drag is **{wf['fee_drag_pct']}%** of gross (2% MDR + 18% GST on fee = "
        f"₹{wf['razorpay_fees_rupees']:,.0f} + ₹{wf['gst_on_fees_rupees']:,.0f})."
    )

    unsettled = analysis.get("unsettled_gmv_rupees", 0)
    if unsettled > 0:
        insights.append(
            f"**₹{unsettled:,.0f}** of coffee GMV is still unsettled — not in bank yet. "
            "Check Exceptions for refunds, T+2 lag, or missing STL rows."
        )

    gap = wf.get("bank_vs_net_gap_rupees", 0)
    if abs(gap) > 1:
        insights.append(
            f"Bank credits differ from Razorpay net by **₹{gap:,.0f}** — bundled STL batches or missing bank lines."
        )
    else:
        insights.append("Bank UTR totals align with Razorpay net settlement — cash position looks consistent.")

    if run.fuzzy_matches > 0:
        insights.append(
            f"**{run.fuzzy_matches} fuzzy matches** recovered orders with typo/noise in refs or T+2 date lag — "
            "typical for real Razorpay exports."
        )
    if run.ai_matches == 0 and run.exception_count > 5:
        insights.append(
            "Tier 3 AI found no extra pairs — remaining exceptions may need manual STL upload or refund adjustment."
        )

    top_exc = analysis.get("exception_breakdown") or []
    if top_exc:
        code, cnt = top_exc[0]["reason_code"], top_exc[0]["count"]
        insights.append(f"Top exception: **{code}** ({cnt} rows) — prioritize these in finance review.")

    return insights


def _risk_board(ledger_rows: list) -> List[Dict[str, Any]]:
    """Score which coffee orders are likely to miss Razorpay/bank match.

    This is a scored heuristic (not a trained neural net). It uses the same
    signals reconnAIssance encodes: refunds, channel (Shopify vs marketplace),
    payment method, and T+2 lag. That is more honest and more useful on a
    few hundred Brew Boulevard rows than fitting sklearn on this demo.
    """
    by_sku: Dict[str, Dict[str, Any]] = {}
    for row in ledger_rows:
        sku = row.sku or "unknown"
        bucket = by_sku.setdefault(
            sku,
            {"sku": sku, "orders": 0, "gmv_paise": 0, "risk_sum": 0.0, "reasons": Counter()},
        )
        score, reason = _row_risk(row)
        bucket["orders"] += 1
        bucket["gmv_paise"] += row.amount_paise
        bucket["risk_sum"] += score
        bucket["reasons"][reason] += 1

    board = []
    for sku, b in by_sku.items():
        avg = b["risk_sum"] / max(b["orders"], 1)
        top_reason = b["reasons"].most_common(1)[0][0] if b["reasons"] else "ok"
        board.append(
            {
                "sku": sku,
                "orders": b["orders"],
                "gmv_rupees": _r(b["gmv_paise"]),
                "risk_score": round(avg, 2),
                "risk_band": "high" if avg >= 0.55 else ("medium" if avg >= 0.28 else "low"),
                "top_reason": top_reason,
            }
        )
    board.sort(key=lambda x: (-x["risk_score"], -x["gmv_rupees"]))
    return board[:8]


def _row_risk(row) -> tuple[float, str]:
    status = (row.status or "").lower()
    mp = (row.marketplace or "").lower()
    pm = (row.payment_method or "").lower()
    if status in ("refunded", "returned", "partially_refunded"):
        return 0.82, "refund_before_settlement"
    if any(x in mp for x in ("amazon", "flipkart", "meesho")):
        return 0.7, "marketplace_payout_not_razorpay"
    if status in ("cancelled", "canceled"):
        return 0.75, "cancelled_order"
    if any(x in mp for x in ("shopify", "d2c", "website")) or pm in ("upi", "card", "razorpay"):
        return 0.12, "shopify_razorpay_expected"
    return 0.4, "channel_unclear"


def _build_predictions(analysis: Dict[str, Any], run: PaymentReconRun) -> List[Dict[str, Any]]:
    wf = analysis["cash_waterfall"]
    unsettled = analysis.get("unsettled_gmv_rupees", 0) or 0
    fee_drag = wf.get("fee_drag_pct") or 2.36
    high_risk = [r for r in (analysis.get("risk_board") or []) if r["risk_band"] == "high"]
    high_gmv = sum(r["gmv_rupees"] for r in high_risk)

    preds = [
        {
            "label": "Expected net in bank (after MDR+GST)",
            "value_rupees": round(wf["gross_gmv_rupees"] * (1 - fee_drag / 100), 0),
            "confidence": "high",
            "explanation": (
                f"Razorpay keeps ~{fee_drag}% of coffee GMV (2% MDR + 18% GST on fee). "
                "This is a formula, not a guess — same math as reconn Tier 2."
            ),
        },
        {
            "label": "Cash at risk this cycle",
            "value_rupees": round(unsettled + high_gmv * 0.35, 0),
            "confidence": "medium",
            "explanation": (
                "Unmatched GMV plus 35% of high-risk SKU sales (refunds / Amazon-Flipkart not on Razorpay). "
                "Use this as a working-capital buffer, not a guarantee."
            ),
        },
        {
            "label": "Likely T+2 bank credit",
            "value_rupees": round(wf.get("net_settlement_rupees") or 0, 0),
            "confidence": "high",
            "explanation": "Net STL already in Razorpay reports typically lands in the bank two days later.",
        },
    ]
    return preds
