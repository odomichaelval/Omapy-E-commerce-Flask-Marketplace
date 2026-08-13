"""
Quick manual test of semantic_search() without Flask.

Run:
    python -m ai.test_semantic_search "affordable lightning cable"
"""

import sys
from ai.predict import semantic_search
from ai.data_export import get_products_dataframe


def main():
    if len(sys.argv) < 2:
        print('Usage: python -m ai.test_semantic_search "your search query"')
        return

    query = " ".join(sys.argv[1:])
    df = get_products_dataframe()

    results = semantic_search(query, top_n=10)

    print(f"\nQuery: '{query}'")
    print(f"Found {len(results)} semantic matches:\n")
    for pid in results:
        row = df[df["id"] == pid].iloc[0]
        print(f"  #{pid}: {row['product_name']} ({row['product_category']}) - {row['product_description'][:60]}")


if __name__ == "__main__":
    main()