/* Politics landing: the state selector jumps to the chosen hub. Every state is also a plain link, so this is enhancement only. */
(function () {
  var f = document.querySelector("[data-pol-state-jump]");
  if (!f) return;
  f.addEventListener("submit", function (ev) { ev.preventDefault(); });
  f.querySelector("select").addEventListener("change", function (ev) { if (ev.target.value) window.location.href = ev.target.value; });
})();

/* Daily Signal: the sticky chapter bar marks the chapter in view. Links work without JavaScript. */
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll(".pol-chapters a[data-chapter]"));
  if (!links.length) return;
  var targets = links.map(function (a) { return document.getElementById(a.getAttribute("data-chapter")); });
  var mark = function () {
    var y = window.scrollY + 150, cur = -1;
    targets.forEach(function (t, i) { if (t && t.getBoundingClientRect().top + window.scrollY <= y) cur = i; });
    var end = document.getElementById("what-next");
    if (end && end.getBoundingClientRect().top + window.scrollY <= y) cur = -1;
    links.forEach(function (a, i) { if (i === cur) { a.setAttribute("aria-current", "location"); a.scrollIntoView({ block: "nearest", inline: "center" }); } else a.removeAttribute("aria-current"); });
  };
  var tick = false;
  window.addEventListener("scroll", function () { if (!tick) { tick = true; requestAnimationFrame(function () { mark(); tick = false; }); } }, { passive: true });
  mark();
})();
