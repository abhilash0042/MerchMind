"""
Database Migration: Add missing columns and constraints for data ingestion fix.
Uses direct psycopg2 connection to avoid asyncpg DNS/SSL issues on Windows.

Run with:  python migrate_add_columns.py
"""
import sys
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from urllib.parse import quote_plus
import psycopg2

# Direct connection parameters matching Supabase session pooler (IPv4)
POSTGRES_HOST = "aws-1-ap-south-1.pooler.supabase.com"
POSTGRES_PORT = 5432
POSTGRES_DB = "postgres"
POSTGRES_USER = "postgres.gwwhksdelequvapksgqx"
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
if not POSTGRES_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD environment variable is not set")


def migrate():
    print("[MIGRATE] CommercePulse DB Migration - Adding missing columns & constraints")
    print("=" * 65)

    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        sslmode="require",
    )
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Orders: Add customer/payment columns
    print("\n[1/5] Adding customer_name, customer_email, payment_mode to orders...")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_name TEXT")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_email TEXT")
    cur.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_mode TEXT")
    print("   [OK] Done")

    # 2. Orders: Make external_order_id unique
    print("\n[2/5] Ensuring unique index on orders.external_order_id...")
    try:
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_orders_external_order_id
            ON orders (external_order_id)
            WHERE external_order_id IS NOT NULL
        """)
        print("   [OK] Unique index created (partial, excludes NULLs)")
    except Exception as e:
        conn.rollback()
        print(f"   [WARN] Could not create unique index: {e}")
        print("   -> Cleaning duplicates first...")
        cur.execute("""
            DELETE FROM orders a USING orders b
            WHERE a.external_order_id = b.external_order_id
              AND a.external_order_id IS NOT NULL
              AND a.created_at < b.created_at
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_orders_external_order_id
            ON orders (external_order_id)
            WHERE external_order_id IS NOT NULL
        """)
        print("   [OK] Duplicates cleaned and unique index created")

    # 3. Logistics: Add UniqueConstraint for upsert
    print("\n[3/5] Ensuring unique constraint on logistics_metrics...")
    try:
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_logistics_seller_tracking_mp_snap
            ON logistics_metrics (seller_id, tracking_id, marketplace, snapshot_date)
            WHERE tracking_id IS NOT NULL
        """)
        print("   [OK] Unique index created (partial, excludes NULL tracking_id)")
    except Exception as e:
        conn.rollback()
        print(f"   [WARN] Could not create logistics unique index: {e}")
        cur.execute("""
            DELETE FROM logistics_metrics a USING logistics_metrics b
            WHERE a.seller_id = b.seller_id
              AND a.tracking_id = b.tracking_id
              AND a.marketplace = b.marketplace
              AND a.snapshot_date = b.snapshot_date
              AND a.tracking_id IS NOT NULL
              AND a.id < b.id
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_logistics_seller_tracking_mp_snap
            ON logistics_metrics (seller_id, tracking_id, marketplace, snapshot_date)
            WHERE tracking_id IS NOT NULL
        """)
        print("   [OK] Duplicates cleaned and unique index created")

    # 4. Ensure all expected columns exist on all tables
    print("\n[4/5] Ensuring all expected columns exist on all tables...")
    safe_alters = [
        "ALTER TABLE traffic_metrics ADD COLUMN IF NOT EXISTS sessions INTEGER DEFAULT 0",
        "ALTER TABLE traffic_metrics ADD COLUMN IF NOT EXISTS page_views INTEGER DEFAULT 0",
        "ALTER TABLE pricing_snapshots ADD COLUMN IF NOT EXISTS mrp NUMERIC(12, 2)",
        "ALTER TABLE logistics_metrics ADD COLUMN IF NOT EXISTS expected_delivery DATE",
        "ALTER TABLE logistics_metrics ADD COLUMN IF NOT EXISTS warehouse_id TEXT",
    ]
    for stmt in safe_alters:
        cur.execute(stmt)
    print("   [OK] Done")

    # 5. Verify table structure
    print("\n[5/5] Verifying table structures...")
    for table in ["orders", "inventory_snapshots", "pricing_snapshots", "traffic_metrics", "logistics_metrics", "products"]:
        cur.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{table}'
            ORDER BY ordinal_position
        """)
        cols = [r[0] for r in cur.fetchall()]
        print(f"   {table}: {len(cols)} columns -> {', '.join(cols)}")

    cur.close()
    conn.close()

    print("\n" + "=" * 65)
    print("[DONE] Migration complete! Database is ready for data ingestion.")


if __name__ == "__main__":
    migrate()
