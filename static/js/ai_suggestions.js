// Live AI suggestions for category and price on the create-listing form.

document.addEventListener("DOMContentLoaded", function () {
  const nameField = document.getElementById("name");               // product_name
  const priceField = document.getElementById("email");             // product_price (yes, "email" - leftover template id)
  const categoryField = document.getElementById("category");       // product_category
  const conditionField = document.getElementById("product_condition");
  const descField = document.getElementById("message");            // product_description

  if (!nameField || !descField) return; // not on the create page

  const csrfInput = document.querySelector('input[name="csrf_token"]');
  if (!csrfInput) {
    console.error("AI suggestions: csrf_token input not found on this form.");
    return;
  }
  const csrfToken = csrfInput.value;

  // Suggestion display boxes - inserted right after each field's wrapper div
  const categoryBox = document.createElement("div");
  categoryBox.className = "ai-suggestion-box mt-1";
  categoryField.closest(".form-floating").insertAdjacentElement("afterend", categoryBox);

  const priceBox = document.createElement("div");
  priceBox.className = "ai-suggestion-box mt-1";
  priceField.closest(".form-floating").insertAdjacentElement("afterend", priceBox);

  let debounceTimer;
  function debounce(fn, delay) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fn, delay);
  }

  async function fetchCategorySuggestion() {
    const res = await fetch("/api/suggest_category", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
      body: JSON.stringify({
        product_name: nameField.value,
        product_description: descField.value,
      }),
    });
    const data = await res.json();

    if (!data.result) {
      categoryBox.innerHTML = "";
      return;
    }

    const alts = data.result.alternatives
      .map(
        (a) =>
          `<button type="button" class="ai-suggest-btn btn-outline-secondary ai-apply-category me-1" data-value="${a.category}">${a.category} (${a.confidence}%)</button>`
      )
      .join(" ");

    categoryBox.innerHTML = `<small>AI suggests: ${alts}</small>`;

    categoryBox.querySelectorAll(".ai-apply-category").forEach((btn) => {
      btn.addEventListener("click", () => {
        categoryField.value = btn.dataset.value;
        fetchPriceSuggestion();
      });
    });
  }

  async function fetchPriceSuggestion() {
    if (!categoryField.value || !conditionField.value) {
      priceBox.innerHTML = "";
      return;
    }

    const res = await fetch("/api/suggest_price", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
      body: JSON.stringify({
        product_name: nameField.value,
        product_description: descField.value,
        product_category: categoryField.value,
        product_condition: conditionField.value,
      }),
    });
    const data = await res.json();

    if (!data.price) {
      priceBox.innerHTML = "";
      return;
    }

    priceBox.innerHTML = `<small>AI suggests: £${data.price}
      <button type="button" class="ai-suggest-btn" id="ai-apply-price">Apply</button></small>`;

    document.getElementById("ai-apply-price").addEventListener("click", () => {
      priceField.value = data.price;
    });
  }

  nameField.addEventListener("input", () => debounce(fetchCategorySuggestion, 600));
  descField.addEventListener("input", () => debounce(fetchCategorySuggestion, 600));
  categoryField.addEventListener("change", fetchPriceSuggestion);
  conditionField.addEventListener("change", fetchPriceSuggestion);
});