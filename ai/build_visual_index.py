"""
Builds visual (image) embeddings for every product's photo, using a
pretrained CLIP model - a vision transformer, genuinely different
architecture from anything else in this project (which has all been
text-based). This lets products be compared by what they LOOK like,
not their name/description text.

First run downloads the model (~350MB) - needs internet, then cached.

Run once (and again whenever product images change significantly):
    python -m ai.build_visual_index
"""

#Completed the Visual Search Implementation
#Neural Network and Deep Learning Completed see code implentation below

import os
import joblib
from PIL import Image
from sentence_transformers import SentenceTransformer
import requests
from io import BytesIO

from ai.data_export import get_products_dataframe

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_NAME = "clip-ViT-B-32"


def _resolve_image_path(product_image_url):
    """product_image is stored like '/static/uploads/xyz.jpg' - resolve to a real file path."""
    if not product_image_url:
        return None
    relative = product_image_url.lstrip("/")
    full_path = os.path.join(PROJECT_ROOT, relative)
    return full_path if os.path.exists(full_path) else None


def build_index():
    df = get_products_dataframe()

    print(f"Loading CLIP model '{MODEL_NAME}' (first run downloads it)...")
    model = SentenceTransformer(MODEL_NAME)

    ids = []
    images = []
    skipped = []

    for _, row in df.iterrows():
        image_ref = row.get("product_image")
        img = None

        if image_ref and image_ref.startswith("http"):
            try:
                resp = requests.get(image_ref, timeout=10)
                img = Image.open(BytesIO(resp.content)).convert("RGB")
            except Exception:
                img = None
        else:
            path = _resolve_image_path(image_ref)
            if path:
                try:
                    img = Image.open(path).convert("RGB")
                except Exception:
                    img = None

        if img is not None:
            images.append(img)
            ids.append(int(row["id"]))
        else:
            skipped.append(int(row["id"]))

    print(f"Encoding {len(images)} product images (skipped {len(skipped)} with missing/unreadable images)...")
    embeddings = model.encode(images, show_progress_bar=True)

    joblib.dump({"ids": ids, "embeddings": embeddings},
                os.path.join(MODELS_DIR, "visual_embeddings.joblib"))

    print(f"Saved: ai/models/visual_embeddings.joblib ({len(ids)} products)")
    if skipped:
        print(f"Skipped (no valid image found): {skipped}")


if __name__ == "__main__":
    build_index()