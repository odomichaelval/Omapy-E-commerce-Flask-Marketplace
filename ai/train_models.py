"""
Trains three AI models on Omapy's product data and saves them to ai/models/:

1. Category classifier   - predicts product_category from listing text
2. Price regressor       - predicts product_price from text + category + condition
3. Product clusterer     - groups similar products for "related products"

Run once from your project root (re-run any time your data changes):
    python -m ai.train_models
"""

import os
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score

from ai.data_export import get_products_dataframe

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


# ============================================================
# 1. CATEGORY CLASSIFIER
# ============================================================
def train_classifier(df):
    """
    Predicts product_category from the listing's text (name + description).

    Pipeline: TF-IDF (unigrams + bigrams, stopwords removed) -> Logistic Regression.

    Logistic Regression (not a neural net) is used deliberately: with ~127
    rows across 10 categories, a simpler linear model overfits less, and
    its coefficients per word are directly explainable in the report.
    """
    X = df["text"]
    y = df["product_category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=500)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\n=== Category Classifier ===")
    print(f"Test accuracy: {acc:.2%}")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Refit on ALL data before saving - in a small-data project every
    # row matters for the deployed model. Note this means the accuracy
    # printed above is only indicative of the final saved model, not an
    # exact measurement of it - worth stating explicitly in your report.
    pipeline.fit(X, y)
    joblib.dump(pipeline, os.path.join(MODELS_DIR, "category_classifier.joblib"))
    print("Saved: ai/models/category_classifier.joblib")

    return pipeline


# ============================================================
# 2. PRICE REGRESSOR
# ============================================================
def train_regressor(df):
    """
    Predicts product_price from text + category + condition.

    Pipeline: ColumnTransformer(TF-IDF on text, OneHot on category/condition)
              -> Random Forest Regressor.

    Random Forest (not Linear Regression) is used because price isn't a
    linear function of these features - e.g. condition's effect on price
    differs by category (a used laptop drops more in £ than a used phone
    case). Random Forest also gives feature_importances_ for free, which
    feeds directly into the Explainable AI stage later.
    """
    X = df[["text", "product_category", "product_condition"]]
    y = df["product_price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessor = ColumnTransformer([
        ("text", TfidfVectorizer(stop_words="english", max_features=300), "text"),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["product_category", "product_condition"]),
    ])

    pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("reg", RandomForestRegressor(n_estimators=200, random_state=42)),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n=== Price Regressor ===")
    print(f"Test MAE: £{mae:.2f}")
    print(f"Test R²:  {r2:.3f}")

    pipeline.fit(X, y)
    joblib.dump(pipeline, os.path.join(MODELS_DIR, "price_regressor.joblib"))
    print("Saved: ai/models/price_regressor.joblib")

    return pipeline


# ============================================================
# 3. PRODUCT CLUSTERER (for smarter "related products")
# ============================================================
def train_clusterer(df, n_clusters=20):
    """
    Groups products by text similarity (TF-IDF + KMeans), independent of
    their declared category. This will let us later suggest "related
    products" that are genuinely similar in wording/description, catching
    cases your current get_related_products() (exact category match only)
    would miss - e.g. a "gaming laptop" and a "gaming mouse" being related
    even though they're in different categories.
    """
    X = df["text"]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=500)
    X_vec = vectorizer.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_vec)

    print("\n=== Product Clusterer ===")
    print(f"Grouped {len(df)} products into {n_clusters} clusters.")
    print(pd.Series(cluster_labels).value_counts().sort_index())

    joblib.dump(vectorizer, os.path.join(MODELS_DIR, "cluster_vectorizer.joblib"))
    joblib.dump(kmeans, os.path.join(MODELS_DIR, "cluster_model.joblib"))

    # Lookup table so predict.py doesn't need to re-vectorise every
    # product at request time - just reads which cluster each id is in.
    cluster_lookup = pd.DataFrame({"id": df["id"], "cluster": cluster_labels})
    cluster_lookup.to_csv(os.path.join(MODELS_DIR, "product_clusters.csv"), index=False)

    print("Saved: ai/models/cluster_vectorizer.joblib, cluster_model.joblib, product_clusters.csv")

    return kmeans, cluster_lookup


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    df = get_products_dataframe()
    print(f"Training on {len(df)} products across {df['product_category'].nunique()} categories.\n")

    train_classifier(df)
    train_regressor(df)
    train_clusterer(df)

    print("\nAll models trained and saved to ai/models/")