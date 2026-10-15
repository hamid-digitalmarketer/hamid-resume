/* hamid-resume — shared front-end behaviors */
(function () {
  "use strict";

  /* Mobile hamburger nav */
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* Projects directory: live search + category filters */
  var searchBox = document.getElementById("project-search");
  var filterBtns = Array.prototype.slice.call(document.querySelectorAll(".filter-btn"));
  var cards = Array.prototype.slice.call(document.querySelectorAll("[data-project-card]"));
  var noResults = document.getElementById("no-results");
  var activeFilter = "all";

  function applyFilters() {
    if (!cards.length) return;
    var q = searchBox ? searchBox.value.trim().toLowerCase() : "";
    var visible = 0;
    cards.forEach(function (card) {
      var text = (card.getAttribute("data-search") || "").toLowerCase();
      var cats = (card.getAttribute("data-cats") || "").split(",");
      var matchCat = activeFilter === "all" || cats.indexOf(activeFilter) !== -1;
      var matchQ = q === "" || text.indexOf(q) !== -1;
      var show = matchCat && matchQ;
      card.style.display = show ? "" : "none";
      if (show) visible += 1;
    });
    if (noResults) noResults.classList.toggle("visible", visible === 0);
  }

  if (searchBox) {
    searchBox.addEventListener("input", applyFilters);
  }
  filterBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filterBtns.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      activeFilter = btn.getAttribute("data-filter") || "all";
      applyFilters();
    });
  });

  /* Lazy-load enhancement for browsers without native support is unnecessary:
     images already use loading="lazy" in markup. */
})();
