import re

with open("c:\\projects\\commercepulse\\AZURE\\backend\\app\\services\\ingestion.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix orders (with_eid / without_eid)
content = content.replace(
    """        if with_eid:
            stmt = pg_insert(Order).values(with_eid).on_conflict_do_update(
                index_elements=["external_order_id"],
                index_where=Order.external_order_id.isnot(None),
                set_={
                    "order_status": pg_insert(Order).excluded.order_status,
                    "delivery_date": pg_insert(Order).excluded.delivery_date,
                },
            )
            await db.execute(stmt)

        if without_eid:
            await db.execute(pg_insert(Order).values(without_eid).on_conflict_do_nothing())""",
    """        for i in range(0, len(with_eid), 1000):
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
            await db.execute(pg_insert(Order).values(without_eid[i:i+1000]).on_conflict_do_nothing())"""
)

# 2. Fix inventory
content = content.replace(
    """    if values_list:
        stmt = pg_insert(InventorySnapshot).values(values_list).on_conflict_do_update(
            index_elements=["seller_id", "product_id", "marketplace", "snapshot_date"],
            set_={
                "available_stock": pg_insert(InventorySnapshot).excluded.available_stock,
                "reserved_stock": pg_insert(InventorySnapshot).excluded.reserved_stock,
            },
        )
        await db.execute(stmt)""",
    """    if values_list:
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(InventorySnapshot).values(values_list[i:i+1000]).on_conflict_do_update(
                index_elements=["seller_id", "product_id", "marketplace", "snapshot_date"],
                set_={
                    "available_stock": pg_insert(InventorySnapshot).excluded.available_stock,
                    "reserved_stock": pg_insert(InventorySnapshot).excluded.reserved_stock,
                },
            )
            await db.execute(stmt)"""
)

# 3. Fix pricing
content = content.replace(
    """    if values_list:
        stmt = pg_insert(PricingSnapshot).values(values_list).on_conflict_do_update(
            index_elements=["seller_id", "product_id", "marketplace", "snapshot_date"],
            set_={
                "selling_price": pg_insert(PricingSnapshot).excluded.selling_price,
                "cost_price": pg_insert(PricingSnapshot).excluded.cost_price
            },
        )
        await db.execute(stmt)""",
    """    if values_list:
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(PricingSnapshot).values(values_list[i:i+1000]).on_conflict_do_update(
                index_elements=["seller_id", "product_id", "marketplace", "snapshot_date"],
                set_={
                    "selling_price": pg_insert(PricingSnapshot).excluded.selling_price,
                    "cost_price": pg_insert(PricingSnapshot).excluded.cost_price
                },
            )
            await db.execute(stmt)"""
)

# 4. Fix traffic
content = content.replace(
    """    if values_list:
        stmt = pg_insert(TrafficMetric).values(values_list).on_conflict_do_update(
            index_elements=["seller_id", "product_id", "marketplace", "metric_date"],
            set_={
                "impressions": pg_insert(TrafficMetric).excluded.impressions,
                "clicks": pg_insert(TrafficMetric).excluded.clicks,
                "ad_spend": pg_insert(TrafficMetric).excluded.ad_spend,
            },
        )
        await db.execute(stmt)""",
    """    if values_list:
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(TrafficMetric).values(values_list[i:i+1000]).on_conflict_do_update(
                index_elements=["seller_id", "product_id", "marketplace", "metric_date"],
                set_={
                    "impressions": pg_insert(TrafficMetric).excluded.impressions,
                    "clicks": pg_insert(TrafficMetric).excluded.clicks,
                    "ad_spend": pg_insert(TrafficMetric).excluded.ad_spend,
                },
            )
            await db.execute(stmt)"""
)

# 5. Fix logistics
content = content.replace(
    """        if with_tid:
            stmt = pg_insert(LogisticsMetric).values(with_tid).on_conflict_do_update(
                index_elements=["seller_id", "tracking_id", "marketplace", "snapshot_date"],
                index_where=LogisticsMetric.tracking_id.isnot(None),
                set_={
                    "delivery_status": pg_insert(LogisticsMetric).excluded.delivery_status,
                    "actual_delivery": pg_insert(LogisticsMetric).excluded.actual_delivery,
                },
            )
            await db.execute(stmt)

        if without_tid:
            await db.execute(pg_insert(LogisticsMetric).values(without_tid).on_conflict_do_nothing())""",
    """        for i in range(0, len(with_tid), 1000):
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
            await db.execute(pg_insert(LogisticsMetric).values(without_tid[i:i+1000]).on_conflict_do_nothing())"""
)

with open("c:\\projects\\commercepulse\\AZURE\\backend\\app\\services\\ingestion.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Batching logic applied to all domains.")
