"""3-tier matching ported from reconnAIssance (exact / fuzzy+MDR / AI leftover)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional, Set, Tuple

from rapidfuzz import fuzz

from app.services.payments.refs import normalize_ref_string, razorpay_fee_split


TIER2_DATE_WINDOW_DAYS = 5
TIER2_CONFIDENCE_FLOOR = 0.70


@dataclass
class Canon:
    id: str
    source: str
    source_row_id: int
    normalized_ref: str
    amount_paise: int
    event_date: date
    batch_id: Optional[str]
    sku: Optional[str]
    product_id: Optional[str]
    raw_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchHit:
    group_id: str
    tier: str
    confidence: float
    reason: str
    members: List[Tuple[str, str]]  # (canonical_id, role)
    audit_reason: str
    audit_canonical_id: str


def _date_diff(d1: date, d2: date) -> int:
    try:
        return abs((d1 - d2).days)
    except Exception:
        return 999


def compute_fee_aware_amount_score(gross_paise: int, net_paise: int) -> Tuple[float, float]:
    if gross_paise <= 0 or net_paise <= 0:
        return 0.0, 1.0
    fee, gst, expected_net = razorpay_fee_split(gross_paise)
    diff = abs(net_paise - expected_net)
    deviation_pct = diff / max(expected_net, 1)
    amt_score = max(0.0, 1.0 - (deviation_pct / 0.05))
    return amt_score, deviation_pct


def _attach_bank(settlement: Canon, bank_records: List[Canon], matched: Set[str]) -> Optional[str]:
    if not settlement.batch_id:
        return None
    bid = settlement.batch_id.lower()
    for b in bank_records:
        if b.id in matched:
            continue
        if (b.batch_id and b.batch_id.lower() == bid) or (
            b.normalized_ref and bid in (b.normalized_ref or "").lower()
        ):
            return b.id
    return None


def match_tier1(records: List[Canon]) -> Tuple[List[MatchHit], List[Canon]]:
    ledger = [r for r in records if r.source == "ledger"]
    settlements = [r for r in records if r.source == "settlement"]
    banks = [r for r in records if r.source == "bank"]

    settlement_by_ref: Dict[str, List[Canon]] = {}
    for s in settlements:
        settlement_by_ref.setdefault(s.normalized_ref, []).append(s)

    matched: Set[str] = set()
    hits: List[MatchHit] = []

    for l in ledger:
        candidates = settlement_by_ref.get(l.normalized_ref, [])
        valid_s = next((s for s in candidates if s.id not in matched), None)
        if not valid_s:
            continue
        gid = str(uuid.uuid4())
        matched.add(l.id)
        matched.add(valid_s.id)
        members = [(l.id, "ledger_entry"), (valid_s.id, "settlement_entry")]
        bank_id = _attach_bank(valid_s, banks, matched)
        if bank_id:
            members.append((bank_id, "bank_entry"))
            matched.add(bank_id)
        reason = f"Tier 1 Exact Match on normalized reference key '{l.normalized_ref}'"
        hits.append(
            MatchHit(
                group_id=gid,
                tier="exact",
                confidence=1.0,
                reason=reason,
                members=members,
                audit_reason=f"Exact 1:1 key match for order '{l.normalized_ref}' with settlement '{valid_s.normalized_ref}'",
                audit_canonical_id=l.id,
            )
        )

    unmatched = [r for r in records if r.id not in matched]
    return hits, unmatched


def match_tier2(records: List[Canon]) -> Tuple[List[MatchHit], List[Canon]]:
    ledger = [r for r in records if r.source == "ledger"]
    settlements = [r for r in records if r.source == "settlement"]
    banks = [r for r in records if r.source == "bank"]
    matched: Set[str] = set()
    hits: List[MatchHit] = []

    for l in ledger:
        best: Optional[Canon] = None
        best_conf = 0.0
        best_metrics: Dict[str, Any] = {}
        for s in settlements:
            if s.id in matched:
                continue
            ref_sim = fuzz.ratio(l.normalized_ref, s.normalized_ref) / 100.0
            day_diff = _date_diff(l.event_date, s.event_date)
            if day_diff > TIER2_DATE_WINDOW_DAYS:
                continue
            date_score = max(0.0, 1.0 - (max(0, day_diff - 2) / (TIER2_DATE_WINDOW_DAYS - 2 + 1e-5)))
            amt_score, dev_pct = compute_fee_aware_amount_score(l.amount_paise, s.amount_paise)
            if ref_sim < 0.70 and amt_score < 0.80:
                continue
            composite = (0.40 * ref_sim) + (0.35 * amt_score) + (0.25 * date_score)
            if composite > best_conf:
                best_conf = composite
                best = s
                best_metrics = {"ref_sim": ref_sim, "day_diff": day_diff, "dev_pct": dev_pct}

        if best and best_conf >= TIER2_CONFIDENCE_FLOOR:
            gid = str(uuid.uuid4())
            matched.add(l.id)
            matched.add(best.id)
            conf_val = round(best_conf, 2)
            reason = (
                f"Tier 2 Fuzzy Match: Ref similarity {best_metrics['ref_sim']*100:.0f}%, "
                f"amount deviation {best_metrics['dev_pct']*100:.1f}% within fee window, "
                f"date lag {best_metrics['day_diff']} days (confidence {conf_val:.2f})"
            )
            members = [(l.id, "ledger_entry"), (best.id, "settlement_entry")]
            bank_id = _attach_bank(best, banks, matched)
            if bank_id:
                members.append((bank_id, "bank_entry"))
                matched.add(bank_id)
            hits.append(
                MatchHit(
                    group_id=gid,
                    tier="fuzzy",
                    confidence=conf_val,
                    reason=reason,
                    members=members,
                    audit_reason=reason,
                    audit_canonical_id=l.id,
                )
            )

    unmatched = [r for r in records if r.id not in matched]
    return hits, unmatched


def _pre_score(ledger: Canon, settlement: Canon) -> float:
    score = 0.0
    ref_sim = fuzz.ratio(ledger.normalized_ref, settlement.normalized_ref) / 100.0
    score += ref_sim * 40.0
    amt_score, _ = compute_fee_aware_amount_score(ledger.amount_paise, settlement.amount_paise)
    score += amt_score * 35.0
    day_diff = _date_diff(ledger.event_date, settlement.event_date)
    date_score = max(0.0, 1.0 - (max(0, day_diff - 2) / 5.0))
    score += date_score * 25.0
    return score


def _mock_ai_decide(item_a: Dict, item_b: Dict) -> Dict[str, Any]:
    ref_a = item_a.get("normalized_ref") or item_a.get("order_id") or item_a.get("order_ref") or ""
    ref_b = item_b.get("normalized_ref") or item_b.get("order_id") or item_b.get("order_ref") or ""
    amt_a = item_a.get("amount_paise") or item_a.get("gross_amount_paise") or 0
    amt_b = item_b.get("amount_paise") or item_b.get("net_amount_paise") or item_b.get("gross_amount_paise") or 0
    expected_net = int(round(amt_a * 0.9764)) if amt_a > amt_b else int(round(amt_b * 0.9764))
    diff = abs(amt_a - amt_b) if abs(amt_a - amt_b) < 1000 else abs(min(amt_a, amt_b) - expected_net)
    amt_diff_pct = diff / max(amt_a, amt_b, 1)
    ref_sim = fuzz.ratio(str(ref_a), str(ref_b)) / 100.0
    if ref_sim >= 0.70 and amt_diff_pct < 0.08:
        confidence = min(0.95, round(0.72 + (ref_sim * 0.15) + (1.0 - amt_diff_pct) * 0.1, 2))
        return {
            "match": True,
            "confidence": confidence,
            "reason": (
                f"AI matched: '{ref_a}' vs '{ref_b}' (similarity {ref_sim:.2f}); "
                "amount delta is consistent with 2% MDR + 18% GST on fee."
            ),
        }
    return {
        "match": False,
        "confidence": 0.35,
        "reason": f"AI rejected: discrepancy between '{ref_a}' and '{ref_b}' or amount vs fee schedule.",
    }


def match_tier3(records: List[Canon]) -> Tuple[List[MatchHit], List[Canon]]:
    ledger = [r for r in records if r.source == "ledger"]
    settlements = [r for r in records if r.source == "settlement"]
    banks = [r for r in records if r.source == "bank"]
    if not ledger or not settlements:
        return [], records

    matched: Set[str] = set()
    hits: List[MatchHit] = []

    for l in ledger:
        scored: List[Tuple[float, Canon]] = []
        for s in settlements:
            if s.id in matched:
                continue
            pre = _pre_score(l, s)
            if pre >= 20.0:
                scored.append((pre, s))
        if not scored:
            continue
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]
        payload_a = {**l.raw_payload, "normalized_ref": l.normalized_ref, "amount_paise": l.amount_paise}
        payload_b = {**best.raw_payload, "normalized_ref": best.normalized_ref, "amount_paise": best.amount_paise}
        decision = _mock_ai_decide(payload_a, payload_b)
        if not decision.get("match"):
            continue
        if l.id in matched or best.id in matched:
            continue
        gid = str(uuid.uuid4())
        matched.add(l.id)
        matched.add(best.id)
        reason = f"Tier 3 AI Match: {decision.get('reason')}"
        members = [(l.id, "ledger_entry"), (best.id, "settlement_entry")]
        bank_id = _attach_bank(best, banks, matched)
        if bank_id:
            members.append((bank_id, "bank_entry"))
            matched.add(bank_id)
        hits.append(
            MatchHit(
                group_id=gid,
                tier="ai_assisted",
                confidence=float(decision.get("confidence", 0.8)),
                reason=reason,
                members=members,
                audit_reason=decision.get("reason", reason),
                audit_canonical_id=l.id,
            )
        )

    unmatched = [r for r in records if r.id not in matched]
    return hits, unmatched


def classify_exceptions(unmatched: List[Canon]) -> List[Dict[str, Any]]:
    ref_counts: Dict[str, int] = {}
    for r in unmatched:
        ref_counts[r.normalized_ref] = ref_counts.get(r.normalized_ref, 0) + 1
    out = []
    for r in unmatched:
        if ref_counts.get(r.normalized_ref, 0) > 1:
            code = "DUPLICATE_SUSPECTED"
            text = (
                f"Duplicate transaction detected: Reference '{r.normalized_ref}' "
                f"appears multiple times in {r.source} dataset."
            )
        elif r.source == "ledger":
            code = "NO_COUNTERPART_FOUND"
            text = (
                f"Unresolved coffee order '{r.normalized_ref}' for ₹{r.amount_paise/100:.2f} "
                "has no matching Razorpay settlement or bank credit."
            )
        elif r.source == "settlement":
            code = "AMOUNT_MISMATCH"
            text = (
                f"Unmatched settlement '{r.normalized_ref}' net ₹{r.amount_paise/100:.2f} "
                "could not be tied back to Brew Boulevard sales ledger."
            )
        else:
            code = "NO_COUNTERPART_FOUND"
            text = (
                f"Unmatched bank credit '{r.normalized_ref}' for ₹{r.amount_paise/100:.2f} "
                "has no corresponding Razorpay STL batch."
            )
        out.append(
            {
                "canonical_id": r.id,
                "reason_code": code,
                "reason_text": text,
            }
        )
    return out
