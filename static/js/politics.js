/* Politics landing: the state selector jumps to the chosen hub. Every state is also a plain link, so this is enhancement only. */
(function () {
  var f = document.querySelector("[data-pol-state-jump]");
  if (!f) return;
  f.addEventListener("submit", function (ev) { ev.preventDefault(); });
  f.querySelector("select").addEventListener("change", function (ev) { if (ev.target.value) window.location.href = ev.target.value; });
})();
