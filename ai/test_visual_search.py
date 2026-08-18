"""
Quick manual test of visual similarity before wiring into Flask.

Run:
    python -m ai.test_visual_search 90
"""

import sys
import os
import joblib
from sklearn.metrics.pairwise import cosine_similarity

from ai.data_export import get_products_dataframe

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m ai.test_visual_search <product_id>")
        return

    product_id = int(sys.argv[1])
    data = joblib.load(os.path.join(MODELS_DIR, "visual_embeddings.joblib"))

    if product_id not in data["ids"]:
        print(f"Product {product_id} has no visual embedding (missing image at index time).")
        return

    idx = data["ids"].index(product_id)
    target_vec = data["embeddings"][idx].reshape(1, -1)
    similarities = cosine_similarity(target_vec, data["embeddings"]).flatten()

    ranked = sorted(zip(data["ids"], similarities), key=lambda x: x[1], reverse=True)
    ranked = [(pid, score) for pid, score in ranked if pid != product_id][:8]

    df = get_products_dataframe()
    target_row = df[df["id"] == product_id].iloc[0]
    print(f"\nTarget: #{product_id} {target_row['product_name']} ({target_row['product_category']})\n")

    print("Visually similar products:")
    for pid, score in ranked:
        row = df[df["id"] == pid].iloc[0]
        print(f"  #{pid}: {row['product_name']} ({row['product_category']}) - similarity {score:.3f}")


if __name__ == "__main__":
    main()