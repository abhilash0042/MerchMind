"""Clean up the database: remove SKU-* test products and deduplicate BB-* products."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

# Proper Brew Boulevard coffee product names
BB_PRODUCTS = {
    "BB-WB-001": ("Ethiopian Yirgacheffe Whole Bean", "Coffee Beans"),
    "BB-WB-002": ("Colombian Supremo Dark Roast", "Coffee Beans"),
    "BB-WB-003": ("Sumatra Mandheling Single Origin", "Coffee Beans"),
    "BB-WB-004": ("Brazilian Santos Medium Roast", "Coffee Beans"),
    "BB-GR-005": ("French Vanilla Ground Coffee", "Ground Coffee"),
    "BB-GR-006": ("Hazelnut Blend Ground Coffee", "Ground Coffee"),
    "BB-GR-007": ("Espresso Classico Fine Grind", "Ground Coffee"),
    "BB-CB-008": ("Caramel Macchiato Cold Brew 12oz", "Cold Brew"),
    "BB-CB-009": ("Nitro Vanilla Cold Brew 12oz", "Cold Brew"),
    "BB-CB-010": ("Mocha Oat Milk Cold Brew 12oz", "Cold Brew"),
    "BB-DB-011": ("Matcha Latte Powder Mix", "Specialty Drinks"),
    "BB-DB-012": ("Chai Spice Concentrate 32oz", "Specialty Drinks"),
    "BB-IN-013": ("Pour Over Dripper Set - Ceramic", "Accessories"),
    "BB-IN-014": ("Stainless Steel Travel Tumbler 16oz", "Accessories"),
    "BB-GF-015": ("Coffee Lover Gift Box - Premium", "General"),
}


async def main():
    from app.db.session import get_db

    async for db in get_db():
        # ─── Step 1: Count current state ───────────────────────────
        r = await db.execute(text("SELECT COUNT(*) FROM products"))
        total_before = r.scalar()
        r = await db.execute(text("SELECT COUNT(*) FROM products WHERE sku LIKE 'SKU-%'"))
        sku_count = r.scalar()
        r = await db.execute(text("SELECT COUNT(*) FROM products WHERE sku LIKE 'BB-%'"))
        bb_count = r.scalar()
        print(f"BEFORE: {total_before} total products ({sku_count} SKU-*, {bb_count} BB-*)")

        # ─── Step 2: Delete all SKU-* related data ─────────────────
        # Delete from child tables first (orders, inventory, pricing, traffic, logistics, embeddings)
        for table in ["orders", "inventory_snapshots", "pricing_snapshots", 
                       "traffic_metrics", "logistics_metrics", "product_embeddings",
                       "insight_embeddings", "ai_product_analyses"]:
            try:
                # These tables reference products by seller_id + sku, or directly
                # We need to find the right column name
                r = await db.execute(text(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'sku'
                """))
                has_sku = r.fetchone()
                if has_sku:
                    result = await db.execute(text(f"DELETE FROM {table} WHERE sku LIKE 'SKU-%'"))
                    if result.rowcount > 0:
                        print(f"  Deleted {result.rowcount} rows from {table} (SKU-* data)")
                else:
                    # Check for product_id reference
                    r2 = await db.execute(text(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = '{table}' AND column_name = 'product_id'
                    """))
                    has_pid = r2.fetchone()
                    if has_pid:
                        result = await db.execute(text(f"""
                            DELETE FROM {table} WHERE product_id IN (
                                SELECT product_id FROM products WHERE sku LIKE 'SKU-%'
                            )
                        """))
                        if result.rowcount > 0:
                            print(f"  Deleted {result.rowcount} rows from {table} (SKU-* product_id refs)")
            except Exception as e:
                print(f"  [SKIP] {table}: {e}")

        # Now delete SKU-* products
        result = await db.execute(text("DELETE FROM products WHERE sku LIKE 'SKU-%'"))
        print(f"  Deleted {result.rowcount} SKU-* products")

        # ─── Step 3: Remove duplicate BB-* products ────────────────
        # Keep only one row per SKU (the one with the lowest product_id)
        r = await db.execute(text("""
            SELECT sku, COUNT(*) as cnt FROM products 
            WHERE sku LIKE 'BB-%' 
            GROUP BY sku HAVING COUNT(*) > 1
            ORDER BY sku
        """))
        dupes = r.fetchall()
        total_dupes_removed = 0
        for row in dupes:
            sku, cnt = row
            # Keep the first product_id, delete the rest
            result = await db.execute(text("""
                DELETE FROM products WHERE product_id IN (
                    SELECT product_id FROM products 
                    WHERE sku = :sku 
                    ORDER BY product_id 
                    OFFSET 1
                )
            """), {"sku": sku})
            total_dupes_removed += result.rowcount
            if result.rowcount > 0:
                print(f"  Deduped {sku}: removed {result.rowcount} duplicate(s) (had {cnt})")
        
        print(f"  Total duplicates removed: {total_dupes_removed}")

        # ─── Step 4: Update BB-* product names ─────────────────────
        updated = 0
        for sku, (name, category) in BB_PRODUCTS.items():
            result = await db.execute(
                text("UPDATE products SET product_name = :name, category = :category WHERE sku = :sku"),
                {"name": name, "category": category, "sku": sku}
            )
            if result.rowcount > 0:
                updated += result.rowcount
        print(f"  Updated {updated} BB-* product names")

        await db.commit()

        # ─── Step 5: Verify final state ────────────────────────────
        r = await db.execute(text("SELECT COUNT(*) FROM products"))
        total_after = r.scalar()
        r = await db.execute(text("""
            SELECT sku, product_name, category FROM products 
            ORDER BY sku
        """))
        rows = r.fetchall()
        print(f"\nAFTER: {total_after} total products")
        print("─" * 70)
        for row in rows:
            print(f"  {row[0]:12s}  {row[1]:45s}  [{row[2]}]")

asyncio.run(main())
