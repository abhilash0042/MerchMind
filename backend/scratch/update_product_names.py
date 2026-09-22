"""Update product names and categories to realistic e-commerce names."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

# Realistic product name + category mapping for all 35 SKUs
SKU_MAP = {
    # Brew Boulevard products (BB-* SKUs) — Coffee & Beverage brand
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
    "BB-IN-013": ("Pour Over Dripper Set — Ceramic", "Accessories"),
    "BB-IN-014": ("Stainless Steel Travel Tumbler 16oz", "Accessories"),
    "BB-GF-015": ("Coffee Lover Gift Box — Premium", "General"),

    # Test data products (SKU-* SKUs) — Multi-category e-commerce
    "SKU-0001": ("Sony WH-1000XM5 Wireless Headphones", "Electronics"),
    "SKU-0002": ("Apple AirPods Pro 2nd Generation", "Electronics"),
    "SKU-0003": ("Samsung Galaxy Buds2 Pro", "Electronics"),
    "SKU-0004": ("JBL Charge 5 Bluetooth Speaker", "Electronics"),
    "SKU-0005": ("Anker PowerCore 26800mAh Power Bank", "Electronics"),
    "SKU-0006": ("Nike Air Max 270 Running Shoes", "Apparel"),
    "SKU-0007": ("Levi's 501 Original Fit Jeans", "Apparel"),
    "SKU-0008": ("Adidas Ultraboost 22 Sneakers", "Apparel"),
    "SKU-0009": ("Ralph Lauren Polo Classic Fit Tee", "Apparel"),
    "SKU-0010": ("Under Armour Tech 2.0 Workout Shirt", "Apparel"),
    "SKU-0011": ("Dyson V15 Detect Cordless Vacuum", "Home"),
    "SKU-0012": ("Instant Pot Duo 7-in-1 Pressure Cooker", "Home"),
    "SKU-0013": ("Philips Sonicare DiamondClean Toothbrush", "Home"),
    "SKU-0014": ("Nespresso Vertuo Next Coffee Machine", "Home"),
    "SKU-0015": ("iRobot Roomba i7+ Self-Emptying Robot", "Home"),
    "SKU-0016": ("CeraVe Moisturizing Cream 19oz", "Beauty"),
    "SKU-0017": ("The Ordinary Niacinamide 10% Serum", "Beauty"),
    "SKU-0018": ("Olaplex No.3 Hair Perfector Treatment", "Beauty"),
    "SKU-0019": ("Neutrogena Hydro Boost Water Gel", "Beauty"),
    "SKU-0020": ("Maybelline Lash Sensational Mascara", "Beauty"),
}


async def main():
    from app.db.session import get_db

    async for db in get_db():
        updated = 0
        for sku, (name, category) in SKU_MAP.items():
            result = await db.execute(
                text("UPDATE products SET product_name = :name, category = :category WHERE sku = :sku"),
                {"name": name, "category": category, "sku": sku}
            )
            if result.rowcount > 0:
                print(f"  Updated {result.rowcount} row(s): {sku} -> {name} [{category}]")
                updated += result.rowcount

        await db.commit()
        print(f"\nDone! Updated {updated} total product rows.")

asyncio.run(main())
