/* /search/ — one query across stories, Finds, threads, topics, pages and (when available) saved videos. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, form = document.querySelector('[data-search-form]');
  if (!form) return;
  var tabsEl = document.querySelector('[data-search-tabs]'), out = document.querySelector('[data-search-results]'), input = form.q;
  var index = [], ledger = {items: [], total: 0}, tab = 'all', thr = [];
  var LABEL = {story: 'Story', find: 'Find', thread: 'Thread', topic: 'Topic', page: 'Page', look: 'Ledger'};

  function score(it, terms, full) {
    var title = it.title.toLowerCase(), dek = (it.dek || '').toLowerCase(), txt = ((it.text || '') + ' ' + (it.threads || []).join(' ')).toLowerCase(), s = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i], hit = false;
      if (title.indexOf(t) >= 0) { s += 10; hit = true; }
      if (dek.indexOf(t) >= 0) { s += 4; hit = true; }
      if (txt.indexOf(t) >= 0) { s += 2; hit = true; }
      if (!hit) return 0;
    }
    if (title.indexOf(full) >= 0) s += 6;
    return s;
  }
  function run() {
    var q = input.value.trim(), terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    history.replaceState(null, '', location.pathname + (q ? '?q=' + encodeURIComponent(q) : ''));
    if (!q) { tabsEl.innerHTML = ''; out.innerHTML = '<div class="empty" style="border:1px dashed var(--rule2);padding:24px;font:14px var(--sans);color:var(--muted)">Start with a question. Or browse the <a href="/threads/">threads</a> and <a href="/topics/">topics</a>.</div>'; return; }
    var hits = index.map(function (it) { return {it: it, s: score(it, terms, q.toLowerCase())}; }).filter(function (x) { return x.s > 0; });
    // a query that matches a thread alias (e.g. "mud flood") surfaces that thread's stories too
    thr.forEach(function (t) {
      var names = [t.title].concat(t.aliases).map(function (x) { return x.toLowerCase(); });
      if (names.some(function (n) { return n.indexOf(q.toLowerCase()) >= 0 || q.toLowerCase().indexOf(n) >= 0; })) {
        index.forEach(function (it) { if ((it.threads || []).indexOf(t.slug) >= 0 && !hits.some(function (h) { return h.it === it; })) hits.push({it: it, s: 5}); });
        var th = index.filter(function (it) { return it.t === 'thread' && it.url === '/threads/' + t.slug + '/'; })[0];
        if (th && !hits.some(function (h) { return h.it === th; })) hits.push({it: th, s: 12});
      }
    });
    hits.sort(function (a, b) { return b.s - a.s; });
    var counts = {all: hits.length + ledger.total, story: 0, find: 0, thread: 0, topic: 0, look: ledger.total};
    hits.forEach(function (h) { if (counts[h.it.t] !== undefined) counts[h.it.t]++; });
    tabsEl.innerHTML = [['all', 'All'], ['story', 'Stories'], ['find', 'Finds'], ['look', 'Ledger'], ['thread', 'Threads'], ['topic', 'Topics']].map(function (t) { return '<button role="tab" data-tab="' + t[0] + '" aria-selected="' + (tab === t[0]) + '">' + t[1] + ' (' + counts[t[0]] + ')</button>'; }).join('');
    var rows = hits.filter(function (h) { return tab === 'all' || h.it.t === tab; }).map(function (h) {
      var it = h.it;
      return '<a class="result" href="' + esc(it.url) + '"><div class="ty">' + LABEL[it.t] + (it.ill ? ' · sample' : '') + '</div><div><h3>' + esc(it.title) + '</h3><p>' + esc(it.dek) + '</p></div></a>';
    });
    if (tab === 'all' || tab === 'look') rows = rows.concat(ledger.items.map(function (i) {
      return '<a class="result" href="' + (i.video.ledger_no ? '/look/L-' + String(i.video.ledger_no).padStart(3, '0') + '/' : '/look/') + '"><div class="ty">Ledger · ' + esc(i.video.ledger || '') + '</div><div><h3>' + esc(i.video.title || 'Saved video') + '</h3><p>“' + esc(i.save.note) + '” · ' + esc(i.save.label) + ' · saved by ' + esc(i.save.saver.display_name) + (i.video.illustrative ? ' · illustrative sample' : '') + '</p></div></a>';
    }));
    out.innerHTML = rows.length ? rows.join('') : '<div class="empty" style="border:1px dashed var(--rule2);padding:24px;font:14px var(--sans);color:var(--muted)"><b style="color:var(--ink)">Nothing on that thread yet.</b> Try a broader question, or <a href="/contribute/">send us a source</a>.</div>';
    if (ledger.total > ledger.items.length && (tab === 'all' || tab === 'look')) out.insertAdjacentHTML('beforeend', '<p style="margin-top:16px"><a class="link teal" href="/look/?q=' + encodeURIComponent(q) + '">See all ' + ledger.total + ' Ledger results ↗</a></p>');
  }
  var t0 = null;
  function go() {
    var q = input.value.trim();
    if (q.length >= 2) LLF.api('ledger/list?facets=0&limit=5&q=' + encodeURIComponent(q)).then(function (j) { ledger = j; run(); }).catch(function () { ledger = {items: [], total: 0}; });
    else ledger = {items: [], total: 0};
    run();
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); go(); });
  input.addEventListener('input', function () { clearTimeout(t0); t0 = setTimeout(go, 250); });
  tabsEl.addEventListener('click', function (e) { var b = e.target.closest('[data-tab]'); if (b) { tab = b.dataset.tab; run(); } });
  Promise.all([fetch('/search-index.json').then(function (r) { return r.json(); }), fetch('/threads.json').then(function (r) { return r.json(); }).catch(function () { return []; })]).then(function (r) {
    index = r[0]; thr = r[1]; var q = LLF.params().get('q'); if (q) { input.value = q; } go();
  });
})();
