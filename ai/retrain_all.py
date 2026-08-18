"""
Re-trains/refreshes all AI models on the CURRENT state of database.db
and static/uploads, covering all 7 features:

  - Classification    (retrained)
  - Regression         (retrained)
  - Clustering          (retrained)
  - NLP semantic search  (embeddings rebuilt)
  - Neural Networks / visual search (image embeddings rebuilt)
  - Sentiment Analysis - NOT retrained on purpose: VADER is a fixed,
    pretrained lexicon, not trained on Omapy's data. Nothing to update.
  - Explainable AI - NOT retrained separately on purpose: SHAP has no
    model of its own - ai/explain.py reads the same classifier/regressor
    .joblib files this script refreshes, so explanations update
    automatically once those retrain and Flask restarts.

Run this any time you've added meaningful new products, categories, or
images - otherwise models stay frozen at whatever the catalog looked
like the last time this ran ("model drift").

    python -m ai.retrain_all
"""

from ai.train_models import get_products_dataframe, train_classifier, train_regressor, train_clusterer
from ai.build_semantic_index import build_index as build_semantic_index
from ai.build_visual_index import build_index as build_visual_index


def retrain_all():
    df = get_products_dataframe()
    print(f"Retraining on {len(df)} current products across {df['product_category'].nunique()} categories.\n")

    print("[1/5] Classification...")
    train_classifier(df)

    print("\n[2/5] Regression...")
    train_regressor(df)

    print("\n[3/5] Clustering...")
    train_clusterer(df)

    print("\n[4/5] NLP semantic search index...")
    build_semantic_index()

    print("\n[5/5] Visual (image) search index - this is the slow one...")
    build_visual_index()

    print("\nDone. Classification, Regression, Clustering, NLP, and Visual Search are refreshed.")
    print("Sentiment Analysis needs no retraining (pretrained VADER lexicon).")
    print("Explainable AI needs no separate step (reads the models just refreshed).")
    print("\nRESTART FLASK NOW - predict.py and explain.py only load models at startup.")


if __name__ == "__main__":
    retrain_all()