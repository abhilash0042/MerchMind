"""Ingest settlement / bank Excel sheets into payment raw tables."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Dict
from uuid import UUID

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import PaymentBankRow, PaymentSettlementRow
from app.services.payments.refs import rupees_to_paise


def _col(df: pd.DataFrame, *names: str):
    lower = {str(c).strip().lower().replace("_", " "): c for c in df.columns}
    for n in names:
        key = n.lower().replace("_", " ")
        if key in lower:
            return lower[key]
    for k, orig in lower.items():
        for n in names:
            if n.lower().replace("_", " ") in k:
                return orig
    return None


def _as_date(val) -> date:
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    return date.fromisoformat(str(val)[:10])


async def ingest_settlements(db: AsyncSession, df: pd.DataFrame, seller_id: str) -> Dict[str, Any]:
    seller_uuid = UUID(str(seller_id))
    batch_c = _col(df, "settlement_batch_id", "batch id", "stl", "settlement id")
    utr_c = _col(df, "utr")
    ref_c = _col(df, "order_ref", "order id", "order_id", "external_order_id")
    gross_c = _col(df, "gross_amount_paise", "gross", "gross amount")
    fee_c = _col(df, "fee_amount_paise", "fee", "mdr")
    gst_c = _col(df, "gst_on_fee_paise", "gst")
    net_c = _col(df, "net_amount_paise", "net", "net amount")
    date_c = _col(df, "settlement_date", "date")
    sku_c = _col(df, "sku")
    if not ref_c:
        return {"ingested": 0, "error": "Settlements sheet needs order_ref / order id"}

    rows = []
    for _, r in df.iterrows():
        gross = r.get(gross_c) if gross_c else None
        net = r.get(net_c) if net_c else None
        gross_p = int(gross) if gross_c and str(gross).replace(".", "", 1).isdigit() and float(gross) > 500 else rupees_to_paise(gross or 0)
        net_p = int(net) if net_c and net is not None and float(net) > 500 else rupees_to_paise(net or 0)
        if gross_p < 50:
            continue
        fee_p = int(r.get(fee_c) or round(gross_p * 0.02)) if fee_c else int(round(gross_p * 0.02))
        gst_p = int(r.get(gst_c) or round(fee_p * 0.18)) if gst_c else int(round(fee_p * 0.18))
        if net_p < 50:
            net_p = gross_p - fee_p - gst_p
        settle_d = _as_date(r.get(date_c)) if date_c and pd.notna(r.get(date_c)) else date.today()
        rows.append(
            PaymentSettlementRow(
                seller_id=seller_uuid,
                settlement_batch_id=str(r.get(batch_c) or "STL-BB-0000"),
                utr=str(r.get(utr_c) or ""),
                order_ref=str(r.get(ref_c)),
                sku=str(r.get(sku_c)) if sku_c and pd.notna(r.get(sku_c)) else None,
                gross_amount_paise=gross_p,
                fee_amount_paise=fee_p,
                gst_on_fee_paise=gst_p,
                net_amount_paise=net_p,
                settlement_date=settle_d,
            )
        )
    db.add_all(rows)
    await db.commit()
    return {"ingested": len(rows)}


async def ingest_bank(db: AsyncSession, df: pd.DataFrame, seller_id: str) -> Dict[str, Any]:
    seller_uuid = UUID(str(seller_id))
    txn_c = _col(df, "bank_txn_id", "txn id", "transaction id")
    date_c = _col(df, "value_date", "date")
    amt_c = _col(df, "credit_amount_paise", "credit", "amount")
    narr_c = _col(df, "narration", "description")
    rows = []
    for _, r in df.iterrows():
        raw_amt = r.get(amt_c) if amt_c else 0
        try:
            amt = float(raw_amt)
            paise = int(round(amt)) if amt > 500 else rupees_to_paise(amt)
        except (TypeError, ValueError):
            continue
        rows.append(
            PaymentBankRow(
                seller_id=seller_uuid,
                bank_txn_id=str(r.get(txn_c) or f"BNK-{uuid.uuid4().hex[:10].upper()}"),
                value_date=_as_date(r.get(date_c)) if date_c and pd.notna(r.get(date_c)) else date.today(),
                credit_amount_paise=paise,
                narration=str(r.get(narr_c) or ""),
            )
        )
    db.add_all(rows)
    await db.commit()
    return {"ingested": len(rows)}
