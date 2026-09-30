/* /threads/<slug>/ for threads that editors approved in the database and that have no built page yet. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, host = document.getElementById('thread-app');
  if (!host) return;
  var slug = (location.pathname.match(/\/threads\/([a-z0-9-]+)/) || [])[1] || '';
  function card(i) {
    return '<a class="card" href="' + esc(i.url) + '"><div class="eyebrow">' + (i.t === 'find' ? 'Find' : 'Learn') + '</div><h3>' + esc(i.title) + '</h3><p>' + esc(i.dek) + '</p>' + (i.ill ? '<div class="kindline">Illustrative sample</div>' : '') + '</a>';
  }
  Promise.all([LLF.api('threads/get?slug=' + encodeURIComponent(slug)), fetch('/search-index.json').then(function (r) { return r.json(); }).catch(function () { return []; })]).then(function (r) {
    var t = r[0].thread, idx = r[1], cat = {politics: 'Politics', economy: 'Economy', society: 'Society', 'everyday-life': 'Everyday life'}[t.category] || 'Thread';
    document.title = t.title + ' — a thread | LookLearnFind';
    var stories = idx.filter(function (x) { return x.t === 'story' && x.threads.indexOf(t.slug) >= 0; }), finds = idx.filter(function (x) { return x.t === 'find' && x.threads.indexOf(t.slug) >= 0; });
    host.innerHTML = '<section class="page-head"><div class="wrap"><div class="breadcrumb"><a href="/">Home</a> / <a href="/threads/">Threads</a> / ' + esc(t.title) + '</div><div class="kicker">Thread / ' + esc(cat) + '<i></i></div><h1 class="display">' + esc(t.title) + '</h1>' + (t.summary ? '<p class="dek">' + esc(t.summary) + '</p>' : '') + (t.aliases.length ? '<p class="small" style="margin-top:14px">Also searched as: ' + esc(t.aliases.join(', ')) + '</p>' : '') + '</div></section>' +
      '<section class="shelf look" data-look-shelf data-thread="' + esc(t.slug) + '"><div class="wrap"><div class="shelf-head"><div><div class="lab">Look · Ledger</div><h2>What people are saving</h2></div><a class="link teal" href="/look/?thread=' + esc(t.slug) + '">Open in the Ledger ↗</a></div><p class="small" style="max-width:640px;margin:-8px 0 22px">Short videos kept by readers and editors. A save is a recommendation to look, not a verification.</p><div data-shelf-body></div></div></section>' +
      '<section class="shelf"><div class="wrap"><div class="shelf-head"><div><div class="lab">Learn · Reported</div><h2>What the record shows</h2></div></div>' + (stories.length ? '<div class="cards">' + stories.map(card).join('') + '</div>' : '<div class="empty"><b>We have not looked into ' + esc(t.title) + ' yet.</b> If you have an original source, a record, or a question worth chasing, <a href="/contribute/">send it to us</a>.</div>') + '</div></section>' +
      '<section class="shelf"><div class="wrap"><div class="shelf-head"><div><div class="lab">Find · Real world</div><h2>Where to try it</h2></div></div>' + (finds.length ? '<div class="cards">' + finds.map(card).join('') + '</div>' : '<div class="empty"><b>No real-world Finds for this yet.</b> Know a person, place, or guide that holds up? <a href="/contribute/">Tell us why</a>.</div>') + '</div></section>';
    LLF.initShelves && LLF.initShelves(host);
  }).catch(function () {
    host.innerHTML = '<section class="page-head"><div class="wrap"><div class="kicker">404<i></i></div><h1 class="display">Nothing on <em>that thread.</em></h1><p class="dek">Try the <a href="/threads/" style="color:var(--teal)">list of threads</a> or <a href="/search/" style="color:var(--teal)">search</a>.</p></div></section>';
  });
})();
