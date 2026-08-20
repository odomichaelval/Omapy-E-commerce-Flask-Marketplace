"""
Explainable AI (XAI) layer using SHAP - explains WHY the price regressor
and category classifier produced their outputs, not just what they
predicted. Builds directly on the already-trained models in ai/models/,
no new training required.
"""

import os
import shap
import joblib
import pandas as pd
import numpy as np

from ai.data_export import get_products_dataframe

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

_regressor_pipeline = joblib.load(os.path.join(MODELS_DIR, "price_regressor.joblib"))
_classifier_pipeline = joblib.load(os.path.join(MODELS_DIR, "category_classifier.joblib"))

_regressor_preprocessor = _regressor_pipeline.named_steps["preprocess"]
_regressor_model = _regressor_pipeline.named_steps["reg"]
_regressor_explainer = shap.TreeExplainer(_regressor_model)
def _to_scalar(value):
    """Converts numpy arrays/scalars to a plain Python float, safely."""
    if isinstance(value, np.ndarray):
        return float(value.flatten()[0])
    return float(value)

_classifier_tfidf = _classifier_pipeline.named_steps["tfidf"]
_classifier_clf = _classifier_pipeline.named_steps["clf"]

_full_df = get_products_dataframe()
_bg_df = _full_df.sample(n=min(30, len(_full_df)), random_state=42)
_bg_matrix = _classifier_tfidf.transform(_bg_df["text"]).toarray()
_classifier_explainer = shap.LinearExplainer(_classifier_clf, _bg_matrix)


def explain_price(text, category, condition):
    """
    Breaks the predicted price down into: category's effect, condition's
    effect, and the combined effect of the description's wording (summed
    into one bucket - showing 300 individual word weights would be noise,
    not insight).
    """
    text = (text or "").strip()
    if not text or not category or not condition:
        return None

    row = pd.DataFrame([{
        "text": text,
        "product_category": category,
        "product_condition": condition,
    }])

    features = _regressor_preprocessor.transform(row)
    if hasattr(features, "toarray"):
        features = features.toarray()

    feature_names = _regressor_preprocessor.get_feature_names_out()
    shap_values = _regressor_explainer.shap_values(features)[0]
    base_value = _to_scalar(_regressor_explainer.expected_value)

    text_contribution = 0.0
    category_contribution = 0.0
    condition_contribution = 0.0

    for name, value in zip(feature_names, shap_values):
        if name.startswith("text__"):
            text_contribution += value
        elif name.startswith("cat__product_category"):
            category_contribution += value
        elif name.startswith("cat__product_condition"):
            condition_contribution += value

    breakdown = [
        {"factor": f"Category: {category}", "impact": round(category_contribution)},
        {"factor": f"Condition: {condition}", "impact": round(condition_contribution)},
        {"factor": "Description wording", "impact": round(text_contribution)},
    ]
    breakdown.sort(key=lambda x: abs(x["impact"]), reverse=True)

    return {
        "base_price": round(base_value),
        "breakdown": breakdown,
        "predicted_price": round(base_value + float(sum(shap_values))),
    }


def explain_category(text, top_n_words=5):
    """
    Shows which words in the listing text pushed the model toward its
    predicted category. Uses SHAP's LinearExplainer since the classifier
    is Logistic Regression (a linear model) - this is exact, not an
    approximation.
    """
    text = (text or "").strip()
    if not text:
        return None

    vec_dense = _classifier_tfidf.transform([text]).toarray()
    predicted_class = _classifier_pipeline.predict([text])[0]
    class_index = list(_classifier_clf.classes_).index(predicted_class)

    raw_shap = _classifier_explainer.shap_values(vec_dense)

    # SHAP's output shape for multi-class linear models varies by version -
    # handle the possibilities rather than assume one.
    if isinstance(raw_shap, list):
        class_shap = raw_shap[class_index][0]
    elif raw_shap.ndim == 3:
        class_shap = raw_shap[0][:, class_index]
    else:
        class_shap = raw_shap[0]

    feature_names = _classifier_tfidf.get_feature_names_out()
    present_mask = vec_dense[0] > 0

    contributions = [
        (feature_names[i], float(class_shap[i]))
        for i in range(len(feature_names))
        if present_mask[i]
    ]
    contributions.sort(key=lambda x: x[1], reverse=True)

    top_words = [{"word": w, "impact": round(v, 3)} for w, v in contributions[:top_n_words]]

    return {
        "predicted_category": predicted_class,
        "top_words": top_words,
    }