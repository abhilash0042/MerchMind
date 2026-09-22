"""Payments / settlements — reconnAIssance engine exposed in CommercePulse."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import enforce_seller_scope, rate_limiter
from app.db.session import get_db
from app.models.models import (
    PaymentAuditLog,
    PaymentCanonical,
    PaymentException,
    PaymentLedgerRow,
    PaymentMatchGroup,
    PaymentMatchMember,
    PaymentReconRun,
)
from app.services.payments.pipeline import execute_pipeline
from app.services.payments.qa import answer_payments_question
from app.services.payments.seed import seed_cash_from_orders

router = APIRouter(
    dependencies=[Depends(rate_limiter(max_requests=60, window_seconds=60))],
)


class SeedRequest(BaseModel):
    seller_id: str


class ReconRequest(BaseModel):
    seller_id: str


class AskRequest(BaseModel):
    seller_id: str
    question: str
    run_id: Optional[str] = None


def _rupees(paise: int) -> float:
    return round((paise or 0) / 100.0, 2)


@router.post("/seed")
async def seed_brew_cash(
    body: SeedRequest,
    seller_id: str = Query(..., description="Seller UUID (must match X-Seller-Id header)"),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    if seller_id != body.seller_id:
        raise HTTPException(status_code=403, detail="seller_id query must match request body")
    return await seed_cash_from_orders(db, body.seller_id)


@router.post("/reconcile")
async def run_reconciliation(
    body: ReconRequest,
    seller_id: str = Query(..., description="Seller UUID (must match X-Seller-Id header)"),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    if seller_id != body.seller_id:
        raise HTTPException(status_code=403, detail="seller_id query must match request body")
    try:
        return await execute_pipeline(db, body.seller_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs")
async def list_runs(
    seller_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    q = (
        select(PaymentReconRun)
        .where(PaymentReconRun.seller_id == UUID(seller_id))
        .order_by(PaymentReconRun.started_at.desc())
        .limit(20)
    )
    rows = (await db.execute(q)).scalars().all()
    return {
        "results": [
            {
                "run_id": r.id,
                "status": r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "match_rate": float(r.match_rate or 0),
                "record_count": r.record_count,
                "exact_matches": r.exact_matches,
                "fuzzy_matches": r.fuzzy_matches,
                "ai_matches": r.ai_matches,
                "exception_count": r.exception_count,
                "error_message": r.error_message,
            }
            for r in rows
        ]
    }


@router.get("/analysis")
async def payments_analysis(
    seller_id: str = Query(...),
    run_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    """Cash waterfall, tier funnel, insights, and settlement predictions."""
    from app.services.payments.analysis import compute_payment_analysis

    run = await _resolve_run(db, seller_id, run_id)
    data = await compute_payment_analysis(db, seller_id, run)
    data["run_id"] = run.id if run else None
    data["has_run"] = run is not None
    if run:
        data["match_rate"] = float(run.match_rate or 0)
        data["tier_breakdown"] = {
            "exact": run.exact_matches,
            "fuzzy": run.fuzzy_matches,
            "ai_assisted": run.ai_matches,
        }
        data["exception_count"] = run.exception_count
    return data


@router.get("/summary")
async def latest_summary(
    seller_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    from app.services.payments.analysis import compute_payment_analysis

    run = await _resolve_run(db, seller_id, None)
    analysis = await compute_payment_analysis(db, seller_id, run)
    ledger_count = analysis.get("ledger_count", 0)

    if not run:
        return {
            "has_run": False,
            "ledger_count": ledger_count,
            "message": "No reconciliation yet. Seed coffee cash files, then run recon.",
            **analysis,
        }

    return {
        "has_run": True,
        "ledger_count": ledger_count,
        "run_id": run.id,
        "status": run.status,
        "match_rate": float(run.match_rate or 0),
        "record_count": run.record_count,
        "tier_breakdown": {
            "exact": run.exact_matches,
            "fuzzy": run.fuzzy_matches,
            "ai_assisted": run.ai_matches,
        },
        "exception_count": run.exception_count,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        **analysis,
    }


@router.get("/matches")
async def list_matches(
    seller_id: str = Query(...),
    run_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    run = await _resolve_run(db, seller_id, run_id)
    if not run:
        return {"total": 0, "results": []}

    total = (
        await db.execute(select(func.count(PaymentMatchGroup.id)).where(PaymentMatchGroup.run_id == run.id))
    ).scalar() or 0
    groups = (
        await db.execute(
            select(PaymentMatchGroup)
            .where(PaymentMatchGroup.run_id == run.id)
            .order_by(PaymentMatchGroup.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    gids = [g.id for g in groups]
    member_map: dict = {}
    if gids:
        rows = (
            await db.execute(
                select(PaymentMatchMember, PaymentCanonical)
                .join(PaymentCanonical, PaymentMatchMember.canonical_id == PaymentCanonical.id)
                .where(PaymentMatchMember.group_id.in_(gids))
            )
        ).all()
        for m, c in rows:
            payload = c.raw_payload or {}
            sku = c.sku or payload.get("sku")
            order_id = payload.get("order_id") or payload.get("order_ref") or c.normalized_ref
            member_map.setdefault(m.group_id, []).append(
                {
                    "role": m.role,
                    "source": c.source,
                    "normalized_ref": c.normalized_ref,
                    "order_id": order_id,
                    "amount_rupees": _rupees(c.amount_paise),
                    "gross_rupees": _rupees(payload.get("gross_amount_paise") or payload.get("amount_paise") or c.amount_paise),
                    "net_rupees": _rupees(payload.get("net_amount_paise") or c.amount_paise),
                    "event_date": str(c.event_date),
                    "batch_id": c.batch_id or payload.get("settlement_batch_id"),
                    "sku": sku,
                    "details": payload,
                }
            )

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "run_id": run.id,
        "results": [
            {
                "group_id": g.id,
                "tier": g.tier,
                "confidence": float(g.confidence or 0),
                "reason": g.reason,
                "members": member_map.get(g.id, []),
            }
            for g in groups
        ],
    }


@router.get("/exceptions")
async def list_exceptions(
    seller_id: str = Query(...),
    run_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    run = await _resolve_run(db, seller_id, run_id)
    if not run:
        return {"total": 0, "results": []}
    rows = (
        await db.execute(
            select(PaymentException, PaymentCanonical)
            .join(PaymentCanonical, PaymentException.canonical_id == PaymentCanonical.id)
            .where(PaymentException.run_id == run.id)
        )
    ).all()
    return {
        "run_id": run.id,
        "total": len(rows),
        "results": [
            {
                "exception_id": e.id,
                "source": c.source,
                "normalized_ref": c.normalized_ref,
                "amount_rupees": _rupees(c.amount_paise),
                "event_date": str(c.event_date),
                "reason_code": e.reason_code,
                "reason_text": e.reason_text,
                "sku": c.sku,
                "details": c.raw_payload or {},
            }
            for e, c in rows
        ],
    }


@router.get("/product/{product_id}")
async def product_cash(
    product_id: str,
    seller_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    """Payments analysis for one coffee SKU — sold vs settled vs exception."""
    seller_uuid = UUID(seller_id)
    pid = UUID(product_id)
    ledgers = list(
        (
            await db.execute(
                select(PaymentLedgerRow).where(
                    PaymentLedgerRow.seller_id == seller_uuid,
                    PaymentLedgerRow.product_id == pid,
                )
            )
        )
        .scalars()
        .all()
    )
    sold_paise = sum(r.amount_paise for r in ledgers)
    refs = {normalize_safe(r.order_id) for r in ledgers}

    run = await _resolve_run(db, seller_id, None)
    settled_paise = 0
    exception_paise = 0
    exception_count = 0
    if run and refs:
        canons = list(
            (
                await db.execute(
                    select(PaymentCanonical).where(
                        PaymentCanonical.run_id == run.id,
                        PaymentCanonical.product_id == pid,
                    )
                )
            )
            .scalars()
            .all()
        )
        matched_ids = set()
        members = (
            await db.execute(
                select(PaymentMatchMember.canonical_id).where(
                    PaymentMatchMember.canonical_id.in_([c.id for c in canons] or ["__none__"])
                )
            )
        ).scalars().all()
        matched_ids = set(members)
        for c in canons:
            if c.source == "ledger" and c.id in matched_ids:
                settled_paise += c.amount_paise
        excs = (
            await db.execute(
                select(PaymentException, PaymentCanonical)
                .join(PaymentCanonical, PaymentException.canonical_id == PaymentCanonical.id)
                .where(
                    PaymentException.run_id == run.id,
                    PaymentCanonical.product_id == pid,
                )
            )
        ).all()
        exception_count = len(excs)
        exception_paise = sum(c.amount_paise for _, c in excs if c.source == "ledger")

    return {
        "product_id": product_id,
        "order_count": len(ledgers),
        "sold_rupees": _rupees(sold_paise),
        "settled_rupees": _rupees(settled_paise),
        "exception_rupees": _rupees(exception_paise),
        "exception_count": exception_count,
        "run_id": run.id if run else None,
    }


@router.post("/ask")
async def ask_payments(
    body: AskRequest,
    seller_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    if seller_id != body.seller_id:
        raise HTTPException(status_code=403, detail="seller_id query must match request body")
    run = await _resolve_run(db, body.seller_id, body.run_id)
    if not run:
        return {
            "answer": "No Brew Boulevard reconciliation run yet. Open Payments and run recon first.",
            "cited_audit_log_ids": [],
        }
    audits = (
        await db.execute(
            select(PaymentAuditLog).where(PaymentAuditLog.run_id == run.id).limit(8)
        )
    ).scalars().all()
    excs = (
        await db.execute(
            select(PaymentException).where(PaymentException.run_id == run.id).limit(8)
        )
    ).scalars().all()
    ctx = {
        "run_id": run.id,
        "metrics": {
            "record_count": run.record_count,
            "match_rate": float(run.match_rate or 0),
            "exact_matches": run.exact_matches,
            "fuzzy_matches": run.fuzzy_matches,
            "ai_matches": run.ai_matches,
            "exception_count": run.exception_count,
        },
        "audit_logs": [{"id": a.id, "tier": a.tier, "action": a.action, "reason": (a.reason or "")[:180]} for a in audits],
        "exceptions": [{"reason_code": e.reason_code, "reason_text": e.reason_text} for e in excs],
    }
    return answer_payments_question(body.question, ctx)


async def _resolve_run(db: AsyncSession, seller_id: str, run_id: Optional[str]) -> Optional[PaymentReconRun]:
    if run_id:
        return (
            await db.execute(
                select(PaymentReconRun).where(
                    PaymentReconRun.id == run_id,
                    PaymentReconRun.seller_id == UUID(seller_id),
                )
            )
        ).scalar_one_or_none()
    return (
        await db.execute(
            select(PaymentReconRun)
            .where(
                PaymentReconRun.seller_id == UUID(seller_id),
                PaymentReconRun.status == "completed",
            )
            .order_by(PaymentReconRun.started_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()


def normalize_safe(ref: str) -> str:
    from app.services.payments.refs import normalize_ref_string
    return normalize_ref_string(ref)
