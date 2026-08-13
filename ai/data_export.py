"""
Exports product data from database.db into a pandas DataFrame for use by
the AI training scripts. Reads directly via sqlite3, matching the same
connection pattern used in db/db.py.
"""

import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "database.db")


def get_products_dataframe():
    """
    Loads all products from the database into a pandas DataFrame,
    with a combined 'text' column (name + description) ready for
    TF-IDF vectorisation.
    """
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT id, product_name, product_description, product_category,
               product_condition, product_price
        FROM products
        """,
        conn,
    )
    conn.close()

    # Fill any missing text fields so TF-IDF doesn't choke on NaN
    df["product_name"] = df["product_name"].fillna("")
    df["product_description"] = df["product_description"].fillna("")
    df["product_condition"] = df["product_condition"].fillna("Unknown")
    df["product_category"] = df["product_category"].fillna("Unknown")

    # Combined text field used as input for classification/clustering
    df["text"] = df["product_name"] + " " + df["product_description"]

    return df


if __name__ == "__main__":
    # Quick sanity check: python -m ai.data_export
    data = get_products_dataframe()
    print(f"Loaded {len(data)} products.")
    print(data["product_category"].value_counts())
    print(data.head())