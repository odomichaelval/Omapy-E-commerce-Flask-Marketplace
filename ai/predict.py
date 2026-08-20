"""
Loads the trained models once at import time and exposes simple functions
for app.py to call. This keeps model-loading cost paid once (at Flask
startup), not on every request.
"""

import os
import joblib
import pandas as pd

from ai.data_export import get_products_dataframe
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from PIL import Image
from io import BytesIO


MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# Load everything once when this module is first imported
_classifier = joblib.load(os.path.join(MODELS_DIR, "category_classifier.joblib"))
_regressor = joblib.load(os.path.join(MODELS_DIR, "price_regressor.joblib"))
_cluster_vectorizer = joblib.load(os.path.join(MODELS_DIR, "cluster_vectorizer.joblib"))
_cluster_model = joblib.load(os.path.join(MODELS_DIR, "cluster_model.joblib"))
_semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
_semantic_data = joblib.load(os.path.join(MODELS_DIR, "semantic_embeddings.joblib"))
_visual_model = SentenceTransformer("clip-ViT-B-32")
_visual_data = joblib.load(os.path.join(MODELS_DIR, "visual_embeddings.joblib"))

MIN_TEXT_LENGTH = 8  # below this, suggestions are too unreliable to show

# ============================================================
# 1. CATEGORY CLASSIFIER

# ============================================================
def suggest_category(text):
    """
    Given listing text (name + description), returns the predicted category
    plus the top 3 candidates with confidence percentages, so the seller
    can see alternatives rather than just one unexplained answer.
    """
    text = (text or "").strip()
    if len(text) < MIN_TEXT_LENGTH:
        return None

    probabilities = _classifier.predict_proba([text])[0]
    classes = _classifier.classes_

    ranked = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
    top3 = [{"category": c, "confidence": round(p * 100, 1)} for c, p in ranked[:3]]

    return {
        "category": top3[0]["category"],
        "confidence": top3[0]["confidence"],
        "alternatives": top3,
    }

# ============================================================
# 2. PRICE REGRESSOR
# ============================================================


def suggest_price(text, category, condition):
    """
    Given listing text, chosen category, and condition, returns a suggested
    price in whole pounds (matching product_price's INTEGER column).
    """
    text = (text or "").strip()
    if len(text) < MIN_TEXT_LENGTH or not category or not condition:
        return None

    row = pd.DataFrame([{
        "text": text,
        "product_category": category,
        "product_condition": condition,
    }])

    predicted = _regressor.predict(row)[0]
    return max(1, round(predicted))  # never suggest £0 or negative


# ============================================================
# 3. PRODUCT CLUSTERER (for smarter "related products")
# Finshed Clsutering Implementation
# ============================================================


def get_similar_products(product_id, current_category, category_limit=5, cluster_limit=5):
    """
    Related products, structured as a deliberate side-by-side comparison:
      - Up to `category_limit` products from the same category (same cluster
        first, since those are the strongest matches, then other clusters)
      - Up to `cluster_limit` products from a DIFFERENT category but the
        same AI cluster (the "AI discovery" picks)
    Total returned: up to category_limit + cluster_limit (default 10).

    If either side doesn't have enough candidates, the other side tops up
    the remainder so you still get close to the full total where possible.
    """
    df = get_products_dataframe()

    if product_id not in df["id"].values:
        return []

    X_vec = _cluster_vectorizer.transform(df["text"])
    df = df.copy()
    df["cluster"] = _cluster_model.predict(X_vec)

    target_cluster = df.loc[df["id"] == product_id, "cluster"].iloc[0]

    same_cat_same_cluster = df[
        (df["product_category"] == current_category)
        & (df["cluster"] == target_cluster)
        & (df["id"] != product_id)
    ]
    same_cat_other_cluster = df[
        (df["product_category"] == current_category)
        & (df["cluster"] != target_cluster)
        & (df["id"] != product_id)
    ]
    other_cat_same_cluster = df[
        (df["product_category"] != current_category)
        & (df["cluster"] == target_cluster)
        & (df["id"] != product_id)
    ]

    # --- Category-side picks (same cluster prioritised, then rest) ---
    category_ids = []
    for group in (same_cat_same_cluster, same_cat_other_cluster):
        for pid in group["id"]:
            if pid not in category_ids:
                category_ids.append(pid)
        if len(category_ids) >= category_limit:
            break
    category_ids = category_ids[:category_limit]

    # --- Cluster-side picks (different category, same cluster) ---
    cluster_ids = [
        pid for pid in other_cat_same_cluster["id"]
        if pid not in category_ids
    ][:cluster_limit]

    combined = category_ids + cluster_ids

    # Top up if either side came up short, using whatever's left over
    total_limit = category_limit + cluster_limit
    if len(combined) < total_limit:
        used = set(combined) | {product_id}
        leftovers = [pid for pid in df["id"] if pid not in used]
        combined += leftovers[: total_limit - len(combined)]

    return combined[:total_limit]


# ============================================================
# 4. SEMANTIC SEARCH and NLP
# ============================================================

SEMANTIC_SIMILARITY_THRESHOLD = 0.35  # tune by testing - see note below


def semantic_search(query, top_n=10):
    """
    Finds products whose MEANING matches the query, not just shared
    keywords. Falls back gracefully - if nothing clears the threshold,
    returns an empty list rather than forcing weak, irrelevant matches.
    """
    query = (query or "").strip()
    if not query:
        return []

    query_embedding = _semantic_model.encode([query])
    similarities = cosine_similarity(query_embedding, _semantic_data["embeddings"]).flatten()

    ranked = sorted(zip(_semantic_data["ids"], similarities), key=lambda x: x[1], reverse=True)
    matches = [(pid, score) for pid, score in ranked if score >= SEMANTIC_SIMILARITY_THRESHOLD]

    return [pid for pid, score in matches[:top_n]]

# ============================================================
# 5. IMAGE SEARCH, Deep Learning/visual search
# ============================================================


def search_by_image(image_bytes, limit=10):
    """
    The advanced feature: upload any photo, find listings that visually
    resemble it. Encodes the uploaded image with the SAME CLIP model used
    to index every product photo, then ranks by cosine similarity.
    """
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return []

    query_embedding = _visual_model.encode([img])
    similarities = cosine_similarity(query_embedding, _visual_data["embeddings"]).flatten()

    ranked = sorted(zip(_visual_data["ids"], similarities), key=lambda x: x[1], reverse=True)
    return [pid for pid, score in ranked[:limit]]