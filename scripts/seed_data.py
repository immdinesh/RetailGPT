"""Seed 1,000+ retail records: products (Adidas, Nike), inventory, sales."""
import random
from datetime import date, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import get_db_config

BRANDS = ("Adidas", "Nike")
CATEGORIES = ("Footwear", "Apparel", "Accessories", "Equipment")

# Sample product names by brand
PRODUCTS_BY_BRAND = {
    "Adidas": [
        "Ultraboost 22", "Stan Smith", "Superstar", "NMD R1", "Gazelle",
        "Trefoil Hoodie", "Tiro Pants", "Predator Boots", "Adilette Slides",
        "Running Shorts", "Training Jacket", "Backpack", "Cap", "Socks 3-Pack",
    ] * 8,  # ~112 base, we'll slice
    "Nike": [
        "Air Max 90", "Air Force 1", "Pegasus 40", "Dunk Low", "Blazer",
        "Dri-FIT Tee", "Sportswear Joggers", "Mercurial Cleats", "Benassi Slides",
        "Pro Shorts", "Windrunner", "Gym Bag", "Legacy91 Cap", "Elite Socks",
    ] * 8,
}


def generate_products(n_total=520):
    """Generate product rows (Adidas + Nike) with unique SKUs."""
    rows = []
    seen_sku = set()
    idx = 0
    for brand in BRANDS:
        names = PRODUCTS_BY_BRAND[brand][: (n_total // 2)]
        for name in names:
            sku = f"{brand[:2].upper()}-{idx:05d}"
            if sku in seen_sku:
                continue
            seen_sku.add(sku)
            cat = random.choice(CATEGORIES)
            unit_price = round(random.uniform(19.99, 249.99), 2)
            rows.append((sku, name, brand, cat, unit_price))
            idx += 1
            if len(rows) >= n_total:
                break
        if len(rows) >= n_total:
            break
    return rows


def generate_inventory(product_ids):
    """One inventory row per product (optional: multi-warehouse)."""
    return [(pid, random.randint(5, 500), "Main") for pid in product_ids]


def generate_sales(product_ids, n_sales=600):
    """Generate 600+ sales over last 12 months."""
    rows = []
    regions = ("North", "South", "East", "West", "Online", None)
    end = date.today()
    start = end - timedelta(days=365)
    for _ in range(n_sales):
        pid = random.choice(product_ids)
        qty = random.randint(1, 5)
        unit_price = round(random.uniform(25.0, 200.0), 2)
        total = round(qty * unit_price, 2)
        d = start + timedelta(days=random.randint(0, 365))
        region = random.choice(regions)
        rows.append((pid, qty, unit_price, total, d, region))
    return rows


def main():
    cfg = get_db_config()
    conn = mysql.connector.connect(**cfg)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM products")
    conn.commit()

    products = generate_products(520)
    cursor.executemany(
        "INSERT INTO products (sku, name, brand, category, unit_price) VALUES (%s, %s, %s, %s, %s)",
        products,
    )
    conn.commit()

    product_ids = list(range(1, len(products) + 1))
    inventory = generate_inventory(product_ids)
    cursor.executemany(
        "INSERT INTO inventory (product_id, quantity, warehouse) VALUES (%s, %s, %s)",
        inventory,
    )
    conn.commit()

    sales = generate_sales(product_ids, n_sales=600)
    cursor.executemany(
        """INSERT INTO sales (product_id, quantity, unit_price, total_amount, sale_date, region)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        sales,
    )
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM products")
    np = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM inventory")
    ni = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sales")
    ns = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f"Seeded: {np} products, {ni} inventory rows, {ns} sales ({np + ni + ns} total records).")


if __name__ == "__main__":
    main()
