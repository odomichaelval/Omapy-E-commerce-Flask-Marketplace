"""
Console test for both SHAP explainers before wiring into Flask.

Run:
    python -m ai.test_explain
"""

from ai.explain import explain_price, explain_category


def main():
    text = "Gaming laptop 16GB RAM fast SSD great for students"
    category = "Laptops"
    condition = "Used"

    print("=== Price Explanation ===")
    price_result = explain_price(text, category, condition)
    print(f"Base price (model average): £{price_result['base_price']}")
    for item in price_result["breakdown"]:
        sign = "+" if item["impact"] >= 0 else ""
        print(f"  {item['factor']}: {sign}£{item['impact']}")
    print(f"Final predicted price: £{price_result['predicted_price']}")

    print("\n=== Category Explanation ===")
    cat_result = explain_category(text)
    print(f"Predicted category: {cat_result['predicted_category']}")
    print("Top contributing words:")
    for w in cat_result["top_words"]:
        print(f"  '{w['word']}': {w['impact']}")


if __name__ == "__main__":
    main()