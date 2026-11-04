/* LookLearnFind global shell: progressive enhancement only. Every link in the rail, mobile bar and Explore sheet works without this script.
   Adds: state lens and recommendations on stories, state picker navigation, outline tracking, logo transition, Explore sheet and the "/" search shortcut.
   No tracking, no window globals. Markup comes from shared_nav.py. */
(function () {
  "use strict";
  var rail = document.getElementById("llf-rail");
  if (!rail) return;
  var KEY = "llf.stateLens";
  var ctx = rail.getAttribute("data-context");
  var def = rail.getAttribute("data-default-lens") || "ALL";
  var cache = null;

  function store(op, v) {
    try { return op === "get" ? sessionStorage.getItem(KEY) : sessionStorage.setItem(KEY, v); } catch (e) { return null; }
  }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }

  /* ---- state picker on non-story pages: choosing a state opens its hub */
  document.querySelectorAll("[data-state-nav-select]").forEach(function (s) {
    s.addEventListener("change", function () { if (s.value) window.location.assign(s.value); });
  });

  /* ---- state lens and recommendations (story pages only) */
  var selects = Array.prototype.slice.call(document.querySelectorAll("[data-state-select]"));
  if (ctx && selects.length) {
    var urlLens = function () {
      var p = new URLSearchParams(location.search).get("state");
      if (!p) return null;
      p = p.toUpperCase();
      return p === "ALL" || /^[A-Z]{2}$/.test(p) ? p : null; // validated again against the registry below
    };
    var valid = function (code) {
      return code && Array.prototype.some.call(selects[0].options, function (o) { return o.value === code; });
    };
    var resolve = function () {
      var u = urlLens();
      if (valid(u)) return u;
      var s = store("get");
      if (valid(s)) return s;
      return def;
    };
    var card = function (s) {
      var thread = s.slot === "Along this thread";
      var a = el("a", "rec " + (thread ? "thread-card" : "radar-card")); a.href = s.url; a.setAttribute("data-slot", s.slot);
      if (s.image) {
        var t = el("span", "thumb"), im = el("img"); im.src = s.image; im.alt = s.alt || ""; im.width = 300; im.height = 200; t.appendChild(im);
        if (s.ai) t.appendChild(el("span", "ai-tag", "AI illustration"));
        a.appendChild(t);
      }
      var b = el("span", "rec-body"); b.appendChild(el("span", "eyebrow", s.slot)); b.appendChild(el("span", "card-title", s.title)); b.appendChild(el("span", "rec-kind", s.kind + " · " + s.reason));
      a.appendChild(b); var ar = el("span", "arrow", "→"); ar.setAttribute("aria-hidden", "true"); a.appendChild(ar);
      return a;
    };
    var apply = function (res, announce) {
      document.querySelectorAll("[data-recs]").forEach(function (box) {
        box.textContent = "";
        if (!res.slots.length) box.appendChild(el("p", "gap", "No eligible suggestions here yet."));
        res.slots.forEach(function (s) { box.appendChild(card(s)); });
      });
      document.querySelectorAll("[data-state-form]").forEach(function (f) {
        var st = f.querySelector("[data-lens-status]"), link = f.querySelector("[data-coverage-link]");
        st.textContent = res.lens === "ALL" ? (announce ? res.status : "") : res.status;
        if (res.hub) { link.hidden = false; link.href = res.hub; link.textContent = "View " + res.lens_name + " coverage →"; }
        else { link.hidden = true; link.removeAttribute("href"); }
        var back = f.querySelector("[data-back-all]");
        if (res.gap && res.lens !== "ALL") {
          if (!back) { back = el("button", "coverage-link", "Back to all states"); back.type = "button"; back.setAttribute("data-back-all", ""); back.style.cssText = "background:none;border:0;padding:0;font:12px Arial,sans-serif;cursor:pointer"; f.appendChild(back); }
        } else if (back) back.remove();
      });
    };
    var load = function (cb) {
      if (cache) return cb(cache);
      fetch("/data/discovery/" + encodeURIComponent(ctx) + ".json").then(function (r) { return r.json(); }).then(function (d) { cache = d; cb(d); }).catch(function () { /* keep the server-rendered baseline */ });
    };
    var setLens = function (code, persist, announce) {
      selects.forEach(function (s) { s.value = code; });
      load(function (d) {
        var res = d.results[code] || d.results.ALL;
        apply(res, announce);
        if (persist) {
          store("set", code);
          var u = new URL(location.href); u.searchParams.set("state", code === "ALL" ? "all" : code);
          history.replaceState(null, "", u);
        }
      });
    };
    selects.forEach(function (s) { s.addEventListener("change", function () { setLens(s.value, true, true); }); });
    document.addEventListener("click", function (ev) {
      if (ev.target.closest && ev.target.closest("[data-back-all]")) { setLens("ALL", true, true); var s = selects[0]; if (s) s.focus(); }
    });
    var first = resolve();
    if (first !== def) setLens(first, false, false);
    window.addEventListener("popstate", function () { setLens(resolve(), false, true); });
  }

  /* ---- logo: sweep only on a genuine mode change between pages; never on hover or footnote opens */
  var brand = rail.querySelector(".brand");
  try {
    var prev = sessionStorage.getItem("llf.format"), now = document.body.getAttribute("data-format") || "";
    if (prev !== null && prev !== now && brand && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
      brand.classList.add("is-changing");
      setTimeout(function () { brand.classList.remove("is-changing"); }, 700);
    }
    sessionStorage.setItem("llf.format", now);
  } catch (e) { /* storage denied: no animation, no problem */ }

  /* ---- outline: highlight the section in view and name it in the summary */
  var outlines = document.querySelectorAll("[data-outline]");
  var links = Array.prototype.slice.call(document.querySelectorAll("[data-outline] a"));
  if (links.length) {
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    var per = links.length / (outlines.length || 1);
    var mark = function () {
      var y = window.scrollY + 140, cur = -1;
      targets.slice(0, per).forEach(function (t, i) { if (t && t.getBoundingClientRect().top + window.scrollY <= y) cur = i; });
      links.forEach(function (a, i) { if (i % per === cur) a.setAttribute("aria-current", "location"); else a.removeAttribute("aria-current"); });
      document.querySelectorAll("[data-outline-cur]").forEach(function (s) { s.textContent = cur >= 0 ? links[cur].textContent : ""; });
    };
    var ticking = false;
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { mark(); ticking = false; }); } }, { passive: true });
    mark();
    if (window.innerHeight >= 940 && matchMedia("(min-width:901px)").matches) rail.querySelectorAll("[data-outline]").forEach(function (o) { o.open = true; });
  }

  /* ---- Explore sheet (mobile) */
  var sheet = document.getElementById("explore-sheet"), opener = document.querySelector("[data-explore]");
  if (sheet && opener && typeof sheet.showModal === "function") {
    opener.addEventListener("click", function () { sheet.showModal(); });
    sheet.querySelector("[data-close-sheet]").addEventListener("click", function () { sheet.close(); });
    sheet.addEventListener("close", function () { opener.focus(); });
    sheet.addEventListener("click", function (ev) { if (ev.target === sheet) sheet.close(); });
    sheet.addEventListener("click", function (ev) { var a = ev.target.closest && ev.target.closest("a[href^='#']"); if (a) sheet.close(); });
  } else if (opener) { opener.hidden = true; }

  /* ---- "/" focuses global search unless the reader is typing in a field */
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "/" || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    var t = document.activeElement, tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable)) return;
    ev.preventDefault();
    var desktop = matchMedia("(min-width:901px)").matches;
    if (!desktop && sheet && !sheet.open && sheet.showModal) sheet.showModal();
    var input = document.getElementById(desktop ? "llf-site-search" : "llf-mobile-search");
    if (input) input.focus();
  });
})();
