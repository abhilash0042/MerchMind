"""Settlement Q&A copied from reconnAIssance, branded for Brew Boulevard."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


OFF_TOPIC_HINT = (
    "I can answer Brew Boulevard settlement questions — Razorpay STL batches, "
    "2% MDR + 18% GST on fee, UTRs, unmatched coffee orders, and this recon run."
)

_SCOPE_TERMS = (
    "recon", "settlement", "razorpay", "mdr", "gst", "ledger",
    "exception", "match", "tier", "batch", "payout", "fee",
    "shortfall", "audit", "utr", "pipeline", "fuzzy", "exact",
    "commission", "refund", "paise", "rupee", "t+2", "bank",
    "stl-", "bb-ord", "payments", "unsettled", "coffee",
)


def question_in_payments_scope(question: str) -> bool:
    q = (question or "").lower()
    if re.search(r"\b(stl-bb-\d+|stl-\d+|bb-ord[-_ ]?\w+)", q):
        return True
    return any(term in q for term in _SCOPE_TERMS)


def answer_payments_question(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    q_lower = (question or "").lower()
    run_id = context.get("run_id", "current_run")
    metrics = context.get("metrics") or {}
    audits = context.get("audit_logs") or []
    exceptions = context.get("exceptions") or []
    cited_ids = [a.get("id") for a in audits[:3] if a.get("id")]

    if not question_in_payments_scope(question):
        return {"answer": OFF_TOPIC_HINT, "cited_audit_log_ids": []}

    batch_match = re.search(r"(stl-bb-\d+|stl-\d+)", q_lower)
    order_match = re.search(r"(bb-ord[-_ ]?[\w]+|ord-\d+)", q_lower)

    if batch_match:
        batch_id = batch_match.group(1).upper()
        return {
            "answer": (
                f"Settlement batch **{batch_id}** for Brew Boulevard uses Razorpay’s payout model: "
                "gross coffee sales minus **2% MDR** and **18% GST on that fee**, then a **T+2** bank credit. "
                "If the batch looks short, check refunds and unmatched ledger lines on the Payments page."
            ),
            "cited_audit_log_ids": cited_ids,
        }
    if order_match:
        order_id = order_match.group(1).upper().replace(" ", "-")
        return {
            "answer": (
                f"Order **{order_id}** is matched across the sales ledger, Razorpay STL, and bank UTR. "
                "Gross will not equal net after 2% MDR + 18% GST. Unmatched coffee orders show as exceptions."
            ),
            "cited_audit_log_ids": cited_ids,
        }
    if any(k in q_lower for k in ("short", "difference", "deduct", "fee", "mdr", "gst")):
        return {
            "answer": (
                "Brew Boulevard Shopify/Razorpay payouts fall short of GMV for three reasons: "
                "(1) **2% MDR**, (2) **18% GST on the commission**, (3) **refunds or T+2 lag**. "
                "That is expected — it is not missing stock or a ROAS problem."
            ),
            "cited_audit_log_ids": cited_ids,
        }
    if any(k in q_lower for k in ("match rate", "accuracy", "metric", "how many")):
        mr = float(metrics.get("match_rate") or 0)
        return {
            "answer": (
                f"Run `{run_id}` match rate **{mr*100:.1f}%**. "
                f"Tiers: {metrics.get('exact_matches', 0)} exact, {metrics.get('fuzzy_matches', 0)} fuzzy, "
                f"{metrics.get('ai_matches', 0)} AI-assisted, {metrics.get('exception_count', 0)} exceptions."
            ),
            "cited_audit_log_ids": cited_ids,
        }
    if "exception" in q_lower or "unmatch" in q_lower or "unsettled" in q_lower:
        sample = exceptions[:1]
        codes = ", ".join(sorted({e.get("reason_code", "?") for e in exceptions})) or "none"
        extra = sample[0].get("reason_text") if sample else ""
        return {
            "answer": (
                f"This run has **{metrics.get('exception_count', 0)}** exceptions ({codes}). {extra}"
            ),
            "cited_audit_log_ids": cited_ids,
        }

    return {
        "answer": (
            f"Run `{run_id}` processed **{metrics.get('record_count', 0)}** cash records for Brew Boulevard: "
            f"{metrics.get('exact_matches', 0)} exact, {metrics.get('fuzzy_matches', 0)} fuzzy, "
            f"{metrics.get('ai_matches', 0)} AI, {metrics.get('exception_count', 0)} still open. "
            "Ask about an STL-BB batch, a BB-ORD id, or why a payout is short of coffee GMV."
        ),
        "cited_audit_log_ids": cited_ids,
    }
