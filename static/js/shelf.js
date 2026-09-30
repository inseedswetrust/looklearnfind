/* Look shelves on thread, topic, category, story and home pages. Filled from the live Ledger; honest when empty or offline. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc;
  LLF.initShelves = function (root) {
  var shelves = LLF.qsa('[data-look-shelf]', root);
  if (!shelves.length || !LLF.entryRow) { return; }
  shelves.forEach(function (sh) {
    if (sh.dataset.ready) return; sh.dataset.ready = '1';
    var body = sh.querySelector('[data-shelf-body]') || sh;
    var p = new URLSearchParams();
    ['thread', 'topic', 'category', 'sort', 'limit'].forEach(function (k) { if (sh.dataset[k]) p.set(k, sh.dataset[k]); });
    if (!p.get('limit')) p.set('limit', '4'); p.set('facets', '0');
    var items = [];
    LLF.api('ledger/list?' + p.toString()).then(function (j) {
      items = j.items;
      if (!j.items.length) {
        body.innerHTML = '<div class="empty"><b>No saved videos on this yet.</b> Seen a short video that belongs here? <a href="/look/add/">Add it to the Ledger</a>. A save is a recommendation to look, not a verification.</div>';
        return;
      }
      body.innerHTML = '<div class="shelf-rows">' + j.items.map(LLF.miniRow).join('') + '</div>' +
        (j.total > j.items.length ? '<p style="margin-top:14px"><a class="link teal" href="/look/?' + p.toString().replace(/&?(facets|limit)=[^&]*/g, '') + '">See all ' + j.total + ' in the Ledger ↗</a></p>' : '');
    }).catch(function () {
      body.innerHTML = '<div class="empty"><b>The Ledger opens soon.</b> Short videos kept by readers and editors will appear here.</div>';
    });
    LLF.bindRows(sh, {find: function (v, s) { return items.filter(function (x) { return x.video.id === v && x.save.id === s; })[0]; }, reload: function () { location.reload(); }});
  });
  };
  LLF.initShelves(document);
})();
