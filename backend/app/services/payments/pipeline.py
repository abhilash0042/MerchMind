"""Run reconnAIssance-style pipeline against Pulse payment tables."""
from __future__ import annotations

import logging
import time
import traceback
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    PaymentAuditLog,
    PaymentBankRow,
    PaymentCanonical,
    PaymentException,
    PaymentLedgerRow,
    PaymentMatchGroup,
    PaymentMatchMember,
    PaymentReconRun,
    PaymentSettlementRow,
)
from app.services.payments.engine import Canon, classify_exceptions, match_tier1, match_tier2, match_tier3
from app.services.payments.refs import extract_utr_and_batch_from_narration, normalize_ref_string

logger = logging.getLogger(__name__)


def _as_date(val) -> date:
    if isinstance(val, datetime):
        return val.date()
    return val


async def _persist_hits(db: AsyncSession, run_id: str, hits, tier: str) -> None:
    groups = []
    members = []
    audits = []
    for h in hits:
        groups.append(
            PaymentMatchGroup(
                id=h.group_id,
                run_id=run_id,
                tier=h.tier,
                confidence=h.confidence,
                reason=h.reason,
            )
        )
        for cid, role in h.members:
            members.append(PaymentMatchMember(group_id=h.group_id, canonical_id=cid, role=role))
        audits.append(
            PaymentAuditLog(
                run_id=run_id,
                canonical_id=h.audit_canonical_id,
                group_id=h.group_id,
                tier=h.tier,
                action="matched",
                confidence=h.confidence,
                reason=h.audit_reason,
            )
        )
    db.add_all(groups)
    db.add_all(members)
    db.add_all(audits)
    await db.flush()


async def execute_pipeline(db: AsyncSession, seller_id: str, run_id: str | None = None) -> Dict[str, Any]:
    seller_uuid = UUID(str(seller_id))
    run_id = run_id or f"run_{uuid.uuid4().hex[:12]}"
    t0 = time.perf_counter()

    run = PaymentReconRun(id=run_id, seller_id=seller_uuid, status="running")
    db.add(run)
    await db.flush()

    try:
        ledgers = list(
            (await db.execute(select(PaymentLedgerRow).where(PaymentLedgerRow.seller_id == seller_uuid)))
            .scalars()
            .all()
        )
        settlements = list(
            (await db.execute(select(PaymentSettlementRow).where(PaymentSettlementRow.seller_id == seller_uuid)))
            .scalars()
            .all()
        )
        banks = list(
            (await db.execute(select(PaymentBankRow).where(PaymentBankRow.seller_id == seller_uuid)))
            .scalars()
            .all()
        )
        if not ledgers:
            raise ValueError("No payment ledger rows. Import Brew Boulevard orders or run cash seed first.")

        records: List[Canon] = []
        orm_rows: List[PaymentCanonical] = []

        for row in ledgers:
            cid = str(uuid.uuid4())
            payload = {
                "source": "ledger",
                "order_id": row.order_id,
                "sku": row.sku,
                "marketplace": row.marketplace,
                "amount_paise": row.amount_paise,
                "payment_method": row.payment_method,
                "status": row.status,
                "order_date": str(row.order_date),
            }
            rec = Canon(
                id=cid,
                source="ledger",
                source_row_id=row.id,
                normalized_ref=normalize_ref_string(row.order_id),
                amount_paise=row.amount_paise,
                event_date=_as_date(row.order_date),
                batch_id=None,
                sku=row.sku,
                product_id=str(row.product_id) if row.product_id else None,
                raw_payload=payload,
            )
            records.append(rec)
            orm_rows.append(
                PaymentCanonical(
                    id=cid,
                    run_id=run_id,
                    seller_id=seller_uuid,
                    source="ledger",
                    source_row_id=row.id,
                    normalized_ref=rec.normalized_ref,
                    amount_paise=row.amount_paise,
                    event_date=rec.event_date,
                    sku=row.sku,
                    product_id=row.product_id,
                    raw_payload=payload,
                )
            )

        for row in settlements:
            cid = str(uuid.uuid4())
            payload = {
                "source": "settlement",
                "settlement_batch_id": row.settlement_batch_id,
                "utr": row.utr,
                "order_ref": row.order_ref,
                "sku": row.sku,
                "gross_amount_paise": row.gross_amount_paise,
                "fee_amount_paise": row.fee_amount_paise,
                "gst_on_fee_paise": row.gst_on_fee_paise,
                "net_amount_paise": row.net_amount_paise,
                "settlement_date": str(row.settlement_date),
            }
            rec = Canon(
                id=cid,
                source="settlement",
                source_row_id=row.id,
                normalized_ref=normalize_ref_string(row.order_ref),
                amount_paise=row.net_amount_paise,
                event_date=_as_date(row.settlement_date),
                batch_id=row.settlement_batch_id,
                sku=row.sku,
                product_id=str(row.product_id) if row.product_id else None,
                raw_payload=payload,
            )
            records.append(rec)
            orm_rows.append(
                PaymentCanonical(
                    id=cid,
                    run_id=run_id,
                    seller_id=seller_uuid,
                    source="settlement",
                    source_row_id=row.id,
                    normalized_ref=rec.normalized_ref,
                    amount_paise=row.net_amount_paise,
                    event_date=rec.event_date,
                    batch_id=row.settlement_batch_id,
                    sku=row.sku,
                    product_id=row.product_id,
                    raw_payload=payload,
                )
            )

        for row in banks:
            cid = str(uuid.uuid4())
            utr, batch_id = extract_utr_and_batch_from_narration(row.narration or "")
            nref = normalize_ref_string(batch_id or utr or row.bank_txn_id)
            payload = {
                "source": "bank",
                "bank_txn_id": row.bank_txn_id,
                "narration": row.narration,
                "extracted_utr": utr,
                "extracted_batch_id": batch_id,
                "credit_amount_paise": row.credit_amount_paise,
            }
            rec = Canon(
                id=cid,
                source="bank",
                source_row_id=row.id,
                normalized_ref=nref,
                amount_paise=row.credit_amount_paise,
                event_date=_as_date(row.value_date),
                batch_id=batch_id or None,
                sku=None,
                product_id=None,
                raw_payload=payload,
            )
            records.append(rec)
            orm_rows.append(
                PaymentCanonical(
                    id=cid,
                    run_id=run_id,
                    seller_id=seller_uuid,
                    source="bank",
                    source_row_id=row.id,
                    normalized_ref=nref,
                    amount_paise=row.credit_amount_paise,
                    event_date=rec.event_date,
                    batch_id=batch_id or None,
                    raw_payload=payload,
                )
            )

        db.add_all(orm_rows)
        db.add(
            PaymentAuditLog(
                run_id=run_id,
                tier="ingestion",
                action="ingested",
                confidence=1.0,
                reason=(
                    f"Ingested {len(ledgers)} ledger, {len(settlements)} settlement, "
                    f"and {len(banks)} bank records for Brew Boulevard cash recon."
                ),
            )
        )
        await db.flush()

        exact_hits, remaining = match_tier1(records)
        await _persist_hits(db, run_id, exact_hits, "exact")
        fuzzy_hits, remaining = match_tier2(remaining)
        await _persist_hits(db, run_id, fuzzy_hits, "fuzzy")
        ai_hits, remaining = match_tier3(remaining)
        await _persist_hits(db, run_id, ai_hits, "ai_assisted")

        exceptions = classify_exceptions(remaining)
        exc_orm = []
        for e in exceptions:
            eid = str(uuid.uuid4())
            exc_orm.append(
                PaymentException(
                    id=eid,
                    run_id=run_id,
                    canonical_id=e["canonical_id"],
                    reason_code=e["reason_code"],
                    reason_text=e["reason_text"],
                )
            )
            db.add(
                PaymentAuditLog(
                    run_id=run_id,
                    canonical_id=e["canonical_id"],
                    tier="ai_assisted",
                    action="flagged_exception",
                    confidence=1.0,
                    reason=f"[{e['reason_code']}] {e['reason_text']}",
                )
            )
        db.add_all(exc_orm)

        ledger_total = len(ledgers)
        matched_ledger = ledger_total - sum(1 for r in remaining if r.source == "ledger")
        match_rate = (matched_ledger / ledger_total) if ledger_total else 0.0

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.record_count = len(records)
        run.match_rate = round(match_rate, 4)
        run.exact_matches = len(exact_hits)
        run.fuzzy_matches = len(fuzzy_hits)
        run.ai_matches = len(ai_hits)
        run.exception_count = len(exceptions)
        await db.commit()

        elapsed = time.perf_counter() - t0
        logger.info("Payments recon %s done in %.2fs match_rate=%.3f", run_id, elapsed, match_rate)
        return {
            "run_id": run_id,
            "status": "completed",
            "record_count": len(records),
            "match_rate": float(run.match_rate),
            "tier_breakdown": {
                "exact": len(exact_hits),
                "fuzzy": len(fuzzy_hits),
                "ai_assisted": len(ai_hits),
            },
            "exception_count": len(exceptions),
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as e:
        logger.error("Payments recon failed: %s\n%s", e, traceback.format_exc())
        run.status = "failed"
        run.completed_at = datetime.now(timezone.utc)
        run.error_message = str(e)
        await db.commit()
        raise
