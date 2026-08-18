document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("buyer_search");
  const resultsBox = document.getElementById("buyer_results");
  const buyerIdField = document.getElementById("buyer_id");
  const selectedBuyerDiv = document.getElementById("selected_buyer");
  const submitBtn = document.getElementById("confirm-submit-btn");

  let debounceTimer;

  searchInput.addEventListener("input", () => {
    buyerIdField.value = "";
    submitBtn.disabled = true;
    selectedBuyerDiv.textContent = "";

    clearTimeout(debounceTimer);
    const query = searchInput.value.trim();

    if (query.length < 3) {
      resultsBox.innerHTML = "";
      return;
    }

    debounceTimer = setTimeout(async () => {
      const res = await fetch(`/api/search_buyers?q=${encodeURIComponent(query)}`);
      const data = await res.json();

      if (!data.results.length) {
        resultsBox.innerHTML = `<div class="list-group-item text-muted">No matching users</div>`;
        return;
      }

      resultsBox.innerHTML = data.results
        .map(u => `<button type="button" class="list-group-item list-group-item-action buyer-option" data-id="${u.id}" data-username="${u.username}">${u.username}</button>`)
        .join("");

      resultsBox.querySelectorAll(".buyer-option").forEach(btn => {
        btn.addEventListener("click", () => {
          buyerIdField.value = btn.dataset.id;
          selectedBuyerDiv.textContent = `Selected buyer: ${btn.dataset.username}`;
          searchInput.value = btn.dataset.username;
          resultsBox.innerHTML = "";
          submitBtn.disabled = false;
        });
      });
    }, 400);
  });

  document.addEventListener("click", (e) => {
    if (!resultsBox.contains(e.target) && e.target !== searchInput) {
      resultsBox.innerHTML = "";
    }
  });
});