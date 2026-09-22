"""
Excel Ingestion Service
Parses uploaded Excel sheets and bulk-inserts into PostgreSQL.
Each domain has its own parser that maps flexible column names to DB columns.
"""
import io
import logging
import uuid
from datetime import date, datetime, timedelta  # timedelta consolidated here (Bug 2)
from typing import Optional

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.models import (
    Product, Order, InventorySnapshot, PricingSnapshot,
    TrafficMetric, LogisticsMetric,
)

# Bug 1 Fix: logger was missing — caused NameError on any row exception
logger = logging.getLogger(__name__)


# ── Column aliases ─────────────────────────────────────────────
# Maps flexible Excel column names → canonical DB column name
ORDER_COL_MAP = {
    "order id": "external_order_id", "order_id": "external_order_id", "id": "external_order_id",
    "marketplace": "marketplace", "platform": "marketplace", "channel": "marketplace",
    "sku": "sku", "product sku": "sku", "item sku": "sku",
    "status": "order_status", "order_status": "order_status", "order status": "order_status",
    "quantity": "quantity", "qty": "quantity", "qty.": "quantity",
    "selling price": "selling_price", "selling_price": "selling_price", "price": "selling_price", "amount": "selling_price",
    "discount": "discount",
    "tax": "tax",
    "shipping fee": "shipping_fee", "shipping_fee": "shipping_fee", "shipping": "shipping_fee",
    "order date": "order_date", "order_date": "order_date", "date": "order_date",
    "delivery date": "delivery_date", "delivery_date": "delivery_date",
    "return": "return_flag", "return_flag": "return_flag",
    "cancellation reason": "cancellation_reason", "cancellation_reason": "cancellation_reason",
    # Customer / payment fields (may be absent — handled gracefully)
    "customer name": "customer_name", "customer_name": "customer_name",
    "customer email": "customer_email", "customer_email": "customer_email",
    "payment mode": "payment_mode", "payment_mode": "payment_mode", "payment": "payment_mode",
    "customer city": "customer_city", "customer_city": "customer_city",
    "customer state": "customer_state", "customer_state": "customer_state",
}

INVENTORY_COL_MAP = {
    "sku": "sku", "product sku": "sku",
    "marketplace": "marketplace",
    "available stock": "available_stock", "available_stock": "available_stock", "stock": "available_stock",
    "reserved stock": "reserved_stock", "reserved_stock": "reserved_stock",
    "reorder threshold": "reorder_threshold", "reorder_threshold": "reorder_threshold",
    "days of stock": "days_of_stock", "days_of_stock": "days_of_stock",
    "warehouse": "warehouse_location", "warehouse_location": "warehouse_location",
    "snapshot date": "snapshot_date", "snapshot_date": "snapshot_date", "date": "snapshot_date",
}

PRICING_COL_MAP = {
    "sku": "sku", "product sku": "sku",
    "marketplace": "marketplace",
    "selling price": "selling_price", "selling_price": "selling_price",
    "cost price": "cost_price", "cost_price": "cost_price",
    "mrp": "mrp",
    "commission %": "commission_pct", "commission_pct": "commission_pct",
    "commission amount": "commission_amount", "commission_amount": "commission_amount",
    "discount %": "discount_percentage", "discount_percentage": "discount_percentage",
    "snapshot date": "snapshot_date", "date": "snapshot_date",
}

TRAFFIC_COL_MAP = {
    "sku": "sku", "product sku": "sku",
    "marketplace": "marketplace",
    "date": "metric_date", "metric date": "metric_date", "metric_date": "metric_date",
    "impressions": "impressions",
    "clicks": "clicks",
    "sessions": "sessions",
    "page views": "page_views", "page_views": "page_views",
    "orders": "orders",
    "ad spend": "ad_spend", "ad_spend": "ad_spend",
    "revenue from ads": "revenue_from_ads", "revenue_from_ads": "revenue_from_ads",
}

LOGISTICS_COL_MAP = {
    "order id": "external_order_id", "order_id": "external_order_id",
    "marketplace": "marketplace",
    "courier": "courier_name", "courier_name": "courier_name",
    "carrier": "courier_name",                             # test_dataset alias
    "tracking id": "tracking_id", "tracking_id": "tracking_id",
    "shipment id": "tracking_id", "shipment_id": "tracking_id",  # test_dataset alias
    "fulfillment type": "fulfillment_type", "fulfillment_type": "fulfillment_type",
    "warehouse id": "warehouse_id", "warehouse_id": "warehouse_id",
    "dispatch date": "dispatch_date", "dispatch_date": "dispatch_date",
    "expected delivery": "expected_delivery",
    "estimated delivery": "expected_delivery", "estimated_delivery": "expected_delivery",  # test_dataset alias
    "actual delivery": "actual_delivery", "actual_delivery": "actual_delivery",
    "delivery status": "delivery_status", "delivery_status": "delivery_status", "status": "delivery_status",
    "rto": "rto_flag", "rto_flag": "rto_flag",
    "rto reason": "rto_reason", "rto_reason": "rto_reason",
    "snapshot date": "snapshot_date", "date": "snapshot_date",
    "shipping cost": "_shipping_cost", "shipping_cost": "_shipping_cost",  # ignored safely
}


# ── Helpers ────────────────────────────────────────────────────

def _normalise_columns(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """Lower-case, replace underscores with spaces, and intelligently map columns."""
    rename = {}
    for original_col in df.columns:
        c = str(original_col).strip().lower()
        c_space = c.replace("_", " ")

        # 1. Exact match
        if c in col_map:
            rename[original_col] = col_map[c]
            continue
            
        # 2. Match after replacing underscore
        if c_space in col_map:
            rename[original_col] = col_map[c_space]
            continue
            
        # 3. Fuzzy Heuristic Substring Match for critical columns
        if "sku" in c:
            rename[original_col] = "sku"
        elif "qty" in c or "quantity" in c:
            rename[original_col] = "quantity"
        elif "price" in c and ("sell" in c or "selling" in c):
            rename[original_col] = "selling_price"
        elif "price" in c and "cost" in c:
            rename[original_col] = "cost_price"
        elif "mrp" in c:
            rename[original_col] = "mrp"
        elif "market" in c or "platform" in c or "channel" in c:
            rename[original_col] = "marketplace"
        elif "order" in c and "id" in c:
            rename[original_col] = "external_order_id"
        elif "shipment" in c and "id" in c:
            rename[original_col] = "tracking_id"
        elif "stock" in c and "avail" in c:
            rename[original_col] = "available_stock"
        elif "stock" in c and "reserv" in c:
            rename[original_col] = "reserved_stock"
        elif "stock" in c:
            rename[original_col] = "available_stock" # fallback
        elif "spend" in c and "ad" in c:
            rename[original_col] = "ad_spend"
        elif "return" in c and "ad" in c:
            rename[original_col] = "revenue_from_ads"
        elif "carrier" in c:
            rename[original_col] = "courier_name"
        elif "estimated" in c and "deliver" in c:
            rename[original_col] = "expected_delivery"
            
    return df.rename(columns=rename)


# timedelta import moved to top of file (Bug 2 fix — duplicate removed)

def _parse_date(val) -> Optional[date]:
    if pd.isna(val):
        return None
    if isinstance(val, (date, datetime)):
        return val if isinstance(val, date) else val.date()
    
    # Handle Excel serial dates (floats)
    try:
        if isinstance(val, (int, float)) or (isinstance(val, str) and val.replace('.','',1).isdigit()):
            float_val = float(val)
            # Excel dates are days since Dec 30, 1899
            return (datetime(1899, 12, 30) + timedelta(days=float_val)).date()
    except Exception:
        pass

    try:
        return pd.to_datetime(val).date()
    except Exception:
        return None


def _safe_float(val, default=0.0) -> float:
    try:
        return float(val) if not pd.isna(val) else default
    except Exception:
        return default


def _safe_int(val, default=0) -> int:
    try:
        return int(val) if not pd.isna(val) else default
    except Exception:
        return default


async def _resolve_products_batch(db: AsyncSession, seller_id: str, skus: list[str], marketplaces: list[str], product_cache: dict):
    """
    Efficiently resolves a list of (sku, marketplace) pairs to product_ids in batches.
    """
    # Filter out what's already in cache
    missing_keys = []
    seen_keys = set()
    for s, m in zip(skus, marketplaces):
        key = (s, m)
        if key not in product_cache and key not in seen_keys:
            missing_keys.append(key)
            seen_keys.add(key)
    
    if not missing_keys:
        return

    # Step 1: Query existing products
    # We use a tuple-based IN clause for (sku, marketplace)
    from sqlalchemy import tuple_
    result = await db.execute(
        select(Product.product_id, Product.sku, Product.marketplace).where(
            Product.seller_id == seller_id,
            tuple_(Product.sku, Product.marketplace).in_(missing_keys)
        )
    )
    
    found_keys = set()
    for row in result:
        key = (row.sku, row.marketplace)
        product_cache[key] = str(row.product_id)
        found_keys.add(key)
    
    # Step 2: Bulk-insert missing products
    really_missing = [k for k in missing_keys if k not in found_keys]
    if really_missing:
        new_products = [
            Product(
                seller_id=seller_id,
                sku=sku,
                product_name=sku,
                marketplace=m,
                is_active=True
            ) for sku, m in really_missing
        ]
        db.add_all(new_products)
        await db.flush()
        
        for p in new_products:
            product_cache[(p.sku, p.marketplace)] = str(p.product_id)

async def _resolve_product(db: AsyncSession, seller_id: str, sku: str, marketplace: str, product_cache: dict) -> Optional[str]:
    """Single resolve fallback (uses batch logic internally)."""
    cache_key = (sku, marketplace)
    if cache_key in product_cache:
        return product_cache[cache_key]
    
    await _resolve_products_batch(db, seller_id, [sku], [marketplace], product_cache)
    return product_cache.get(cache_key)


# ── Domain Parsers ──────────────────────────────────────────────

async def ingest_orders(db: AsyncSession, df: pd.DataFrame, seller_id: str, snapshot_date: date) -> dict:
    df = _normalise_columns(df, ORDER_COL_MAP)

    rows_inserted = 0
    rows_skipped  = 0
    product_cache = {}
    
    # Pre-warm product cache in one batch
    skus = df.get("sku", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    marketplaces = df.get("marketplace", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    await _resolve_products_batch(db, seller_id, skus, marketplaces, product_cache)

    values_list = []
    
    for row in df.itertuples(index=False):
        row_dict = row._asdict()
        try:
            sku         = str(row_dict.get("sku", "")).strip()
            if not sku or sku == "nan":
                sku = "UNKNOWN-SKU"
                
            marketplace = str(row_dict.get("marketplace", "unknown")).strip()
            product_id = await _resolve_product(db, seller_id, sku, marketplace, product_cache)

            # Handle return_flag — may be string 'True'/'False' or bool
            raw_return = row_dict.get("return_flag", False)
            if isinstance(raw_return, str):
                return_flag = raw_return.strip().lower() in ("true", "1", "yes")
            else:
                return_flag = bool(raw_return)

            values_list.append({
                "external_order_id":   str(row_dict.get("external_order_id", "")) or None,
                "seller_id":           seller_id,
                "product_id":          product_id,
                "marketplace":         marketplace,
                "order_status":        str(row_dict.get("order_status", "unknown")),
                "quantity":            _safe_int(row_dict.get("quantity"), 1),
                "selling_price":       _safe_float(row_dict.get("selling_price")),
                "discount":            _safe_float(row_dict.get("discount")),
                "tax":                 _safe_float(row_dict.get("tax")),
                "shipping_fee":        _safe_float(row_dict.get("shipping_fee")),
                "order_date":          _parse_date(row_dict.get("order_date")) or snapshot_date,
                "delivery_date":       _parse_date(row_dict.get("delivery_date")),
                "return_flag":         return_flag,
                "cancellation_reason": str(row_dict.get("cancellation_reason", "")) or None,
                "customer_name":       str(row_dict.get("customer_name", "")).strip() or None,
                "customer_email":      str(row_dict.get("customer_email", "")).strip() or None,
                "payment_mode":        str(row_dict.get("payment_mode", "")).strip() or None,
                "snapshot_date":       snapshot_date,
            })
            rows_inserted += 1
        except Exception as e:
            logger.warning(f"Error skipping row in orders: {e}")
            rows_skipped += 1

    if values_list:
        # Deduplicate values list based on ON CONFLICT key
        seen = {}
        no_eid = []
        for v in values_list:
            if v.get("external_order_id"):
                seen[v["external_order_id"]] = v
            else:
                no_eid.append(v)
        values_list = list(seen.values()) + no_eid
        
        # Split into two paths: rows WITH an external_order_id (upsert) and
        # rows WITHOUT one (plain insert) to avoid NULL conflict key issues.
        with_eid = [v for v in values_list if v.get("external_order_id")]
        without_eid = [v for v in values_list if not v.get("external_order_id")]

        for i in range(0, len(with_eid), 1000):
            stmt = pg_insert(Order).values(with_eid[i:i+1000]).on_conflict_do_update(
                index_elements=["external_order_id"],
                index_where=Order.external_order_id.isnot(None),
                set_={
                    "order_status": pg_insert(Order).excluded.order_status,
                    "delivery_date": pg_insert(Order).excluded.delivery_date,
                },
            )
            await db.execute(stmt)

        for i in range(0, len(without_eid), 1000):
            await db.execute(pg_insert(Order).values(without_eid[i:i+1000]).on_conflict_do_nothing())

    await db.commit()
    return {"inserted": rows_inserted, "skipped": rows_skipped, "domain": "orders"}


async def ingest_inventory(db: AsyncSession, df: pd.DataFrame, seller_id: str, snapshot_date: date) -> dict:
    df = _normalise_columns(df, INVENTORY_COL_MAP)

    rows_inserted = 0
    rows_skipped  = 0
    product_cache = {}
    
    # Pre-warm product cache in one batch
    skus = df.get("sku", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    marketplaces = df.get("marketplace", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    await _resolve_products_batch(db, seller_id, skus, marketplaces, product_cache)

    # Enrich Product records if Inventory sheet has product_name/category
    has_product_name = "product_name" in df.columns
    has_category     = "category" in df.columns
    if has_product_name or has_category:
        for row in df.itertuples(index=False):
            row_dict = row._asdict()
            sku = str(row_dict.get("sku", "")).strip()
            marketplace = str(row_dict.get("marketplace", "unknown")).strip()
            cache_key = (sku, marketplace)
            pid = product_cache.get(cache_key)
            if not pid:
                continue
            updates = {}
            if has_product_name:
                pname = str(row_dict.get("product_name", "")).strip()
                if pname and pname != "nan":
                    updates["product_name"] = pname
            if has_category:
                cat = str(row_dict.get("category", "")).strip()
                if cat and cat != "nan":
                    updates["category"] = cat
            if updates:
                from sqlalchemy import update
                await db.execute(
                    update(Product).where(Product.product_id == pid).values(**updates)
                )
        await db.flush()

    values_list = []

    # Use itertuples for massive speedup
    for row in df.itertuples(index=False):
        row_dict = row._asdict()
        try:
            sku         = str(row_dict.get("sku", "")).strip()
            if not sku or sku == "nan":
                sku = "UNKNOWN-SKU"
                
            marketplace = str(row_dict.get("marketplace", "unknown")).strip()

            product_id = await _resolve_product(db, seller_id, sku, marketplace, product_cache)
            snap_date  = _parse_date(row_dict.get("snapshot_date")) or snapshot_date

            values_list.append({
                "seller_id":         seller_id,
                "product_id":        product_id,
                "marketplace":       marketplace,
                "available_stock":   _safe_int(row_dict.get("available_stock")),
                "reserved_stock":    _safe_int(row_dict.get("reserved_stock")),
                "reorder_threshold": _safe_int(row_dict.get("reorder_threshold"), 10),
                "days_of_stock":     _safe_float(row_dict.get("days_of_stock")) or None,
                "warehouse_location": str(row_dict.get("warehouse_location", "")) or None,
                "snapshot_date":     snap_date,
            })
            rows_inserted += 1
        except Exception as e:
            logger.warning(f"Error skipping row in inventory: {e}")
            rows_skipped += 1

    if values_list:
        seen = {}
        for v in values_list:
            key = (v["seller_id"], v["product_id"], v["marketplace"], v["snapshot_date"])
            seen[key] = v
        values_list = list(seen.values())
        
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(InventorySnapshot).values(values_list[i:i+1000]).on_conflict_do_update(
                index_elements=["seller_id", "product_id", "marketplace", "snapshot_date"],
                set_={
                    "available_stock": pg_insert(InventorySnapshot).excluded.available_stock,
                    "reserved_stock": pg_insert(InventorySnapshot).excluded.reserved_stock,
                },
            )
            await db.execute(stmt)

    await db.commit()
    return {"inserted": rows_inserted, "skipped": rows_skipped, "domain": "inventory"}


async def ingest_pricing(db: AsyncSession, df: pd.DataFrame, seller_id: str, snapshot_date: date) -> dict:
    df = _normalise_columns(df, PRICING_COL_MAP)

    rows_inserted = 0
    rows_skipped  = 0
    product_cache = {}
    
    # Pre-warm product cache in one batch
    skus = df.get("sku", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    marketplaces = df.get("marketplace", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    await _resolve_products_batch(db, seller_id, skus, marketplaces, product_cache)

    values_list = []

    for row in df.itertuples(index=False):
        row_dict = row._asdict()
        try:
            sku         = str(row_dict.get("sku", "")).strip()
            if not sku or sku == "nan":
                sku = "UNKNOWN-SKU"
                
            marketplace = str(row_dict.get("marketplace", "unknown")).strip()

            product_id  = await _resolve_product(db, seller_id, sku, marketplace, product_cache)
            snap_date   = _parse_date(row_dict.get("snapshot_date")) or snapshot_date
            sell_price  = _safe_float(row_dict.get("selling_price"))
            cost_price  = _safe_float(row_dict.get("cost_price")) or None
            comm_amount = _safe_float(row_dict.get("commission_amount"))

            values_list.append({
                "seller_id":           seller_id,
                "product_id":          product_id,
                "marketplace":         marketplace,
                "selling_price":       sell_price,
                "cost_price":          cost_price,
                "mrp":                 _safe_float(row_dict.get("mrp")) or None,
                "commission_pct":      _safe_float(row_dict.get("commission_pct")),
                "commission_amount":   comm_amount,
                "discount_percentage": _safe_float(row_dict.get("discount_percentage")),
                "snapshot_date":       snap_date,
            })
            rows_inserted += 1
        except Exception as e:
            logger.warning(f"Error skipping row in pricing: {e}")
            rows_skipped += 1

    if values_list:
        seen = {}
        for v in values_list:
            key = (v["seller_id"], v["product_id"], v["marketplace"], v["snapshot_date"])
            seen[key] = v
        values_list = list(seen.values())
        
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(PricingSnapshot).values(values_list[i:i+1000]).on_conflict_do_update(
                index_elements=["seller_id", "product_id", "marketplace", "snapshot_date"],
                set_={
                    "selling_price": pg_insert(PricingSnapshot).excluded.selling_price,
                    "cost_price": pg_insert(PricingSnapshot).excluded.cost_price
                },
            )
            await db.execute(stmt)

    await db.commit()
    return {"inserted": rows_inserted, "skipped": rows_skipped, "domain": "pricing"}


async def ingest_traffic(db: AsyncSession, df: pd.DataFrame, seller_id: str, snapshot_date: date) -> dict:
    df = _normalise_columns(df, TRAFFIC_COL_MAP)

    rows_inserted = 0
    rows_skipped  = 0
    product_cache = {}
    
    # Pre-warm product cache in one batch
    skus = df.get("sku", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    marketplaces = df.get("marketplace", pd.Series(dtype=str)).astype(str).str.strip().tolist()
    await _resolve_products_batch(db, seller_id, skus, marketplaces, product_cache)

    values_list = []

    for row in df.itertuples(index=False):
        row_dict = row._asdict()
        try:
            sku         = str(row_dict.get("sku", "")).strip()
            if not sku or sku == "nan":
                sku = "UNKNOWN-SKU"
                
            marketplace = str(row_dict.get("marketplace", "unknown")).strip()

            product_id  = await _resolve_product(db, seller_id, sku, marketplace, product_cache)
            metric_date = _parse_date(row_dict.get("metric_date")) or snapshot_date

            values_list.append({
                "seller_id":        seller_id,
                "product_id":       product_id,
                "marketplace":      marketplace,
                "metric_date":      metric_date,
                "impressions":      _safe_int(row_dict.get("impressions")),
                "clicks":           _safe_int(row_dict.get("clicks")),
                "sessions":         _safe_int(row_dict.get("sessions")),
                "page_views":       _safe_int(row_dict.get("page_views")),
                "orders":           _safe_int(row_dict.get("orders")),
                "ad_spend":         _safe_float(row_dict.get("ad_spend")),
                "revenue_from_ads": _safe_float(row_dict.get("revenue_from_ads")),
            })
            rows_inserted += 1
        except Exception as e:
            logger.warning(f"Error skipping row in traffic: {e}")
            rows_skipped += 1

    if values_list:
        seen = {}
        for v in values_list:
            key = (v["seller_id"], v["product_id"], v["marketplace"], v["metric_date"])
            seen[key] = v
        values_list = list(seen.values())
        
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(TrafficMetric).values(values_list[i:i+1000]).on_conflict_do_update(
                index_elements=["seller_id", "product_id", "marketplace", "metric_date"],
                set_={
                    "impressions": pg_insert(TrafficMetric).excluded.impressions,
                    "clicks": pg_insert(TrafficMetric).excluded.clicks,
                    "ad_spend": pg_insert(TrafficMetric).excluded.ad_spend,
                },
            )
            await db.execute(stmt)

    await db.commit()
    return {"inserted": rows_inserted, "skipped": rows_skipped, "domain": "traffic"}


async def ingest_logistics(db: AsyncSession, df: pd.DataFrame, seller_id: str, snapshot_date: date) -> dict:
    df = _normalise_columns(df, LOGISTICS_COL_MAP)

    rows_inserted = 0
    rows_skipped  = 0

    # Bug 6 Fix: Pre-build a lookup map of external_order_id → order_id so logistics rows
    # can set the order_id FK (was always NULL before, breaking analytics joins).
    # Collect all external_order_ids present in the logistics sheet first.
    ext_ids_in_sheet = set()
    for row in df.itertuples(index=False):
        row_dict = row._asdict()
        raw_eid = row_dict.get("external_order_id", "")
        if raw_eid and not pd.isna(raw_eid):
            ext_id_str = str(raw_eid).strip()
            if ext_id_str and ext_id_str != "nan":
                ext_ids_in_sheet.add(ext_id_str)

    # Batch-fetch the matching order UUIDs
    order_id_map: dict[str, str] = {}
    if ext_ids_in_sheet:
        from app.models.models import Order
        res = await db.execute(
            select(Order.order_id, Order.external_order_id).where(
                Order.seller_id == seller_id,
                Order.external_order_id.in_(list(ext_ids_in_sheet)),
            )
        )
        for ord_row in res:
            order_id_map[ord_row.external_order_id] = str(ord_row.order_id)

    values_list = []

    for row in df.itertuples(index=False):
        row_dict = row._asdict()
        try:
            marketplace = str(row_dict.get("marketplace", "unknown")).strip()
            # tracking_id may have been mapped from shipment_id
            raw_tid = row_dict.get("tracking_id", "")
            ext_id = str(raw_tid).strip() if not pd.isna(raw_tid) else None
            if ext_id == "nan" or ext_id == "":
                ext_id = None

            # Resolve order_id FK (Bug 6 fix)
            raw_eid = row_dict.get("external_order_id", "")
            ext_oid = str(raw_eid).strip() if raw_eid and not pd.isna(raw_eid) else None
            if ext_oid == "nan" or ext_oid == "":
                ext_oid = None
            resolved_order_id = order_id_map.get(ext_oid) if ext_oid else None

            # Handle rto_flag — may be string 'True'/'False' or bool
            raw_rto = row_dict.get("rto_flag", False)
            if isinstance(raw_rto, str):
                rto_flag = raw_rto.strip().lower() in ("true", "1", "yes")
            else:
                rto_flag = bool(raw_rto) if not pd.isna(raw_rto) else False

            values_list.append({
                "seller_id":          seller_id,
                "order_id":           resolved_order_id,   # Bug 6: now populated when resolvable
                "marketplace":        marketplace,
                "courier_name":       str(row_dict.get("courier_name", "")) or None,
                "tracking_id":        ext_id,
                "fulfillment_type":   str(row_dict.get("fulfillment_type", "seller")),
                "warehouse_id":       str(row_dict.get("warehouse_id", "")) or None,
                "dispatch_date":      _parse_date(row_dict.get("dispatch_date")),
                "expected_delivery":  _parse_date(row_dict.get("expected_delivery")),
                "actual_delivery":    _parse_date(row_dict.get("actual_delivery")),
                "delivery_status":    str(row_dict.get("delivery_status", "unknown")),
                "rto_flag":           rto_flag,
                "rto_reason":         str(row_dict.get("rto_reason", "")) or None,
                "snapshot_date":      _parse_date(row_dict.get("snapshot_date")) or snapshot_date,
            })
            rows_inserted += 1
        except Exception as e:
            logger.warning(f"Error skipping row in returns: {e}")
            rows_skipped += 1

    if values_list:
        seen = {}
        no_tid = []
        for v in values_list:
            if v.get("tracking_id"):
                key = (v["seller_id"], v["tracking_id"], v["marketplace"], v["snapshot_date"])
                seen[key] = v
            else:
                no_tid.append(v)
        values_list = list(seen.values()) + no_tid
        
        # Split: rows with tracking_id can be upserted; rows without get plain inserts
        with_tid = [v for v in values_list if v.get("tracking_id")]
        without_tid = [v for v in values_list if not v.get("tracking_id")]

        for i in range(0, len(with_tid), 1000):
            stmt = pg_insert(LogisticsMetric).values(with_tid[i:i+1000]).on_conflict_do_update(
                index_elements=["seller_id", "tracking_id", "marketplace", "snapshot_date"],
                index_where=LogisticsMetric.tracking_id.isnot(None),
                set_={
                    "delivery_status": pg_insert(LogisticsMetric).excluded.delivery_status,
                    "actual_delivery": pg_insert(LogisticsMetric).excluded.actual_delivery,
                },
            )
            await db.execute(stmt)

        for i in range(0, len(without_tid), 1000):
            await db.execute(pg_insert(LogisticsMetric).values(without_tid[i:i+1000]).on_conflict_do_nothing())

    await db.commit()
    return {"inserted": rows_inserted, "skipped": rows_skipped, "domain": "logistics"}
