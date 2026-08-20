"""
Builds sentence-embedding vectors for every product's text and saves them,
so semantic search at request time only has to encode the search query
itself (fast) rather than re-embedding the whole catalog every time.

Uses a pretrained sentence-transformer model - unlike the TF-IDF used
elsewhere in this project, this model was trained on huge amounts of
general text and captures MEANING, not just shared words. E.g. "affordable
lightning cable" and "cheap iPhone charger" score as similar even though
they share almost no vocabulary - TF-IDF could never do that.

Run once (and again any time products change significantly):
    python -m ai.build_semantic_index
"""

import os
import joblib
from sentence_transformers import SentenceTransformer

from ai.data_export import get_products_dataframe

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Small (~80MB), fast, good general-purpose semantic model - no GPU needed
MODEL_NAME = "all-MiniLM-L6-v2"


def build_index():
    df = get_products_dataframe()

    print(f"Loading sentence-transformer model '{MODEL_NAME}' (first run downloads it)...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Encoding {len(df)} product listings into embeddings...")
    embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)

    joblib.dump({
        "ids": df["id"].tolist(),
        "embeddings": embeddings,
    }, os.path.join(MODELS_DIR, "semantic_embeddings.joblib"))

    print(f"Saved: ai/models/semantic_embeddings.joblib ({len(df)} products)")


if __name__ == "__main__":
    build_index()