"""Derive Razorpay ledger / STL / bank rows from Brew Boulevard Pulse orders."""
from __future__ import annotations

import random
import uuid
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Dict
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Order,
    Product,
    PaymentBankRow,
    PaymentLedgerRow,
    PaymentSettlementRow,
)
from app.services.payments.noise import generate_messy_narration, inject_amount_drift, inject_ref_typo
from app.services.payments.refs import razorpay_fee_split, rupees_to_paise


def _is_razorpay_eligible(order: Order) -> bool:
    mp = (order.marketplace or "").lower()
    pm = (order.payment_mode or "").lower()
    if any(x in mp for x in ("shopify", "d2c", "website", "direct", "own")):
        return True
    if any(x in pm for x in ("upi", "card", "razorpay", "netbanking", "wallet")):
        return True
    return False


async def clear_raw_cash(db: AsyncSession, seller_uuid: UUID) -> None:
    await db.execute(delete(PaymentBankRow).where(PaymentBankRow.seller_id == seller_uuid))
    await db.execute(delete(PaymentSettlementRow).where(PaymentSettlementRow.seller_id == seller_uuid))
    await db.execute(delete(PaymentLedgerRow).where(PaymentLedgerRow.seller_id == seller_uuid))


async def seed_cash_from_orders(db: AsyncSession, seller_id: str, seed: int = 42) -> Dict[str, Any]:
    seller_uuid = UUID(str(seller_id))
    rng = random.Random(seed)

    result = await db.execute(
        select(Order).where(Order.seller_id == seller_uuid).order_by(Order.order_date.asc())
    )
    orders = list(result.scalars().all())
    if not orders:
        return {"status": "empty", "message": "No Brew Boulevard orders to build a cash ledger from."}

    eligible = [o for o in orders if _is_razorpay_eligible(o)]
    if len(eligible) < 15:
        eligible = [
            o for o in orders
            if (o.order_status or "").lower() not in ("cancelled", "canceled")
        ]
    if not eligible:
        eligible = orders

    products = {}
    pids = {o.product_id for o in eligible if o.product_id}
    if pids:
        pres = await db.execute(select(Product).where(Product.product_id.in_(list(pids))))
        products = {p.product_id: p for p in pres.scalars().all()}

    await clear_raw_cash(db, seller_uuid)

    ledger_rows: list[PaymentLedgerRow] = []
    for o in eligible:
        ext = o.external_order_id or f"BB-ORD-{str(o.order_id)[:8]}"
        prod = products.get(o.product_id) if o.product_id else None
        status = "refunded" if o.return_flag else ((o.order_status or "captured").lower())
        if status in ("delivered", "shipped", "completed"):
            status = "captured"
        ledger_rows.append(
            PaymentLedgerRow(
                seller_id=seller_uuid,
                order_id=str(ext),
                product_id=o.product_id,
                sku=(prod.sku if prod else None),
                marketplace=o.marketplace,
                order_date=o.order_date,
                amount_paise=rupees_to_paise(o.selling_price),
                payment_method=(o.payment_mode or "upi").lower(),
                status=status,
            )
        )
    db.add_all(ledger_rows)
    await db.flush()

    skip_stl = set()
    for row in ledger_rows:
        if row.status == "refunded" and rng.random() < 0.55:
            skip_stl.add(row.id)
        elif rng.random() < 0.06:
            skip_stl.add(row.id)

    by_date: Dict[date, list] = defaultdict(list)
    for row in ledger_rows:
        if row.id in skip_stl:
            continue
        by_date[row.order_date].append(row)

    settlement_rows: list[PaymentSettlementRow] = []
    bank_rows: list[PaymentBankRow] = []
    batch_n = 1001
    dates_sorted = sorted(by_date.keys())
    i = 0
    while i < len(dates_sorted):
        chunk_dates = dates_sorted[i : i + rng.randint(1, 2)]
        i += len(chunk_dates)
        members = []
        for d in chunk_dates:
            members.extend(by_date[d])
        if not members:
            continue
        batch_id = f"STL-BB-{batch_n}"
        batch_n += 1
        settle_day = max(chunk_dates) + timedelta(days=2)
        utr = f"UTR{settle_day.strftime('%y%m%d')}{rng.randint(1000, 9999)}RZP"
        batch_net = 0
        for row in members:
            fee, gst, net = razorpay_fee_split(row.amount_paise)
            if rng.random() < 0.12:
                net = inject_amount_drift(net, rng)
                fee, gst, _ = razorpay_fee_split(row.amount_paise)
            order_ref = row.order_id
            if rng.random() < 0.08:
                order_ref = inject_ref_typo(order_ref, rng)
            settlement_rows.append(
                PaymentSettlementRow(
                    seller_id=seller_uuid,
                    settlement_batch_id=batch_id,
                    utr=utr,
                    order_ref=order_ref,
                    sku=row.sku,
                    product_id=row.product_id,
                    gross_amount_paise=row.amount_paise,
                    fee_amount_paise=fee,
                    gst_on_fee_paise=gst,
                    net_amount_paise=net,
                    settlement_date=settle_day,
                )
            )
            batch_net += net
        if rng.random() > 0.04:
            bank_rows.append(
                PaymentBankRow(
                    seller_id=seller_uuid,
                    bank_txn_id=f"BNK-BB-{uuid.uuid4().hex[:10].upper()}",
                    value_date=settle_day,
                    credit_amount_paise=batch_net,
                    narration=generate_messy_narration(utr, batch_id, rng),
                )
            )

    db.add_all(settlement_rows)
    db.add_all(bank_rows)
    await db.commit()

    return {
        "status": "ok",
        "brand": "Brew Boulevard",
        "ledger_count": len(ledger_rows),
        "settlement_count": len(settlement_rows),
        "bank_count": len(bank_rows),
        "intentionally_unsettled": len(skip_stl),
        "fee_model": "2% Razorpay MDR + 18% GST on fee, T+2",
    }
