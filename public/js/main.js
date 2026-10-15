/* hamid-resume — shared front-end behaviors */
(function () {
  "use strict";

  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");

  /* Mobile hamburger nav */
  if (toggle && links) {
    function setOpen(open) {
      links.classList.toggle("open", open);
      toggle.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }

    toggle.addEventListener("click", function () {
      setOpen(!links.classList.contains("open"));
    });

    /* Close after choosing a link */
    links.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });

    /* Close with Escape */
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && links.classList.contains("open")) setOpen(false);
    });

    /* Close when clicking outside the menu */
    document.addEventListener("click", function (e) {
      if (links.classList.contains("open") && !links.contains(e.target) && e.target !== toggle) {
        setOpen(false);
      }
    });
  }

  /* Active nav state based on the current path */
  (function () {
    var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-links a"));
    if (!navLinks.length) return;

    function normalize(p) {
      return p.replace(/\/+$/, "").replace(/\/index\.html$/i, "").replace(/\/+$/, "") || "/";
    }

    var here = normalize(location.pathname);
    var dir = location.pathname.replace(/[^/]*$/, "");

    navLinks.forEach(function (a) {
      if (a.classList.contains("nav-wa")) return;
      var href = a.getAttribute("href");
      if (!href || /^https?:/i.test(href)) return;
      var abs = new URL(href, location.origin + dir).pathname;
      if (normalize(abs) === here) {
        a.classList.add("active");
        a.setAttribute("aria-current", "page");
      }
    });
  })();

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
      activeFilter = btn.getAttribute("data-cat") || "all";
      applyFilters();
    });
  });
})();
