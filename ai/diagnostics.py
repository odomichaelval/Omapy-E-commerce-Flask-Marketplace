"""
Deeper evaluation of the trained models than a single train/test split
can give at this dataset size. Run after train_models.py.

    python -m ai.diagnostics
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, cross_val_predict, StratifiedKFold
from sklearn.metrics import confusion_matrix

from ai.data_export import get_products_dataframe

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


def diagnose_classifier(df):
    classifier = joblib.load(os.path.join(MODELS_DIR, "category_classifier.joblib"))

    X = df["text"]
    y = df["product_category"]

    # 5-fold cross-validation: every row gets used as test data exactly
    # once across 5 rounds, giving a far more stable accuracy estimate
    # than one lucky/unlucky 80/20 split on only 120 rows.
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(classifier, X, y, cv=cv)

    print("\n=== Classifier: 5-fold Cross-Validation ===")
    print(f"Fold accuracies: {[f'{s:.2%}' for s in scores]}")
    print(f"Mean accuracy:   {scores.mean():.2%}  (+/- {scores.std():.2%})")

    # Confusion matrix across all folds - shows exactly which categories
    # get mistaken for which others.
    y_pred = cross_val_predict(classifier, X, y, cv=cv)
    labels = sorted(y.unique())
    cm = confusion_matrix(y, y_pred, labels=labels)

    print("\nConfusion matrix (rows = actual, columns = predicted):")
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    print(cm_df)


def diagnose_clusters(df):
    vectorizer = joblib.load(os.path.join(MODELS_DIR, "cluster_vectorizer.joblib"))
    kmeans = joblib.load(os.path.join(MODELS_DIR, "cluster_model.joblib"))

    feature_names = np.array(vectorizer.get_feature_names_out())

    print("\n=== Clusterer: top words per cluster ===")
    for i, center in enumerate(kmeans.cluster_centers_):
        top_indices = center.argsort()[-8:][::-1]
        top_words = feature_names[top_indices]
        size = (kmeans.labels_ == i).sum()
        print(f"Cluster {i} ({size} products): {', '.join(top_words)}")


if __name__ == "__main__":
    df = get_products_dataframe()
    diagnose_classifier(df)
    diagnose_clusters(df)