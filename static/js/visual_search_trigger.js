document.addEventListener("DOMContentLoaded", function () {
  const trigger = document.getElementById("visual-search-trigger");
  const fileInput = document.getElementById("visual-search-input");
  const form = document.getElementById("visual-search-form");

  if (!trigger || !fileInput || !form) return;

  trigger.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files.length > 0) {
      form.submit();
    }
  });
});