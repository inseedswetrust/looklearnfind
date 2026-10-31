/* /find/candidates/: filter the directory table in place. Without JavaScript the full table shows and the form stays hidden. */
(function () {
  'use strict';
  var form = document.querySelector('[data-cand-filter]');
  if (!form) return;
  var rows = [].slice.call(document.querySelectorAll('[data-cand-row]'));
  var count = document.querySelector('[data-cand-count]');
  function run() {
    var st = form.state ? form.state.value : '', off = form.office.value, pa = form.party.value, q = form.q.value.trim().toLowerCase();
    var n = 0;
    rows.forEach(function (r) {
      var ok = (!st || r.dataset.state === st) && (!off || r.dataset.office === off) && (!pa || r.dataset.party === pa) && (!q || r.dataset.name.indexOf(q) >= 0);
      r.hidden = !ok;
      if (ok) n++;
    });
    if (count) count.textContent = n + ' of ' + rows.length + ' candidates shown';
  }
  form.addEventListener('input', run);
  form.addEventListener('change', run);
  form.addEventListener('submit', function (e) { e.preventDefault(); run(); });
  run();
})();
