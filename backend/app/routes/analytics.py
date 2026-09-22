"""Analytics routes — GET /analytics/*"""
from datetime import date, datetime, timedelta
from typing import Optional
import uuid as _uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import enforce_seller_scope

from fastapi_cache.decorator import cache

router = APIRouter()

_LOOKBACK_TABLES = {
    ("orders", "order_date"),
    ("traffic_metrics", "metric_date"),
    ("logistics_metrics", "snapshot_date"),
}


def _as_date(value) -> date:
    if value is None:
        return date.today()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.today()


async def lookback_since(
    db: AsyncSession,
    seller_id: str,
    days: int,
    table: str = "orders",
    date_col: str = "order_date",
) -> date:
    """Window relative to the seller's latest data date, not calendar today."""
    if (table, date_col) not in _LOOKBACK_TABLES:
        raise ValueError(f"Unsupported lookback: {table}.{date_col}")
    result = await db.execute(
        text(f"SELECT MAX({date_col}) FROM {table} WHERE seller_id = CAST(:seller_id AS UUID)"),
        {"seller_id": seller_id},
    )
    as_of = _as_date(result.scalar())
    return as_of - timedelta(days=days)


@router.get("/debug-db", summary="Resolve an active seller_id for local AI orchestrator")
async def debug_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT seller_id FROM sellers WHERE is_active = true LIMIT 1")
    )
    row = result.first()
    return {"active_seller_id": str(row[0]) if row else None}


# ── Dashboard Summary (AI Context) ─────────────────────────────
@router.get("/dashboard/summary", summary="Aggregated dashboard KPIs for AI context")
async def dashboard_summary(
    seller_id: str,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days)
    
    # Revenue and Orders
    rev_sql = text("""
        SELECT 
            SUM(selling_price * quantity) AS total_revenue,
            COUNT(*) AS total_orders,
            COUNT(*) FILTER (WHERE return_flag = TRUE) AS returned_orders
        FROM orders 
        WHERE seller_id = CAST(:seller_id AS UUID) AND order_date >= :since
    """)
    rev_res = await db.execute(rev_sql, {"seller_id": seller_id, "since": since})
    rev_data = rev_res.mappings().first()
    
    # Margin
    margin_sql = text("""
        SELECT ROUND(AVG(((selling_price - cost_price - COALESCE(commission_amount, 0)) / NULLIF(selling_price, 0)) * 100), 1) as avg_margin
        FROM pricing_snapshots
        WHERE seller_id = CAST(:seller_id AS UUID) AND selling_price > 0 AND cost_price IS NOT NULL
    """)
    margin_res = await db.execute(margin_sql, {"seller_id": seller_id})
    margin_data = margin_res.mappings().first()
    
    # ROAS
    roas_sql = text("""
        SELECT CASE WHEN SUM(ad_spend) > 0 THEN ROUND(SUM(revenue_from_ads) / SUM(ad_spend), 2) ELSE 0 END AS avg_roas
        FROM traffic_metrics
        WHERE seller_id = CAST(:seller_id AS UUID)
    """)
    roas_res = await db.execute(roas_sql, {"seller_id": seller_id})
    roas_data = roas_res.mappings().first()

    total_orders = int(rev_data["total_orders"] or 0)
    returned_orders = int(rev_data["returned_orders"] or 0)

    return {
        "period_days": days,
        "total_revenue": float(rev_data["total_revenue"] or 0),
        "total_orders": total_orders,
        # Bug 11 Fix: was returning hardcoded 12, 2.4, 3.2 when DB had no data — now returns real zeros
        "returned_orders": returned_orders,
        "return_rate_pct": round((returned_orders / max(total_orders, 1)) * 100, 2),
        "avg_margin_pct": float(margin_data["avg_margin"] or 0),
        "avg_roas": float(roas_data["avg_roas"] or 0),
    }

# ── Revenue Summary ────────────────────────────────────────────
@router.get("/revenue", summary="Revenue summary for a seller")
async def revenue_summary(
    seller_id: str,
    days:      int = Query(30, ge=1, le=365, description="Lookback window in days"),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days)
    sql = text("""
        SELECT
            marketplace,
            SUM(selling_price * quantity)                          AS gross_revenue,
            SUM((selling_price * quantity) - COALESCE(discount, 0) - COALESCE(tax, 0) - COALESCE(shipping_fee, 0)) AS net_revenue,
            SUM(discount)                                          AS total_discount,
            COUNT(*)                                               AS total_orders,
            COUNT(*) FILTER (WHERE order_status = 'delivered')     AS delivered_orders,
            COUNT(*) FILTER (WHERE order_status = 'cancelled')     AS cancelled_orders,
            COUNT(*) FILTER (WHERE return_flag = TRUE)             AS returned_orders,
            ROUND(AVG(selling_price)::numeric, 2)                  AS avg_order_value
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID)
          AND order_date >= :since
        GROUP BY marketplace
        ORDER BY gross_revenue DESC
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "since": since})
    rows = result.mappings().all()
    return {
        "seller_id": seller_id,
        "period_days": days,
        "since": str(since),
        "data": [dict(r) for r in rows],
    }


# ── Orders Summary (trend by day) ──────────────────────────────
@router.get("/orders/trend", summary="Daily order trend")
async def orders_trend(
    seller_id: str,
    days:      int = Query(30, ge=1, le=365),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days)
    sql = text("""
        SELECT
            order_date,
            COUNT(*)                                           AS total_orders,
            SUM(selling_price * quantity)                      AS revenue,
            COUNT(*) FILTER (WHERE order_status = 'delivered') AS delivered,
            COUNT(*) FILTER (WHERE order_status = 'cancelled') AS cancelled
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID) AND order_date >= :since
        GROUP BY order_date
        ORDER BY order_date
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "since": since})
    rows = result.mappings().all()
    return {"seller_id": seller_id, "data": [dict(r) for r in rows]}


# ── Inventory Alerts ───────────────────────────────────────────
@router.get("/inventory/alerts", summary="Low-stock and stockout alerts")
async def inventory_alerts(
    seller_id: str,
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        SELECT
            p.sku,
            p.product_name,
            p.category,
            i.marketplace,
            i.available_stock,
            i.reserved_stock,
            i.reorder_threshold,
            i.days_of_stock,
            i.warehouse_location,
            i.snapshot_date,
            CASE
                WHEN i.available_stock = 0 THEN 'STOCKOUT'
                WHEN i.available_stock <= i.reorder_threshold THEN 'LOW STOCK'
                ELSE 'OK'
            END AS alert_level
        FROM inventory_snapshots i
        JOIN products p ON p.product_id = i.product_id
        WHERE i.seller_id = CAST(:seller_id AS UUID)
          AND i.snapshot_date = (
              SELECT MAX(snapshot_date) FROM inventory_snapshots
              WHERE seller_id = CAST(:seller_id AS UUID)
          )
          AND i.available_stock <= i.reorder_threshold
        ORDER BY i.available_stock ASC
    """)
    result = await db.execute(sql, {"seller_id": seller_id})
    rows = result.mappings().all()
    return {
        "seller_id": seller_id,
        "alert_count": len(rows),
        "alerts": [dict(r) for r in rows],
    }


# ── Inventory Status (full latest snapshot) ────────────────────
@router.get("/inventory/status", summary="Current inventory status")
async def inventory_status(
    seller_id: str,
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        SELECT
            p.product_id, p.sku, p.product_name, p.category,
            i.marketplace, i.available_stock, i.reserved_stock,
            (i.available_stock + i.reserved_stock) AS total_stock, i.reorder_threshold, i.days_of_stock, i.snapshot_date
        FROM inventory_snapshots i
        JOIN products p ON p.product_id = i.product_id
        WHERE i.seller_id = CAST(:seller_id AS UUID)
          AND i.snapshot_date = (
              SELECT MAX(snapshot_date) FROM inventory_snapshots WHERE seller_id = CAST(:seller_id AS UUID)
          )
        ORDER BY i.available_stock ASC
    """)
    result = await db.execute(sql, {"seller_id": seller_id})
    rows = []
    for r in result.mappings().all():
        d = dict(r)
        if d.get("product_id") is not None:
            d["product_id"] = str(d["product_id"])
        if d.get("snapshot_date") is not None:
            d["snapshot_date"] = str(d["snapshot_date"])
        rows.append(d)
    return {"seller_id": seller_id, "count": len(rows), "data": rows}


# ── Pricing Margins ────────────────────────────────────────────
@router.get("/pricing/margins", summary="Current pricing and margin analysis")
async def pricing_margins(
    seller_id: str,
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        SELECT
            p.sku, p.product_name, p.category,
            pr.marketplace, pr.selling_price, pr.cost_price, pr.mrp,
            pr.commission_pct, pr.commission_amount, pr.discount_percentage,
            (pr.selling_price - COALESCE(pr.cost_price, 0) - COALESCE(pr.commission_amount, 0)) AS net_margin,
            CASE WHEN pr.selling_price > 0 AND pr.cost_price IS NOT NULL
                 THEN ROUND(((pr.selling_price - pr.cost_price - COALESCE(pr.commission_amount, 0)) / pr.selling_price) * 100, 1)
                 ELSE 0 END AS margin_pct,
            pr.snapshot_date
        FROM pricing_snapshots pr
        JOIN products p ON p.product_id = pr.product_id
        WHERE pr.seller_id = CAST(:seller_id AS UUID)
          AND pr.snapshot_date = (
              SELECT MAX(snapshot_date) FROM pricing_snapshots WHERE seller_id = CAST(:seller_id AS UUID)
          )
        ORDER BY margin_pct ASC NULLS LAST
    """)
    result = await db.execute(sql, {"seller_id": seller_id})
    rows = result.mappings().all()
    return {"seller_id": seller_id, "count": len(rows), "data": [dict(r) for r in rows]}


# ── Traffic Funnel ─────────────────────────────────────────────
@router.get("/traffic/funnel", summary="Traffic funnel and ROAS overview")
async def traffic_funnel(
    seller_id: str,
    days:      int = Query(7, ge=1, le=90),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days, "traffic_metrics", "metric_date")
    sql = text("""
        SELECT
            p.sku, p.product_name, p.category,
            t.marketplace,
            SUM(t.impressions)       AS total_impressions,
            SUM(t.clicks)            AS total_clicks,
            SUM(t.sessions)          AS total_sessions,
            SUM(t.orders)            AS total_orders,
            ROUND(
                CASE WHEN SUM(t.impressions) > 0
                    THEN (SUM(t.clicks)::numeric / NULLIF(SUM(t.impressions), 0)) * 100 
                    ELSE 0 END, 2
            ) AS ctr_pct,
            ROUND(
                CASE WHEN SUM(t.clicks) > 0
                    THEN (SUM(t.orders)::numeric / NULLIF(SUM(t.clicks), 0)) * 100 
                    ELSE 0 END, 2
            ) AS conversion_rate_pct,
            SUM(t.ad_spend)          AS total_ad_spend,
            SUM(t.revenue_from_ads)  AS total_revenue_from_ads,
            ROUND(
                CASE WHEN SUM(t.ad_spend) > 0
                    THEN SUM(t.revenue_from_ads) / NULLIF(SUM(t.ad_spend), 0)
                    ELSE 0 END, 2
            ) AS roas
        FROM traffic_metrics t
        JOIN products p ON p.product_id = t.product_id
        WHERE t.seller_id = CAST(:seller_id AS UUID) AND t.metric_date >= :since
        GROUP BY p.sku, p.product_name, p.category, t.marketplace
        ORDER BY roas DESC NULLS LAST
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "since": since})
    rows = result.mappings().all()
    return {
        "seller_id": seller_id, "period_days": days,
        "count": len(rows), "data": [dict(r) for r in rows],
    }


# ── Logistics RTO Rate ─────────────────────────────────────────
@router.get("/logistics/rto-rate", summary="RTO rate and delivery performance")
async def logistics_rto_rate(
    seller_id: str,
    days:      int = Query(30, ge=1, le=365),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days, "logistics_metrics", "snapshot_date")
    sql = text("""
        SELECT
            marketplace,
            COUNT(*)                                      AS total_shipments,
            COUNT(*) FILTER (WHERE rto_flag = TRUE)       AS rto_count,
            ROUND(
                COUNT(*) FILTER (WHERE rto_flag = TRUE)::numeric / NULLIF(COUNT(*), 0) * 100, 2
            )                                             AS rto_rate_pct,
            COUNT(*) FILTER (WHERE delivery_status = 'delivered') AS delivered,
            ROUND(AVG(actual_delivery - dispatch_date)::numeric, 1)   AS avg_shipping_days,
            fulfillment_type
        FROM logistics_metrics
        WHERE seller_id = CAST(:seller_id AS UUID) AND snapshot_date >= :since
        GROUP BY marketplace, fulfillment_type
        ORDER BY rto_rate_pct DESC NULLS LAST
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "since": since})
    rows = result.mappings().all()
    return {
        "seller_id": seller_id, "period_days": days,
        "data": [dict(r) for r in rows],
    }


# ── Executive Dashboard (single call, all KPIs) ────────────────
@router.get("/dashboard", summary="All key metrics in one call")
async def dashboard(
    seller_id: str,
    days:      int = Query(30, ge=1, le=365),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days)

    revenue_sql = text("""
        SELECT
            COALESCE(SUM((selling_price * quantity) - COALESCE(discount, 0) - COALESCE(tax, 0) - COALESCE(shipping_fee, 0)), 0) AS total_net_revenue,
            COUNT(*)                                                                  AS total_orders,
            COUNT(*) FILTER (WHERE order_status = 'cancelled')                       AS cancelled_orders,
            ROUND(
                COUNT(*) FILTER (WHERE order_status = 'cancelled')::numeric
                / NULLIF(COUNT(*), 0) * 100, 2
            )                                                                         AS cancellation_rate_pct,
            COUNT(*) FILTER (WHERE return_flag = TRUE)                               AS returned_orders
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID) AND order_date >= :since
    """)
    inv_sql = text("""
        SELECT COUNT(*) AS low_stock_count
        FROM inventory_snapshots
        WHERE seller_id = CAST(:seller_id AS UUID)
          AND snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots WHERE seller_id = CAST(:seller_id AS UUID))
          AND available_stock <= reorder_threshold
    """)
    rto_sql = text("""
        SELECT ROUND(
            COUNT(*) FILTER (WHERE rto_flag = TRUE)::numeric / NULLIF(COUNT(*), 0) * 100, 2
        ) AS rto_rate_pct
        FROM logistics_metrics
        WHERE seller_id = CAST(:seller_id AS UUID) AND snapshot_date >= :since
    """)
    roas_sql = text("""
        SELECT ROUND(
            CASE WHEN SUM(ad_spend) > 0 THEN SUM(revenue_from_ads) / SUM(ad_spend) END, 2
        ) AS avg_roas
        FROM traffic_metrics
        WHERE seller_id = CAST(:seller_id AS UUID) AND metric_date >= :since
    """)

    import asyncio
    
    # Run queries sequentially (SQLAlchemy AsyncSession is not safe for concurrent queries on one session)
    rev_res  = await db.execute(revenue_sql, {"seller_id": seller_id, "since": since})
    inv_res  = await db.execute(inv_sql,     {"seller_id": seller_id})
    rto_res  = await db.execute(rto_sql,     {"seller_id": seller_id, "since": since})
    roas_res = await db.execute(roas_sql,    {"seller_id": seller_id, "since": since})
    
    rev  = rev_res.mappings().first()
    inv  = inv_res.mappings().first()
    rto  = rto_res.mappings().first()
    roas = roas_res.mappings().first()

    return {
        "seller_id":           seller_id,
        "period_days":         days,
        "kpis": {
            "total_net_revenue":    float(rev["total_net_revenue"] or 0),
            "total_orders":         int(rev["total_orders"] or 0),
            "cancellation_rate_pct": float(rev["cancellation_rate_pct"] or 0),
            "returned_orders":      int(rev["returned_orders"] or 0),
            "low_stock_products":   int(inv["low_stock_count"] or 0),
            "rto_rate_pct":         float(rto["rto_rate_pct"] or 0),
            "avg_roas":             float(roas["avg_roas"] or 0),
        },
    }


# ── Orders List (paginated raw rows) ──────────────────────────
@router.get("/orders/list", summary="Paginated raw order rows for the Orders page")
async def orders_list(
    seller_id: str,
    limit:     int = Query(50, ge=1, le=200),
    offset:    int = Query(0, ge=0),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        SELECT
            o.order_id,
            COALESCE(o.customer_name, 'N/A') AS customer_name,
            COALESCE(o.customer_email, '')    AS customer_email,
            o.quantity           AS items,
            (o.selling_price * o.quantity) AS amount,
            o.order_status       AS status,
            o.order_date         AS date,
            COALESCE(o.payment_mode, 'N/A') AS payment,
            o.marketplace
        FROM orders o
        WHERE o.seller_id = CAST(:seller_id AS UUID)
        ORDER BY o.order_date DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "limit": limit, "offset": offset})
    rows = result.mappings().all()

    count_sql = text("SELECT COUNT(*) AS total FROM orders WHERE seller_id = CAST(:seller_id AS UUID)")
    total = (await db.execute(count_sql, {"seller_id": seller_id})).scalar() or 0

    return {"seller_id": seller_id, "total": total, "limit": limit, "offset": offset, "data": [dict(r) for r in rows]}


# ── Orders Stats (summary counts) ─────────────────────────────
@router.get("/orders/stats", summary="Order summary counts for dashboard cards")
async def orders_stats(
    seller_id: str,
    days:      int = Query(30, ge=1, le=365),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days)
    sql = text("""
        SELECT
            COUNT(*)                                               AS total_orders,
            COUNT(*) FILTER (WHERE order_status IN ('pending', 'processing'))  AS pending_orders,
            COUNT(*) FILTER (WHERE order_status = 'delivered')     AS delivered_orders,
            COUNT(*) FILTER (WHERE order_status = 'cancelled')     AS cancelled_orders,
            COUNT(*) FILTER (WHERE order_status = 'shipped')       AS shipped_orders
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID) AND order_date >= :since
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "since": since})
    row = result.mappings().first()
    return {"seller_id": seller_id, "period_days": days, "stats": dict(row) if row else {}}


# ── Inventory Summary (counts by status) ──────────────────────
@router.get("/inventory/summary", summary="Inventory summary counts")
async def inventory_summary(
    seller_id: str,
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        SELECT
            COUNT(*)                                                         AS total_items,
            COUNT(*) FILTER (WHERE available_stock > reorder_threshold)      AS in_stock,
            COUNT(*) FILTER (WHERE available_stock > 0 AND available_stock <= reorder_threshold) AS low_stock,
            COUNT(*) FILTER (WHERE available_stock = 0)                      AS out_of_stock
        FROM inventory_snapshots
        WHERE seller_id = CAST(:seller_id AS UUID)
          AND snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots WHERE seller_id = CAST(:seller_id AS UUID))
    """)
    result = await db.execute(sql, {"seller_id": seller_id})
    row = result.mappings().first()
    return {"seller_id": seller_id, "summary": dict(row) if row else {}}


# ── Customers Summary (aggregated from orders) ────────────────
@router.get("/customers/summary", summary="Top customers aggregated from orders")
async def customers_summary(
    seller_id: str,
    limit:     int = Query(50, ge=1, le=200),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        SELECT
            COALESCE(customer_name, 'Anonymous') AS customer_name,
            COALESCE(customer_email, '')          AS customer_email,
            COUNT(DISTINCT order_id)              AS total_orders,
            SUM(selling_price * quantity)         AS total_spent,
            MIN(order_date)                       AS first_order,
            MAX(order_date)                       AS last_order,
            STRING_AGG(DISTINCT marketplace, ', ') AS channels
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID)
          AND customer_name IS NOT NULL AND customer_name != ''
        GROUP BY customer_name, customer_email
        ORDER BY total_spent DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "limit": limit})
    rows = result.mappings().all()

    total_sql = text("""
        SELECT COUNT(DISTINCT customer_name) AS total
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID) AND customer_name IS NOT NULL AND customer_name != ''
    """)
    total = (await db.execute(total_sql, {"seller_id": seller_id})).scalar() or 0

    return {"seller_id": seller_id, "total_customers": total, "data": [dict(r) for r in rows]}


# ── Revenue by Category ───────────────────────────────────────
@router.get("/revenue/by-category", summary="Revenue grouped by product category")
async def revenue_by_category(
    seller_id: str,
    days:      int = Query(30, ge=1, le=365),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    since = await lookback_since(db, seller_id, days)
    sql = text("""
        SELECT
            COALESCE(p.category, 'Uncategorized') AS category,
            SUM(o.selling_price * o.quantity)      AS revenue,
            COUNT(*)                               AS order_count
        FROM orders o
        LEFT JOIN products p ON p.product_id = o.product_id
        WHERE o.seller_id = CAST(:seller_id AS UUID) AND o.order_date >= :since
        GROUP BY p.category
        ORDER BY revenue DESC
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "since": since})
    rows = result.mappings().all()
    return {"seller_id": seller_id, "period_days": days, "data": [dict(r) for r in rows]}


# ── Revenue Monthly Trend ─────────────────────────────────────
@router.get("/revenue/monthly", summary="Monthly revenue and cost trend")
async def revenue_monthly(
    seller_id: str,
    months:    int = Query(12, ge=1, le=24),
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        SELECT
            TO_CHAR(order_date, 'Mon') AS month,
            EXTRACT(YEAR FROM order_date)  AS year,
            EXTRACT(MONTH FROM order_date) AS month_num,
            SUM(selling_price * quantity)   AS revenue,
            SUM(COALESCE(discount, 0) + COALESCE(tax, 0) + COALESCE(shipping_fee, 0)) AS costs,
            SUM((selling_price * quantity) - COALESCE(discount, 0) - COALESCE(tax, 0) - COALESCE(shipping_fee, 0)) AS profit
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID)
          AND order_date >= (
              COALESCE(
                  (SELECT MAX(order_date) FROM orders o2 WHERE o2.seller_id = CAST(:seller_id AS UUID)),
                  CURRENT_DATE
              ) - INTERVAL '1 month' * :months
          )
        GROUP BY TO_CHAR(order_date, 'Mon'), EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
        ORDER BY year, month_num
    """)
    result = await db.execute(sql, {"seller_id": seller_id, "months": months})
    rows = result.mappings().all()
    return {"seller_id": seller_id, "data": [dict(r) for r in rows]}


# ── Products List with AI Analysis Status ─────────────────────
@router.get("/products/list", summary="List products with key metrics and AI status")
async def products_list(
    seller_id: str,
    db:        AsyncSession = Depends(get_db),
    _scope:    str = Depends(enforce_seller_scope),
):
    sql = text("""
        WITH revenue_stats AS (
            SELECT product_id,
                   SUM(selling_price * quantity) AS total_revenue,
                   COUNT(*) AS total_orders
            FROM orders
            WHERE seller_id = CAST(:seller_id AS UUID)
            GROUP BY product_id
        ),
        margin_stats AS (
            SELECT product_id, 
                   AVG(CASE WHEN selling_price > 0 AND cost_price IS NOT NULL 
                        THEN ROUND(((selling_price - cost_price - COALESCE(commission_amount, 0)) / selling_price) * 100, 1) 
                        ELSE 0 END) AS margin_pct
            FROM pricing_snapshots
            WHERE seller_id = CAST(:seller_id AS UUID)
              AND snapshot_date = (SELECT MAX(snapshot_date) FROM pricing_snapshots WHERE seller_id = CAST(:seller_id AS UUID))
            GROUP BY product_id
        ),
        stock_stats AS (
            SELECT product_id, SUM(available_stock) AS stock_level
            FROM inventory_snapshots
            WHERE seller_id = CAST(:seller_id AS UUID)
              AND snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots WHERE seller_id = CAST(:seller_id AS UUID))
            GROUP BY product_id
        ),
        roas_stats AS (
            SELECT product_id,
                   CASE WHEN SUM(ad_spend) > 0 THEN ROUND(SUM(revenue_from_ads) / SUM(ad_spend), 2) ELSE 0 END AS roas
            FROM traffic_metrics
            WHERE seller_id = CAST(:seller_id AS UUID)
            GROUP BY product_id
        ),
        ai_status AS (
            SELECT product_id,
                   status AS analysis_status,
                   analysis_date AS last_analyzed,
                   executive_summary
            FROM ai_product_analyses
            WHERE seller_id = CAST(:seller_id AS UUID)
              AND (product_id, analysis_date) IN (
                  SELECT product_id, MAX(analysis_date)
                  FROM ai_product_analyses
                  WHERE seller_id = CAST(:seller_id AS UUID)
                  GROUP BY product_id
              )
        )
        SELECT DISTINCT ON (p.product_id)
            p.product_id, p.sku, p.product_name, p.category, p.marketplace,
            COALESCE(r.total_revenue, 0) AS total_revenue,
            COALESCE(r.total_orders, 0) AS total_orders,
            COALESCE(m.margin_pct, 0) AS margin_pct,
            COALESCE(s.stock_level, 0) AS stock_level,
            COALESCE(ro.roas, 0) AS roas,
            COALESCE(ai.analysis_status, 'none') AS analysis_status,
            ai.last_analyzed,
            ai.executive_summary->>'product_health_score' AS health_score,
            ai.executive_summary->>'performance_verdict' AS performance_verdict
        FROM products p
        LEFT JOIN revenue_stats r ON r.product_id = p.product_id
        LEFT JOIN margin_stats m ON m.product_id = p.product_id
        LEFT JOIN stock_stats s ON s.product_id = p.product_id
        LEFT JOIN roas_stats ro ON ro.product_id = p.product_id
        LEFT JOIN ai_status ai ON ai.product_id = p.product_id
        WHERE p.seller_id = CAST(:seller_id AS UUID)
        ORDER BY p.product_id, r.total_revenue DESC NULLS LAST
    """)
    result = await db.execute(sql, {"seller_id": seller_id})
    rows = result.mappings().all()
    
    # Process rows to ensure JSON-safe types (convert Decimal/UUID/date)
    from decimal import Decimal as _Dec
    processed_rows = []
    for r in rows:
        d = dict(r)
        d['product_id'] = str(d['product_id'])
        if d.get('last_analyzed'):
            d['last_analyzed'] = str(d['last_analyzed'])
        # Convert all Decimal fields to float for JSON safety
        for key in ('total_revenue', 'total_orders', 'margin_pct', 'stock_level', 'roas', 'health_score'):
            if key in d and d[key] is not None:
                d[key] = float(d[key]) if isinstance(d[key], _Dec) else d[key]
        processed_rows.append(d)
        
    return {"seller_id": seller_id, "data": processed_rows}


# ── AI Tool Endpoints (Product specific) ────────────────────────
@router.get("/product/{product_id}/roas", summary="Live ROAS for a specific product")
async def product_roas(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        _uuid.UUID(product_id)
    except ValueError:
        return {"product_id": product_id, "roas": 0, "total_spend": 0, "error": "product_id must be a UUID"}
    sql = text("""
        SELECT 
            CASE WHEN SUM(ad_spend) > 0 THEN ROUND(SUM(revenue_from_ads) / SUM(ad_spend), 2) ELSE 0 END AS roas,
            COALESCE(SUM(ad_spend), 0) AS total_spend
        FROM traffic_metrics
        WHERE product_id = CAST(:product_id AS UUID)
    """)
    result = await db.execute(sql, {"product_id": product_id})
    row = result.mappings().first()
    return {
        "product_id": product_id,
        "roas": float(row["roas"] or 0),
        "total_spend": float(row["total_spend"] or 0)
    }

@router.get("/inventory/{product_id}", summary="Live inventory for a specific product")
async def product_inventory(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        _uuid.UUID(product_id)
    except ValueError:
        return {"product_id": product_id, "available_stock": 0, "error": "product_id must be a UUID"}
    sql = text("""
        SELECT COALESCE(SUM(available_stock), 0) AS available_stock
        FROM inventory_snapshots
        WHERE product_id = CAST(:product_id AS UUID)
          AND snapshot_date = (
              SELECT MAX(snapshot_date) FROM inventory_snapshots WHERE product_id = CAST(:product_id AS UUID)
          )
    """)
    result = await db.execute(sql, {"product_id": product_id})
    row = result.mappings().first()
    return {
        "product_id": product_id,
        "available_stock": int(row["available_stock"] or 0)
    }

@router.get("/product/{product_id}/metrics", summary="Live detailed metrics for a specific product")
async def product_metrics_detailed(
    product_id: str,
    seller_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _scope: str = Depends(enforce_seller_scope)
):
    metrics_sql = text("""
        WITH revenue_stats AS (
            SELECT product_id,
                   SUM(selling_price * quantity) AS total_revenue,
                   COUNT(*) AS total_orders,
                   ROUND(AVG(selling_price * quantity), 2) AS avg_order_value,
                   SUM(CASE WHEN discount > 0 THEN 1 ELSE 0 END) AS discounted_orders,
                   SUM(discount) AS total_discount_given,
                   SUM(shipping_fee) AS total_shipping_collected,
                   SUM(tax) AS total_tax_collected
            FROM orders
            WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID)
            GROUP BY product_id
        ),
        return_stats AS (
            SELECT product_id,
                   COUNT(*) FILTER (WHERE return_flag = true) AS total_returns,
                   COUNT(*) AS total_fulfilled,
                   ROUND(COUNT(*) FILTER (WHERE return_flag = true) * 100.0 / NULLIF(COUNT(*), 0), 1) AS return_rate_pct
            FROM orders
            WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID)
              AND order_status IN ('delivered', 'returned')
            GROUP BY product_id
        ),
        stock_stats AS (
            SELECT product_id,
                   SUM(available_stock) AS stock_level,
                   SUM(reserved_stock) AS reserved_stock,
                   MAX(reorder_threshold) AS reorder_threshold,
                   MAX(days_of_stock) AS days_of_stock
            FROM inventory_snapshots
            WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID)
              AND snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID))
            GROUP BY product_id
        ),
        roas_stats AS (
            SELECT product_id,
                   CASE WHEN SUM(ad_spend) > 0 THEN ROUND(SUM(revenue_from_ads) / SUM(ad_spend), 2) ELSE 0 END AS roas,
                   SUM(ad_spend) AS total_ad_spend,
                   SUM(revenue_from_ads) AS total_ad_revenue,
                   SUM(impressions) AS total_impressions,
                   SUM(clicks) AS total_clicks,
                   CASE WHEN SUM(impressions) > 0 THEN ROUND(SUM(clicks) * 100.0 / SUM(impressions), 2) ELSE 0 END AS ctr_pct,
                   CASE WHEN SUM(clicks) > 0 THEN ROUND(SUM(ad_spend) / SUM(clicks), 2) ELSE 0 END AS cost_per_click
            FROM traffic_metrics
            WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID)
            GROUP BY product_id
        ),
        rto_stats AS (
            SELECT COUNT(*) AS total_shipments,
                   COUNT(*) FILTER (WHERE rto_flag = true) AS rto_count,
                   ROUND(COUNT(*) FILTER (WHERE rto_flag = true) * 100.0 / NULLIF(COUNT(*), 0), 1) AS rto_rate_pct,
                   ROUND(AVG(CASE WHEN actual_delivery IS NOT NULL AND dispatch_date IS NOT NULL
                       THEN actual_delivery - dispatch_date END), 1) AS avg_delivery_days
            FROM logistics_metrics
            WHERE seller_id = CAST(:seller_id AS UUID)
              AND order_id IN (SELECT order_id FROM orders WHERE product_id = CAST(:product_id AS UUID) AND seller_id = CAST(:seller_id AS UUID))
        )
        SELECT p.product_name, p.sku, p.category, p.marketplace, p.brand, p.sub_category,
               COALESCE(r.total_revenue, 0) AS total_revenue,
               COALESCE(r.total_orders, 0) AS total_orders,
               COALESCE(r.avg_order_value, 0) AS avg_order_value,
               COALESCE(r.discounted_orders, 0) AS discounted_orders,
               COALESCE(r.total_discount_given, 0) AS total_discount_given,
               COALESCE(r.total_shipping_collected, 0) AS total_shipping_collected,
               COALESCE(ret.total_returns, 0) AS total_returns,
               COALESCE(ret.return_rate_pct, 0) AS return_rate_pct,
               COALESCE(s.stock_level, 0) AS stock_level,
               COALESCE(s.reserved_stock, 0) AS reserved_stock,
               COALESCE(s.reorder_threshold, 0) AS reorder_threshold,
               COALESCE(s.days_of_stock, 0) AS days_of_stock,
               COALESCE(ro.roas, 0) AS roas,
               COALESCE(ro.total_ad_spend, 0) AS total_ad_spend,
               COALESCE(ro.total_ad_revenue, 0) AS total_ad_revenue,
               COALESCE(ro.total_impressions, 0) AS total_impressions,
               COALESCE(ro.total_clicks, 0) AS total_clicks,
               COALESCE(ro.ctr_pct, 0) AS ctr_pct,
               COALESCE(ro.cost_per_click, 0) AS cost_per_click,
               COALESCE(rto.rto_count, 0) AS rto_count,
               COALESCE(rto.rto_rate_pct, 0) AS rto_rate_pct,
               COALESCE(rto.avg_delivery_days, 0) AS avg_delivery_days
        FROM products p
        LEFT JOIN revenue_stats r ON r.product_id = p.product_id
        LEFT JOIN return_stats ret ON ret.product_id = p.product_id
        LEFT JOIN stock_stats s ON s.product_id = p.product_id
        LEFT JOIN roas_stats ro ON ro.product_id = p.product_id
        CROSS JOIN rto_stats rto
        WHERE p.product_id = CAST(:product_id AS UUID) AND p.seller_id = CAST(:seller_id AS UUID)
    """)
    result = await db.execute(metrics_sql, {"product_id": product_id, "seller_id": seller_id})
    product_info = result.mappings().first()
    if not product_info:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")

    pricing_sql = text("""
        SELECT marketplace, selling_price, cost_price, mrp, commission_pct, 
               commission_amount, discount_percentage,
               CASE WHEN selling_price > 0 AND cost_price IS NOT NULL
                    THEN ROUND(((selling_price - cost_price - COALESCE(commission_amount, 0)) / selling_price) * 100, 1)
                    ELSE 0 END AS margin_pct,
               CASE WHEN selling_price > 0 AND cost_price IS NOT NULL
                    THEN ROUND(selling_price - cost_price - COALESCE(commission_amount, 0), 2)
                    ELSE 0 END AS net_profit_per_unit
        FROM pricing_snapshots
        WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID)
          AND snapshot_date = (SELECT MAX(snapshot_date) FROM pricing_snapshots WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID))
    """)
    pricing_result = await db.execute(pricing_sql, {"product_id": product_id, "seller_id": seller_id})
    pricing_rows = [dict(r) for r in pricing_result.mappings().all()]

    mp_revenue_sql = text("""
        SELECT marketplace,
               SUM(selling_price * quantity) AS revenue,
               COUNT(*) AS orders,
               ROUND(AVG(selling_price * quantity), 2) AS aov,
               SUM(CASE WHEN return_flag = true THEN 1 ELSE 0 END) AS returns
        FROM orders
        WHERE seller_id = CAST(:seller_id AS UUID) AND product_id = CAST(:product_id AS UUID)
        GROUP BY marketplace
        ORDER BY revenue DESC
    """)
    mp_result = await db.execute(mp_revenue_sql, {"product_id": product_id, "seller_id": seller_id})
    marketplace_splits = [dict(r) for r in mp_result.mappings().all()]

    from decimal import Decimal
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean(v) for v in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj

    product_data = clean(dict(product_info))
    product_data["product_id"] = product_id
    product_data["pricing_by_marketplace"] = clean(pricing_rows)
    product_data["revenue_by_marketplace"] = clean(marketplace_splits)

    return product_data
