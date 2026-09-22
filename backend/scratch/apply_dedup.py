import re

with open("c:\\projects\\commercepulse\\AZURE\\backend\\app\\services\\ingestion.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Orders
content = content.replace(
    """    if values_list:
        # Split into two paths""",
    """    if values_list:
        # Deduplicate values list based on ON CONFLICT key
        seen = {}
        no_eid = []
        for v in values_list:
            if v.get("external_order_id"):
                seen[v["external_order_id"]] = v
            else:
                no_eid.append(v)
        values_list = list(seen.values()) + no_eid
        
        # Split into two paths"""
)

# 2. Inventory
content = content.replace(
    """    if values_list:
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(InventorySnapshot).values""",
    """    if values_list:
        seen = {}
        for v in values_list:
            key = (v["seller_id"], v["product_id"], v["marketplace"], v["snapshot_date"])
            seen[key] = v
        values_list = list(seen.values())
        
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(InventorySnapshot).values"""
)

# 3. Pricing
content = content.replace(
    """    if values_list:
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(PricingSnapshot).values""",
    """    if values_list:
        seen = {}
        for v in values_list:
            key = (v["seller_id"], v["product_id"], v["marketplace"], v["snapshot_date"])
            seen[key] = v
        values_list = list(seen.values())
        
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(PricingSnapshot).values"""
)

# 4. Traffic
content = content.replace(
    """    if values_list:
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(TrafficMetric).values""",
    """    if values_list:
        seen = {}
        for v in values_list:
            key = (v["seller_id"], v["product_id"], v["marketplace"], v["metric_date"])
            seen[key] = v
        values_list = list(seen.values())
        
        for i in range(0, len(values_list), 1000):
            stmt = pg_insert(TrafficMetric).values"""
)

# 5. Logistics
content = content.replace(
    """    if values_list:
        # Split: rows with tracking_id""",
    """    if values_list:
        seen = {}
        no_tid = []
        for v in values_list:
            if v.get("tracking_id"):
                key = (v["seller_id"], v["tracking_id"], v["marketplace"], v["snapshot_date"])
                seen[key] = v
            else:
                no_tid.append(v)
        values_list = list(seen.values()) + no_tid
        
        # Split: rows with tracking_id"""
)

with open("c:\\projects\\commercepulse\\AZURE\\backend\\app\\services\\ingestion.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Deduplication logic applied to all domains.")
