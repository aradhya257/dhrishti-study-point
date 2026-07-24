// Dhrishti Study Point — main.js
// Handles dark/light theme toggle and small UX helpers.

(function () {
  const root = document.documentElement;
  const toggleBtn = document.getElementById("themeToggle");
  const STORAGE_KEY = "dsp-theme";

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (toggleBtn) {
      const icon = toggleBtn.querySelector("i");
      if (icon) {
        icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
      }
    }
  }

  // Load saved preference (falls back to light)
  const saved = localStorage.getItem(STORAGE_KEY) || "light";
  applyTheme(saved);

  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(STORAGE_KEY, next);
    });
  }

  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll(".alert").forEach(function (alertEl) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      bsAlert.close();
    }, 5000);
  });
})();
