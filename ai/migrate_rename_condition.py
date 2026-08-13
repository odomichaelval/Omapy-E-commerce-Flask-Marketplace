"""
One-time migration: renames products.product_brand -> products.product_condition.
Existing data (the "New"/"Used" values already in that column) is preserved as-is.

Run once from your project root:
    python -m ai.migrate_rename_condition
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "database.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)

    # Check the column hasn't already been renamed (safe to re-run)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(products)").fetchall()]
    if "product_condition" in columns:
        print("Already migrated — product_condition column exists. Nothing to do.")
        conn.close()
        return
    if "product_brand" not in columns:
        print("ERROR: product_brand column not found. Check DB_PATH is correct.")
        conn.close()
        return

    conn.execute("ALTER TABLE products RENAME COLUMN product_brand TO product_condition")
    conn.commit()
    conn.close()
    print("Migration complete: product_brand -> product_condition")


if __name__ == "__main__":
    confirm = input("Backed up database.db? This alters your live schema. (yes/no): ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
    else:
        migrate()