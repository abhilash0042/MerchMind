"""
Column Mapping Validation Test
Tests that _normalise_columns correctly maps all test dataset columns
to their expected DB column names — no database connection needed.
"""
import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from app.services.ingestion import (
    _normalise_columns,
    ORDER_COL_MAP, INVENTORY_COL_MAP, PRICING_COL_MAP,
    TRAFFIC_COL_MAP, LOGISTICS_COL_MAP,
)


def test_normalise(sheet_name, raw_columns, col_map, expected_db_cols):
    """Test that raw Excel columns are properly mapped to expected DB columns."""
    df = pd.DataFrame({c: ["dummy"] for c in raw_columns})
    result = _normalise_columns(df, col_map)
    mapped = set(result.columns)

    missing = set(expected_db_cols) - mapped
    extra = mapped - set(expected_db_cols) - set(raw_columns)  # unmapped originals are ok

    status = "[PASS]" if not missing else "[FAIL]"
    print(f"\n{status} {sheet_name}")
    print(f"  Raw columns: {raw_columns}")
    print(f"  Mapped to:   {sorted(mapped)}")
    if missing:
        print(f"  MISSING DB COLUMNS: {missing}")
    if extra:
        print(f"  Extra mapped: {extra}")
    return len(missing) == 0


print("=" * 65)
print("Column Mapping Validation Test")
print("=" * 65)

results = []

# Test 1: test_dataset.xlsx Orders
results.append(test_normalise(
    "test_dataset.xlsx / Orders",
    ["order_id", "marketplace", "order_date", "sku", "quantity", "selling_price",
     "discount", "tax", "shipping_fee", "order_status", "return_flag",
     "customer_city", "customer_state"],
    ORDER_COL_MAP,
    ["external_order_id", "marketplace", "order_date", "sku", "quantity",
     "selling_price", "discount", "tax", "shipping_fee", "order_status",
     "return_flag", "customer_city", "customer_state"],
))

# Test 2: commercepulse_testdata.xlsx Orders
results.append(test_normalise(
    "commercepulse_testdata.xlsx / Orders",
    ["order_id", "marketplace", "sku", "order_status", "quantity", "selling_price",
     "discount", "tax", "shipping_fee", "order_date", "delivery_date",
     "return_flag", "cancellation_reason"],
    ORDER_COL_MAP,
    ["external_order_id", "marketplace", "sku", "order_status", "quantity",
     "selling_price", "discount", "tax", "shipping_fee", "order_date",
     "delivery_date", "return_flag", "cancellation_reason"],
))

# Test 3: test_dataset.xlsx Inventory
results.append(test_normalise(
    "test_dataset.xlsx / Inventory",
    ["sku", "marketplace", "available_stock", "reserved_stock",
     "reorder_threshold", "warehouse_location", "product_name", "category"],
    INVENTORY_COL_MAP,
    ["sku", "marketplace", "available_stock", "reserved_stock",
     "reorder_threshold", "warehouse_location"],
))

# Test 4: test_dataset.xlsx Pricing
results.append(test_normalise(
    "test_dataset.xlsx / Pricing",
    ["sku", "marketplace", "cost_price", "mrp", "selling_price",
     "commission_pct", "discount_percentage"],
    PRICING_COL_MAP,
    ["sku", "marketplace", "cost_price", "mrp", "selling_price",
     "commission_pct", "discount_percentage"],
))

# Test 5: test_dataset.xlsx Traffic
results.append(test_normalise(
    "test_dataset.xlsx / Traffic",
    ["metric_date", "marketplace", "sku", "impressions", "clicks",
     "sessions", "orders", "ad_spend", "revenue_from_ads"],
    TRAFFIC_COL_MAP,
    ["metric_date", "marketplace", "sku", "impressions", "clicks",
     "sessions", "orders", "ad_spend", "revenue_from_ads"],
))

# Test 6: test_dataset.xlsx Logistics (THE CRITICAL ONE)
results.append(test_normalise(
    "test_dataset.xlsx / Logistics",
    ["shipment_id", "order_id", "marketplace", "carrier", "dispatch_date",
     "estimated_delivery", "actual_delivery", "delivery_status",
     "rto_flag", "shipping_cost", "fulfillment_type"],
    LOGISTICS_COL_MAP,
    ["tracking_id", "external_order_id", "marketplace", "courier_name",
     "dispatch_date", "expected_delivery", "actual_delivery",
     "delivery_status", "rto_flag", "fulfillment_type"],
))

# Test 7: commercepulse_testdata.xlsx Logistics
results.append(test_normalise(
    "commercepulse_testdata.xlsx / Logistics",
    ["order_id", "marketplace", "courier_name", "tracking_id",
     "fulfillment_type", "warehouse_id", "dispatch_date",
     "expected_delivery", "actual_delivery", "delivery_status",
     "rto_flag", "rto_reason", "snapshot_date"],
    LOGISTICS_COL_MAP,
    ["external_order_id", "marketplace", "courier_name", "tracking_id",
     "fulfillment_type", "warehouse_id", "dispatch_date",
     "expected_delivery", "actual_delivery", "delivery_status",
     "rto_flag", "rto_reason", "snapshot_date"],
))

print("\n" + "=" * 65)
passed = sum(results)
total = len(results)
status = "ALL TESTS PASSED" if passed == total else f"{total - passed} TESTS FAILED"
print(f"Results: {passed}/{total} passed -- {status}")
print("=" * 65)
