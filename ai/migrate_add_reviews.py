"""
One-time migration: adds transactions and reviews tables.
Safe to re-run - uses CREATE TABLE IF NOT EXISTS.

Run once from your project root:
    python -m ai.migrate_add_reviews
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "database.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vendor_id INTEGER NOT NULL REFERENCES users(id),
            buyer_id INTEGER NOT NULL REFERENCES users(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            UNIQUE(buyer_id, product_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            transaction_id INTEGER NOT NULL UNIQUE REFERENCES transactions(id),
            reviewer_id INTEGER NOT NULL REFERENCES users(id),
            vendor_id INTEGER NOT NULL REFERENCES users(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            rating INTEGER NOT NULL,
            review_text TEXT NOT NULL,
            sentiment_label TEXT,
            sentiment_score REAL
        )
    """)

    conn.commit()
    conn.close()
    print("Migration complete: transactions and reviews tables ready.")


if __name__ == "__main__":
    migrate()