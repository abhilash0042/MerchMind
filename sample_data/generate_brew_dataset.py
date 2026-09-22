#!/usr/bin/env python3
"""
Generate brew_boulevard_demo.xlsx — upload via CommercePulse Data Import.

Sheets: Orders, Inventory, Pricing, Traffic, Logistics, Settlements, Bank
All order IDs use BB-ORD-* so product + payments analysis join on the same coffee brand.
"""
from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SEED = 42
OUTPUT = Path(__file__).resolve().parent / "brew_boulevard_demo.xlsx"
SNAPSHOT = date(2026, 3, 12)

PRODUCTS = [
    ("BB-CF-001", "Artisan Cold Brew Concentrate", 549, 220, "Cold Brew"),
    ("BB-CF-002", "Single-Origin Espresso Roast", 495, 210, "Whole Bean"),
    ("BB-CF-003", "French Press Classic Blend", 399, 165, "Ground Coffee"),
    ("BB-CF-004", "Pour Over Drip Bags", 299, 120, "Drip Bags"),
    ("BB-CF-005", "Vanilla Hazelnut Instant", 349, 140, "Instant Coffee"),
    ("BB-CF-006", "Decaf Colombian Roast", 490, 200, "Whole Bean"),
    ("BB-GR-007", "Ground Roast Coffee 500g", 449, 180, "Ground Coffee"),
    ("BB-CB-008", "Cold Brew Blend 1L", 599, 240, "Cold Brew"),
    ("BB-WB-009", "Whole Bean Coffee 250g", 525, 215, "Whole Bean"),
    ("BB-IN-010", "Premium Instant Coffee 100g", 299, 115, "Instant Coffee"),
]

MARKETPLACES = [
    ("shopify", 0.0, ["upi", "card", "razorpay"]),
    ("amazon_in", 15.0, ["prepaid"]),
    ("flipkart", 14.0, ["prepaid", "cod"]),
]

COURIERS = ["Bluedart", "Delhivery", "Xpressbees", "DTDC"]
WAREHOUSES = ["BLR-WH1", "BOM-WH1", "DEL-WH2"]


def rupees_to_paise(v: float) -> int:
    return int(round(v * 100))


def fee_split(gross_paise: int) -> tuple[int, int, int]:
    fee = int(round(gross_paise * 0.02))
    gst = int(round(fee * 0.18))
    return fee, gst, gross_paise - fee - gst


def messy_narration(utr: str, batch_id: str, rng: random.Random) -> str:
    templates = [
        f"NEFT/CMS/RAZORPAY/{utr}/SETTLEMENT",
        f"ACH CR-RAZORPAY SOFTWARE PRIVATE LIMITED-{utr}-SETL",
        f"CMS-RAZORPAY SETTLEMENT {batch_id} UTR:{utr}",
        f"NEFT CR-{utr}-RAZORPAY-{batch_id}",
    ]
    return rng.choice(templates)


def build_orders(rng: random.Random) -> pd.DataFrame:
    rows = []
    order_num = 10001
    start = date(2026, 1, 5)
    end = date(2026, 3, 10)

    for _ in range(180):
        sku, _name, base_price, cost, _cat = rng.choice(PRODUCTS)
        mp, _comm, payments = rng.choice(MARKETPLACES)
        qty = rng.choice([1, 1, 1, 2, 2, 3])
        discount = round(base_price * qty * rng.uniform(0, 0.12), 2)
        selling = round(base_price * qty - discount, 2)
        tax = round(selling * 0.18, 2)
        ship = round(rng.uniform(0, 99), 2)
        order_date = start + timedelta(days=rng.randint(0, (end - start).days))

        roll = rng.random()
        if roll < 0.06:
            status, ret, cancel = "cancelled", False, "Customer request"
            delivery = None
        elif roll < 0.10:
            status, ret, cancel = "returned", True, ""
            delivery = None
        else:
            status, ret, cancel = "delivered", False, ""
            delivery = order_date + timedelta(days=rng.randint(2, 7))

        rows.append(
            {
                "Order ID": f"BB-ORD-{order_num}",
                "Marketplace": mp,
                "SKU": sku,
                "Status": status,
                "Quantity": qty,
                "Selling Price": selling,
                "Cost Price": round(cost * qty, 2),
                "Discount": discount,
                "Tax": tax,
                "Shipping Fee": ship,
                "Order Date": order_date,
                "Delivery Date": delivery,
                "Return": ret,
                "Cancellation Reason": cancel,
                "Payment Mode": rng.choice(payments) if mp == "shopify" else rng.choice(payments),
                "Customer Name": rng.choice(["Aarav S.", "Priya M.", "Rohan K.", "Ananya D.", "Vikram P."]),
            }
        )
        order_num += 1

    return pd.DataFrame(rows)


def build_inventory() -> pd.DataFrame:
    rows = []
    for sku, _n, price, _c, _cat in PRODUCTS:
        for mp, _comm, _p in MARKETPLACES:
            stock = random.randint(15, 420)
            reserved = random.randint(0, min(20, stock // 5))
            rows.append(
                {
                    "SKU": sku,
                    "Marketplace": mp,
                    "Available Stock": stock,
                    "Reserved Stock": reserved,
                    "Reorder Threshold": random.randint(20, 80),
                    "Days of Stock": round(random.uniform(5, 90), 1),
                    "Warehouse": random.choice(WAREHOUSES),
                    "Snapshot Date": SNAPSHOT,
                }
            )
    return pd.DataFrame(rows)


def build_pricing() -> pd.DataFrame:
    rows = []
    for sku, _n, sell, cost, _cat in PRODUCTS:
        for mp, comm_pct, _p in MARKETPLACES:
            comm_amt = round(sell * comm_pct / 100, 2)
            margin = round((sell - cost - comm_amt) / sell * 100, 2) if sell else 0
            rows.append(
                {
                    "SKU": sku,
                    "Marketplace": mp,
                    "Selling Price": sell,
                    "Cost Price": cost,
                    "MRP": round(sell * 1.25, 2),
                    "Commission %": comm_pct,
                    "Commission Amount": comm_amt,
                    "Discount %": round(random.uniform(5, 18), 2),
                    "Net Margin": round(sell - cost - comm_amt, 2),
                    "Margin %": margin,
                    "Snapshot Date": SNAPSHOT,
                }
            )
    return pd.DataFrame(rows)


def build_traffic(rng: random.Random) -> pd.DataFrame:
    rows = []
    for sku, _n, sell, _c, _cat in PRODUCTS:
        for mp, _comm, _p in MARKETPLACES:
            for day_offset in range(14):
                d = SNAPSHOT - timedelta(days=day_offset)
                impressions = rng.randint(800, 12000)
                clicks = max(1, int(impressions * rng.uniform(0.02, 0.08)))
                orders = rng.randint(0, max(1, clicks // 8))
                spend = round(rng.uniform(200, 3500), 2)
                rev = round(orders * sell * rng.uniform(0.8, 1.1), 2)
                rows.append(
                    {
                        "SKU": sku,
                        "Marketplace": mp,
                        "Date": d,
                        "Impressions": impressions,
                        "Clicks": clicks,
                        "Sessions": int(clicks * rng.uniform(0.7, 1.2)),
                        "Page Views": int(clicks * rng.uniform(1.1, 2.5)),
                        "Orders": orders,
                        "Ad Spend": spend,
                        "Revenue from Ads": rev,
                    }
                )
    return pd.DataFrame(rows)


def build_logistics(orders: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    rows = []
    sample = orders[orders["Status"].isin(["delivered", "returned"])].head(120)
    for _, o in sample.iterrows():
        od = o["Order Date"]
        if isinstance(od, str):
            od = date.fromisoformat(od[:10])
        dispatch = od + timedelta(days=1)
        expected = dispatch + timedelta(days=rng.randint(2, 6))
        actual = expected if o["Status"] == "delivered" else None
        rows.append(
            {
                "Order ID": o["Order ID"],
                "Marketplace": o["Marketplace"],
                "Courier": rng.choice(COURIERS),
                "Tracking ID": f"TRK{rng.randint(100000, 999999)}",
                "Fulfillment Type": rng.choice(["seller", "marketplace"]),
                "Warehouse ID": rng.choice(WAREHOUSES),
                "Dispatch Date": dispatch,
                "Expected Delivery": expected,
                "Actual Delivery": actual,
                "Delivery Status": "delivered" if o["Status"] == "delivered" else "rto",
                "RTO": o["Return"],
                "RTO Reason": "Customer refused" if o["Return"] else "",
                "Snapshot Date": SNAPSHOT,
            }
        )
    return pd.DataFrame(rows)


def build_settlements_and_bank(orders: pd.DataFrame, rng: random.Random) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Razorpay STL + bank credits for Shopify orders only (same BB-ORD ids)."""
    shopify = orders[
        (orders["Marketplace"].str.lower() == "shopify")
        & (orders["Status"] == "delivered")
    ].copy()

    skip = set()
    for idx in shopify.index:
        if rng.random() < 0.08:
            skip.add(idx)

    by_date: dict[date, list] = defaultdict(list)
    for idx, row in shopify.iterrows():
        if idx in skip:
            continue
        od = row["Order Date"]
        if isinstance(od, str):
            od = date.fromisoformat(str(od)[:10])
        by_date[od].append(row)

    settlement_rows = []
    bank_rows = []
    batch_n = 1001
    dates_sorted = sorted(by_date.keys())
    i = 0
    while i < len(dates_sorted):
        chunk = dates_sorted[i : i + rng.randint(1, 2)]
        i += len(chunk)
        members = []
        for d in chunk:
            members.extend(by_date[d])
        if not members:
            continue
        batch_id = f"STL-BB-{batch_n}"
        batch_n += 1
        settle_day = max(chunk) + timedelta(days=2)
        utr = f"UTR{settle_day.strftime('%y%m%d')}{rng.randint(1000, 9999)}RZP"
        batch_net_paise = 0
        for row in members:
            gross_p = rupees_to_paise(float(row["Selling Price"]))
            fee_p, gst_p, net_p = fee_split(gross_p)
            batch_net_paise += net_p
            order_ref = row["Order ID"]
            if rng.random() < 0.06:
                order_ref = order_ref.replace("-", " ").lower()
            settlement_rows.append(
                {
                    "Settlement Batch ID": batch_id,
                    "UTR": utr,
                    "Order Ref": order_ref,
                    "SKU": row["SKU"],
                    "Gross Amount": round(gross_p / 100, 2),
                    "Fee Amount": round(fee_p / 100, 2),
                    "GST on Fee": round(gst_p / 100, 2),
                    "Net Amount": round(net_p / 100, 2),
                    "Settlement Date": settle_day,
                }
            )
        if rng.random() > 0.05:
            bank_rows.append(
                {
                    "Bank Txn ID": f"BNK-BB-{batch_n}{rng.randint(10, 99)}",
                    "Value Date": settle_day,
                    "Credit Amount": round(batch_net_paise / 100, 2),
                    "Narration": messy_narration(utr, batch_id, rng),
                }
            )

    return pd.DataFrame(settlement_rows), pd.DataFrame(bank_rows)


def main() -> None:
    rng = random.Random(SEED)
    random.seed(SEED)

    orders = build_orders(rng)
    inventory = build_inventory()
    pricing = build_pricing()
    traffic = build_traffic(rng)
    logistics = build_logistics(orders, rng)
    settlements, bank = build_settlements_and_bank(orders, rng)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        orders.to_excel(writer, sheet_name="Orders", index=False)
        inventory.to_excel(writer, sheet_name="Inventory", index=False)
        pricing.to_excel(writer, sheet_name="Pricing", index=False)
        traffic.to_excel(writer, sheet_name="Traffic", index=False)
        logistics.to_excel(writer, sheet_name="Logistics", index=False)
        settlements.to_excel(writer, sheet_name="Settlements", index=False)
        bank.to_excel(writer, sheet_name="Bank", index=False)

    print(f"Wrote {OUTPUT}")
    print(f"  Orders: {len(orders)} | Settlements: {len(settlements)} | Bank: {len(bank)}")
    print(f"  Shopify delivered (Razorpay-eligible): {len(orders[(orders['Marketplace']=='shopify') & (orders['Status']=='delivered')])}")


if __name__ == "__main__":
    main()
