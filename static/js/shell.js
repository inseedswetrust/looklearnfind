/* LookLearnFind global shell: progressive enhancement only. Every link in the rail and the mobile drawer works without this script
   (the drawer opens through :target when JavaScript is off). Adds: the slide-in drawer behavior on small screens (focus trap, scroll lock, Escape, backdrop and
   swipe-left to close, focus and scroll restoration), state picker navigation, outline tracking, the logo transition and the "/" search shortcut.
   On stories with current recommendations it also runs the state lens. No tracking, no window globals. Markup comes from shared_nav.py. */
(function () {
  "use strict";
  var rail = document.getElementById("llf-rail");
  if (!rail) return;
  var doc = document, body = doc.body;
  var trigger = doc.querySelector(".nav-open"), backdrop = doc.querySelector(".drawer-backdrop"), closeBtn = rail.querySelector(".drawer-close");
  var small = window.matchMedia("(max-width:900px)");
  var isOpen = false, lastFocus = null, savedY = 0;
  var KEY = "llf.stateLens";
  var ctx = rail.getAttribute("data-context");
  var def = rail.getAttribute("data-default-lens") || "ALL";
  var cache = null;

  function el(tag, cls, text) { var n = doc.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }
  function store(op, v) { try { return op === "get" ? sessionStorage.getItem(KEY) : sessionStorage.setItem(KEY, v); } catch (e) { return null; } }

  /* ---------------------------------------------------------------- drawer (small screens) */
  function background() { return doc.querySelectorAll("#main,.signup,.foot,.mast"); }
  function setBackgroundInert(on) {
    Array.prototype.forEach.call(background(), function (n) { if (on) n.setAttribute("inert", ""); else n.removeAttribute("inert"); });
  }
  function sync() {
    /* dialog semantics only while the rail is a drawer; on desktop it is a plain complementary landmark */
    if (small.matches) {
      rail.setAttribute("role", "dialog");
      rail.setAttribute("aria-modal", isOpen ? "true" : "false");
      if (isOpen) rail.removeAttribute("inert"); else rail.setAttribute("inert", "");
    } else {
      rail.removeAttribute("role"); rail.removeAttribute("aria-modal"); rail.removeAttribute("inert");
    }
  }
  function focusables() {
    return Array.prototype.filter.call(rail.querySelectorAll("a[href],button:not([disabled]),select,input,summary"), function (n) { return n.offsetParent !== null || n === doc.activeElement; });
  }
  /* the page may use smooth scrolling; restoring the reader's position must be exact and immediate */
  function jump(y) {
    var h = doc.documentElement, prev = h.style.scrollBehavior;
    h.style.scrollBehavior = "auto";
    window.scrollTo(0, y);
    h.style.scrollBehavior = prev;
  }
  function openDrawer() {
    if (!small.matches || isOpen || !trigger) return;
    isOpen = true;
    lastFocus = doc.activeElement && doc.activeElement !== body ? doc.activeElement : trigger;
    savedY = window.pageYOffset || doc.documentElement.scrollTop || 0;
    body.style.top = (-savedY) + "px";
    body.classList.add("drawer-open");
    rail.classList.add("is-open");
    trigger.setAttribute("aria-expanded", "true");
    setBackgroundInert(true);
    sync();
    (closeBtn || focusables()[0]).focus({ preventScroll: true });
  }
  function closeDrawer(restoreFocus) {
    if (!isOpen) return;
    isOpen = false;
    rail.classList.remove("is-open");
    body.classList.remove("drawer-open");
    body.style.top = "";
    jump(savedY);
    trigger.setAttribute("aria-expanded", "false");
    setBackgroundInert(false);
    sync();
    if (restoreFocus !== false) (lastFocus && doc.contains(lastFocus) ? lastFocus : trigger).focus({ preventScroll: true });
  }
  if (trigger) {
    if (location.hash === "#llf-rail") history.replaceState(null, "", location.pathname + location.search);    /* a no-JS open state must not linger */
    trigger.addEventListener("click", function (ev) { ev.preventDefault(); if (isOpen) closeDrawer(); else openDrawer(); });
    if (closeBtn) closeBtn.addEventListener("click", function (ev) { ev.preventDefault(); closeDrawer(); });
    if (backdrop) backdrop.addEventListener("click", function (ev) { ev.preventDefault(); closeDrawer(); });
    /* in-page links in the drawer (outline, source link): close first, then go to the section */
    rail.addEventListener("click", function (ev) {
      var a = ev.target.closest && ev.target.closest("a[href^='#']");
      if (!a || a === closeBtn || !isOpen) return;
      var id = a.getAttribute("href").slice(1), target = id && doc.getElementById(id);
      ev.preventDefault();
      closeDrawer(false);
      if (target) { requestAnimationFrame(function () { var h = doc.documentElement, prev = h.style.scrollBehavior; h.style.scrollBehavior = "auto"; target.scrollIntoView(); h.style.scrollBehavior = prev; history.replaceState(null, "", "#" + id); }); }
    });
    doc.addEventListener("keydown", function (ev) {
      if (!isOpen) return;
      if (ev.key === "Escape") { ev.preventDefault(); closeDrawer(); return; }
      if (ev.key === "Tab") {                                   /* keep focus inside the drawer */
        var f = focusables(); if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (ev.shiftKey && (doc.activeElement === first || !rail.contains(doc.activeElement))) { ev.preventDefault(); last.focus(); }
        else if (!ev.shiftKey && (doc.activeElement === last || !rail.contains(doc.activeElement))) { ev.preventDefault(); first.focus(); }
      }
    });
    /* swipe left inside the drawer closes it; a normal horizontal gesture elsewhere never opens it */
    var sx = 0, sy = 0, st = 0;
    rail.addEventListener("touchstart", function (ev) { var t = ev.changedTouches[0]; sx = t.clientX; sy = t.clientY; st = Date.now(); }, { passive: true });
    rail.addEventListener("touchend", function (ev) {
      if (!isOpen) return;
      var t = ev.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
      if (dx < -60 && Math.abs(dy) < Math.abs(dx) * 0.6 && Date.now() - st < 700) closeDrawer();
    }, { passive: true });
    var onChange = function () { if (!small.matches && isOpen) closeDrawer(false); sync(); };
    if (small.addEventListener) small.addEventListener("change", onChange); else small.addListener(onChange);
  }
  sync();

  /* ---------------------------------------------------------------- state picker (navigates to the hub) */
  doc.querySelectorAll("[data-state-nav-select]").forEach(function (s) {
    s.addEventListener("change", function () { if (s.value) window.location.assign(s.value); });
  });

  /* ---------------------------------------------------------------- state lens and recommendations (only when current recommendations exist) */
  var selects = Array.prototype.slice.call(doc.querySelectorAll("[data-state-select]"));
  if (ctx && selects.length) {
    var urlLens = function () {
      var p = new URLSearchParams(location.search).get("state");
      if (!p) return null;
      p = p.toUpperCase();
      return p === "ALL" || /^[A-Z]{2}$/.test(p) ? p : null;
    };
    var valid = function (code) { return code && Array.prototype.some.call(selects[0].options, function (o) { return o.value === code; }); };
    var resolve = function () { var u = urlLens(); if (valid(u)) return u; var s = store("get"); if (valid(s)) return s; return def; };
    var card = function (s) {
      var thread = s.slot === "Along this thread";
      var a = el("a", "rec " + (thread ? "thread-card" : "radar-card")); a.href = s.url; a.setAttribute("data-slot", s.slot);
      if (s.image) {
        var t = el("span", "thumb"), im = el("img"); im.src = s.image; im.alt = s.alt || ""; im.width = 300; im.height = 200; t.appendChild(im);
        a.appendChild(t);
      }
      var b = el("span", "rec-body"); b.appendChild(el("span", "eyebrow", s.slot)); b.appendChild(el("span", "card-title", s.title)); b.appendChild(el("span", "rec-kind", s.kind + " · " + s.reason));
      a.appendChild(b); var ar = el("span", "arrow", "→"); ar.setAttribute("aria-hidden", "true"); a.appendChild(ar);
      return a;
    };
    var apply = function (res, announce) {
      doc.querySelectorAll("[data-recs]").forEach(function (box) {
        box.textContent = "";
        if (!res.slots.length) box.appendChild(el("p", "gap", "No eligible suggestions here yet."));
        res.slots.forEach(function (s) { box.appendChild(card(s)); });
      });
      doc.querySelectorAll("[data-state-form]").forEach(function (f) {
        var st = f.querySelector("[data-lens-status]"), link = f.querySelector("[data-coverage-link]");
        st.textContent = res.lens === "ALL" ? (announce ? res.status : "") : res.status;
        if (res.hub) { link.hidden = false; link.href = res.hub; link.textContent = "View " + res.lens_name + " coverage →"; }
        else { link.hidden = true; link.removeAttribute("href"); }
      });
    };
    var load = function (cb) {
      if (cache) return cb(cache);
      fetch("/data/discovery/" + encodeURIComponent(ctx) + ".json").then(function (r) { return r.json(); }).then(function (d) { cache = d; cb(d); }).catch(function () { });
    };
    var setLens = function (code, persist, announce) {
      selects.forEach(function (s) { s.value = code; });
      load(function (d) {
        apply(d.results[code] || d.results.ALL, announce);
        if (persist) { store("set", code); var u = new URL(location.href); u.searchParams.set("state", code === "ALL" ? "all" : code); history.replaceState(null, "", u); }
      });
    };
    selects.forEach(function (s) { s.addEventListener("change", function () { setLens(s.value, true, true); }); });
    var first = resolve();
    if (first !== def) setLens(first, false, false);
    window.addEventListener("popstate", function () { setLens(resolve(), false, true); });
  }

  /* ---------------------------------------------------------------- logo: sweep only on a genuine mode change between pages */
  var brand = rail.querySelector(".brand");
  try {
    var prev = sessionStorage.getItem("llf.format"), now = body.getAttribute("data-format") || "";
    if (prev !== null && prev !== now && brand && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
      brand.classList.add("is-changing");
      setTimeout(function () { brand.classList.remove("is-changing"); }, 700);
    }
    sessionStorage.setItem("llf.format", now);
  } catch (e) { /* storage denied: no animation, no problem */ }

  /* ---------------------------------------------------------------- outline: highlight the section in view and name it in the summary */
  var outlines = doc.querySelectorAll("[data-outline]");
  var links = Array.prototype.slice.call(doc.querySelectorAll("[data-outline] a"));
  if (links.length) {
    var targets = links.map(function (a) { return doc.getElementById(a.getAttribute("href").slice(1)); });
    var per = links.length / (outlines.length || 1);
    var mark = function () {
      var y = window.scrollY + 140, cur = -1;
      if (isOpen) return;                                           /* the page is scroll-locked while the drawer is open */
      targets.slice(0, per).forEach(function (t, i) { if (t && t.getBoundingClientRect().top + window.scrollY <= y) cur = i; });
      links.forEach(function (a, i) { if (i % per === cur) a.setAttribute("aria-current", "location"); else a.removeAttribute("aria-current"); });
      doc.querySelectorAll("[data-outline-cur]").forEach(function (s) { s.textContent = cur >= 0 ? links[cur].textContent : ""; });
    };
    var ticking = false;
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { mark(); ticking = false; }); } }, { passive: true });
    mark();
  }

  /* ---------------------------------------------------------------- "/" focuses global search unless the reader is typing in a field */
  doc.addEventListener("keydown", function (ev) {
    if (ev.key !== "/" || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    var t = doc.activeElement, tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (t && t.isContentEditable)) return;
    ev.preventDefault();
    if (small.matches) openDrawer();
    var input = doc.getElementById("llf-site-search");
    if (input) input.focus();
  });
})();
