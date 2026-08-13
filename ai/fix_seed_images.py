"""
Fixes image fields on the synthetic products inserted by seed_training_data.py.
Only touches rows still pointing at the generic /static/img/product-N.png
placeholders, so it's safe to run without affecting your original 27
real listings (which use /static/uploads/... images).

Run once from your project root:
    python -m ai.fix_seed_images
"""

import random
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "database.db")

# Only files confirmed by filename to be real, on-topic product photos.
# Deliberately excludes: portrait/selfie-style photos, ambiguous
# Amazon-CDN-style filenames, and leftover theme placeholders.
CATEGORY_IMAGE_POOLS = {
    "Accessories":  ["watch.jpg", "watch2.jpg", "watch3.jpg", "headset1.jpg", "headset2.jpg"],
    "Clothings":    ["arsenal jersey1.jpg", "arsenal jersey2.jpg", "arsenal jersey3.jpg",
                      "zara1.jpg", "zara2.jpg", "zara3.jpg"],
    "Electronics":  ["samsung tv.jpg", "samsung tv2.jpg", "samsung tv3.jpg",
                      "refrigerator1.jpg", "refrigerator2.jpg", "refrigerator3.jpg", "refrigerator4.jpg"],
    "Fashion":      ["zara1.jpg", "zara2.jpg", "zara3.jpg",
                      "nike shoes1.jpg", "nike shoes2.jpg", "nike shoes3.jpg"],
    "Furniture":    ["desk1.jpg", "desk2.jpg", "desk3.jpg", "shelf1.jpg", "shelf2.jpg"],
    "Gadgets":      ["keyboardandmouse.jpg", "keyboardandmouse1.jpg", "keyboardandmouse2.jpg",
                      "keyboardandmouse3.jpg", "headset1.jpg", "headset2.jpg"],
    "Laptops":      ["asus laptop1.jpg", "asus laptop2.jpg", "asus laptop3.jpg", "asus laptop4.jpg",
                      "hplaptop1.jpg", "hplaptop2.jpg", "hplaptop3.jpg"],
    "Smartphones":  ["z fold1.jpg", "z fold2.jpg", "z fold3.jpg"],
    "Sports":       ["nike shoes1.jpg", "nike shoes2.jpg", "nike shoes3.jpg",
                      "nike socks1.jpg", "nike socks2.jpg", "nike socks3.jpg"],
    "Stationery":   ["pencil case1.jpg", "pencil case2.jpg", "pencil case3.jpg"],
}


def fix_images():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT id, product_category FROM products WHERE product_image LIKE '/static/img/product-%'"
    ).fetchall()

    updated = 0
    skipped_categories = set()

    for row in rows:
        category = row["product_category"]
        pool = CATEGORY_IMAGE_POOLS.get(category)

        if not pool:
            skipped_categories.add(category)
            continue

        picks = [random.choice(pool) for _ in range(4)]
        main, g1, g2, g3 = [f"/static/uploads/{p}" for p in picks]

        conn.execute(
            """UPDATE products
               SET product_image = ?, product_gallery1 = ?, product_gallery2 = ?, product_gallery3 = ?
               WHERE id = ?""",
            (main, g1, g2, g3, row["id"]),
        )
        updated += 1

    conn.commit()
    conn.close()

    print(f"Updated {updated} product(s) with real category-matched images.")
    if skipped_categories:
        print(f"No image pool defined for: {', '.join(skipped_categories)} — left unchanged.")


if __name__ == "__main__":
    confirm = input(
        "This will overwrite image fields on any product still using "
        "/static/img/product-N.png placeholders. Backed up database.db? (yes/no): "
    )
    if confirm.strip().lower() != "yes":
        print("Aborted.")
    else:
        fix_images()