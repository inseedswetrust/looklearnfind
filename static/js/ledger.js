/* /look/ — Explore, Following, My Ledger. Filters live in the URL so any view can be shared. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, app = document.getElementById('ledger-app');
  if (!app) return;
  var FKEYS = ['q', 'category', 'topic', 'kind', 'length', 'platform', 'lang', 'by', 'thread', 'since', 'deep', 'find', 'collection'];
  var st = {mode: 'explore', f: {}, sort: 'added', view: 'table', offset: 0, items: [], total: 0, facets: null, sd: null, desk: null, loading: false};
  var PAGE = 20;

  function readUrl() {
    var p = LLF.params();
    st.mode = ['explore', 'following', 'mine'].indexOf(p.get('mode')) >= 0 ? p.get('mode') : 'explore';
    st.f = {}; FKEYS.forEach(function (k) { if (p.get(k)) st.f[k] = p.get(k); });
    st.sort = p.get('sort') === 'posted' ? 'posted' : 'added';
    st.view = p.get('view') === 'compact' ? 'compact' : 'table';
  }
  function writeUrl() {
    var p = new URLSearchParams();
    if (st.mode !== 'explore') p.set('mode', st.mode);
    Object.keys(st.f).forEach(function (k) { p.set(k, st.f[k]); });
    if (st.sort !== 'added') p.set('sort', st.sort);
    if (st.view !== 'table') p.set('view', st.view);
    var s = p.toString(); history.replaceState(null, '', location.pathname + (s ? '?' + s : ''));
  }
  function qstr(extra) {
    var p = new URLSearchParams();
    Object.keys(st.f).forEach(function (k) { p.set(k, st.f[k]); });
    p.set('sort', st.sort); p.set('mode', st.mode);
    Object.keys(extra || {}).forEach(function (k) { p.set(k, extra[k]); });
    return p.toString();
  }

  function shell() {
    app.innerHTML =
      '<section class="controls"><div class="wrap wide"><nav class="tabs" role="tablist" aria-label="Ledger views">' +
      ['explore', 'following', 'mine'].map(function (m) { return '<button role="tab" data-mode="' + m + '" aria-selected="' + (st.mode === m) + '">' + ({explore: 'Explore', following: 'Following', mine: 'My Ledger'})[m] + '</button>'; }).join('') + '</nav>' +
      '<div class="controls-main"><form class="qwrap" data-qf role="search"><label class="sr" for="lq">What are you looking into?</label><input id="lq" type="search" placeholder="What are you looking into?" value="' + esc(st.f.q || '') + '" autocomplete="off"><button type="submit" aria-label="Search">⌕</button></form>' +
      '<select class="cselect desk-only" data-sel="category" aria-label="Subject"></select><select class="cselect desk-only" data-sel="kind" aria-label="Kind of post"></select>' +
      '<button class="cselect" data-more-filters type="button">More filters<span data-fcount></span></button>' +
      '<a class="add-btn" href="/look/add/">+ Add a post</a></div>' +
      '<div class="filterline" data-line></div></div></section>' +
      '<div data-desk></div><section class="ledger"><div class="wrap wide"><div class="ledger-title"><div><span class="eyebrow" data-eyebrow></span><h2>Worth the scroll.</h2></div>' +
      '<div class="right"><label class="sr" for="viewsel">View</label><select class="viewsel" id="viewsel"><option value="table">View: detailed table</option><option value="compact">View: compact list</option></select>' +
      '<button class="shuffle" data-shuffle type="button">Shuffle this shelf ↝</button></div></div>' +
      '<div data-shuffled></div><div class="table-head"><span>Preview</span><span>The clip &amp; why it stayed</span><span>Filed under</span><span>People behind it</span><span>Open / save</span></div>' +
      '<div data-rows></div><div class="end" data-end></div><div data-peek></div></div></section>' +
      '<div class="drawer" data-drawer><div class="scrim" data-close></div><div class="panel" role="dialog" aria-label="More filters"></div></div>';
    LLF.qs('#viewsel').value = st.view;
  }

  function opt(v, l, sel) { return '<option value="' + esc(v) + '"' + (sel ? ' selected' : '') + '>' + esc(l) + '</option>'; }
  function facetOpts(list, cur, labelFn, allLabel) {
    var has = {}; (list || []).forEach(function (x) { has[x.value] = x.n; });
    var out = opt('', allLabel, !cur);
    if (cur && !has[cur]) out += opt(cur, labelFn(cur), true);
    (list || []).forEach(function (x) { out += opt(x.value, labelFn(x.value, x) + ' (' + x.n + ')', cur === x.value); });
    return out;
  }
  function topicLabel(v) { var t = (st.sd.topics || []).filter(function (x) { return x.slug === v; })[0]; return t ? t.label : v; }
  function platLabel(v) { return LLF.platformLabels[v] || v; }

  function drawControls() {
    var F = st.facets || {};
    LLF.qs('[data-sel="category"]').innerHTML = facetOpts(F.category, st.f.category, LLF.catLabel, 'Subject');
    LLF.qs('[data-sel="kind"]').innerHTML = facetOpts(F.kind, st.f.kind, function (v) { return v; }, 'Kind of post');
    ['category', 'kind'].forEach(function (k) { LLF.qs('[data-sel="' + k + '"]').classList.toggle('on', !!st.f[k]); });
    var n = ['topic', 'length', 'platform', 'lang', 'by', 'thread', 'since', 'deep', 'find', 'collection'].filter(function (k) { return st.f[k]; }).length;
    LLF.qs('[data-fcount]').textContent = n ? ' (' + n + ')' : '';
    var line = '', lab = {q: function (v) { return '“' + v + '”'; }, category: LLF.catLabel, topic: topicLabel, kind: function (v) { return v; }, length: function (v) { return LLF.lengthLabels[v] || v; }, platform: platLabel, lang: function (v) { return v.toUpperCase(); }, by: function (v) { return 'Added by @' + v; }, thread: function (v) { return 'Thread: ' + v; }, since: function (v) { return 'Since ' + v; }, deep: function () { return 'Has a deep dive'; }, find: function () { return 'Has a real-world Find'; }, collection: function () { return 'Collection'; }};
    Object.keys(st.f).forEach(function (k) { line += '<button class="facet" data-rm="' + k + '" aria-label="Remove filter">' + esc(lab[k] ? lab[k](st.f[k]) : st.f[k]) + ' ×</button>'; });
    if (Object.keys(st.f).length > 1) line += '<button class="clear" data-clear>Clear all</button>';
    line += '<span class="count" aria-live="polite">' + (st.loading ? 'Loading…' : st.total + ' clip' + (st.total === 1 ? '' : 's') + ' in this view') + '</span>' +
      '<label class="sr" for="sortsel">Order by</label><select class="sortsel" id="sortsel"><option value="added"' + (st.sort === 'added' ? ' selected' : '') + '>Order by: Recently added</option><option value="posted"' + (st.sort === 'posted' ? ' selected' : '') + '>Order by: Original post date</option></select>';
    LLF.qs('[data-line]').innerHTML = line;
  }

  function drawDesk() {
    var box = LLF.qs('[data-desk]');
    var active = Object.keys(st.f).length > 0;
    if (st.mode !== 'explore' || active || !st.desk || !st.desk.items.length) { box.innerHTML = ''; return; }
    var d = st.desk;
    box.innerHTML = '<section class="desk"><div class="wrap wide"><div class="desk-top"><span class="eyebrow">From the desk &nbsp;•&nbsp; ' + esc(d.title) + '</span><span class="desc">' + esc(d.note || 'A few links we keep coming back to, and why.') + ' Curated by ' + esc(d.curator) + '.</span></div>' + d.items.slice(0, 1).map(LLF.featured).join('') + '</div></section>';
  }

  function find(vid, sid) {
    var all = st.items.concat(st.desk ? st.desk.items : []).concat(st.shuffled ? [st.shuffled] : []);
    for (var i = 0; i < all.length; i++) if (all[i].video.id === vid && all[i].save.id === sid) return all[i];
    return null;
  }

  function emptyState() {
    var m = st.mode, filtered = Object.keys(st.f).length > 0;
    if (m === 'following') {
      return '<div class="empty-state">Your Following shelf is quiet. Find someone whose eye you trust, then their public saves will appear here in time order.<div class="btns"><a class="btn" href="/look/">Explore the Ledger</a></div></div>';
    }
    if (m === 'mine') {
      return '<div class="empty-state">' + (filtered ? 'Nothing in your Ledger matches this slice.' : 'Nothing saved yet. Hit <b>Save +</b> on any clip, or paste a link of your own.') + '<div class="btns"><a class="btn" href="/look/add/">+ Add a post</a></div></div>';
    }
    return '<div class="empty-state">Nothing in this slice yet. Remove a filter, try a broader question, or add a link we missed.<div class="btns">' + (filtered ? '<button class="btn ghost" data-clear>Clear filters</button>' : '') + '<a class="btn" href="/look/add/">+ Add a post</a></div></div>';
  }

  function drawRows(append) {
    var rows = LLF.qs('[data-rows]');
    var html = st.items.slice(append ? st.offset - PAGE : 0).map(function (it) { return LLF.entryRow(it, {mode: st.mode}); }).join('');
    if (append) rows.insertAdjacentHTML('beforeend', html); else rows.innerHTML = html || emptyState();
    rows.className = st.view === 'compact' ? 'compact' : '';
    var end = LLF.qs('[data-end]');
    if (!st.items.length) end.innerHTML = '';
    else end.innerHTML = '<span>Showing ' + st.items.length + ' of ' + st.total + ' clips in this view. The order is yours' + (st.sort === 'added' ? ': recently added.' : ': original post date, when known.') + '</span>' + (st.items.length < st.total ? '<button class="more" data-more>More entries ↓</button>' : '');
    LLF.qs('[data-eyebrow]').textContent = ({explore: 'The public index', following: 'Public saves from people you follow', mine: 'Your Ledger'})[st.mode] + ' / ' + String(st.total).padStart(3, '0') + ' entries';
  }

  function drawPeek() {
    var box = LLF.qs('[data-peek]');
    if (st.mode !== 'explore' || Object.keys(st.f).length) { box.innerHTML = ''; return; }
    LLF.api('ledger/suggest').then(function (j) {
      var ps = j.profiles.filter(function (p) { return !LLF.user || p.handle !== LLF.user.handle; }).slice(0, 3);
      if (!ps.length) return;
      box.innerHTML = '<div class="peek"><span class="eyebrow" style="color:var(--green)">Whose eye</span><h3>People worth following.</h3><div class="peek-grid">' + ps.map(function (p) {
        var ints = p.interests.slice(0, 3).map(topicLabel).join(', ');
        return '<div class="peek-card"><h4>' + esc(p.display_name) + '’s Ledger</h4><p>' + esc(p.looks_for || 'Saves worth a second look.') + '</p><p>' + (ints ? 'Interested in ' + esc(ints) + '. ' : '') + p.public_saves + ' public save' + (p.public_saves === 1 ? '' : 's') + '.</p><a class="link teal" href="/u/' + esc(p.handle) + '/">See their public Ledger ↗</a></div>';
      }).join('') + '</div></div>';
    }).catch(function () {});
  }

  function load(append) {
    if (st.mode !== 'explore' && !LLF.user) { signedOut(); return; }
    st.loading = true; drawControls();
    var off = append ? st.items.length : 0;
    LLF.api('ledger/list?' + qstr({limit: PAGE, offset: off})).then(function (j) {
      st.loading = false; st.total = j.total; st.facets = j.facets || st.facets;
      st.offset = off + PAGE;
      st.items = append ? st.items.concat(j.items) : j.items;
      writeUrl(); drawControls(); drawDesk(); drawRows(append); drawPeek();
    }).catch(function (er) {
      st.loading = false;
      if (er.status === 401) { signedOut(); return; }
      LLF.qs('[data-rows]').innerHTML = '<div class="empty-state">' + esc(er.message) + ' The Ledger needs its server to be running; everything else on the site works without it.</div>';
      LLF.qs('[data-end]').innerHTML = ''; drawControls();
    });
  }
  function signedOut() {
    st.loading = false; st.items = []; st.total = 0; drawControls(); drawDesk();
    LLF.qs('[data-rows]').innerHTML = '<div class="empty-state">' + (st.mode === 'following' ? 'Follow people whose eye you trust, and their newest public saves appear here in time order.' : 'Keep your own Ledger: save links privately, add notes, and choose what to make public.') + ' Sign in or create a profile to begin.<div class="btns"><button class="btn" data-signin>Create a profile</button><button class="btn ghost" data-signin="in">Sign in</button></div></div>';
    LLF.qs('[data-end]').innerHTML = '';
  }

  function drawer() {
    var F = st.facets || {}, d = LLF.qs('[data-drawer]'), p = d.querySelector('.panel');
    function sel(k, label, list, lf) { return '<div class="field"><label for="d-' + k + '">' + label + '</label><select class="select" id="d-' + k + '" data-f="' + k + '">' + facetOpts(list, st.f[k], lf, 'Any') + '</select></div>'; }
    p.innerHTML = '<h2>More filters</h2><p class="small" style="margin-bottom:16px">Only options that exist in the current results are listed. <span data-dcount></span></p>' +
      sel('category', 'Subject', F.category, LLF.catLabel) + sel('kind', 'Kind of post', F.kind, function (v) { return v; }) + sel('topic', 'Topic', F.topic, topicLabel) + sel('length', 'Length', F.length, function (v) { return LLF.lengthLabels[v] || v; }) + sel('platform', 'Platform', F.platform, platLabel) +
      sel('lang', 'Language', F.lang, function (v) { return v.toUpperCase(); }) + sel('by', 'Added by', F.by, function (v, x) { return x && x.label ? x.label : '@' + v; }) +
      '<div class="field"><label for="d-since">Added since</label><input class="input" type="date" id="d-since" data-f="since" value="' + esc(st.f.since || '') + '"></div>' +
      '<div class="field"><label for="d-thread">Thread</label><input class="input" id="d-thread" data-f="thread" placeholder="e.g. tartaria" value="' + esc(st.f.thread || '') + '"></div>' +
      '<div class="field checks"><label><input type="checkbox" data-f="deep" ' + (st.f.deep ? 'checked' : '') + '> Has a deep dive attached</label><label><input type="checkbox" data-f="find" ' + (st.f.find ? 'checked' : '') + '> Has a real-world Find</label></div>' +
      '<div class="done"><button class="btn" data-apply>Show results</button><button class="btn ghost" data-close>Close</button></div>';
    d.classList.add('open');
  }

  function setF(k, v) { if (v === '' || v == null || v === false) delete st.f[k]; else st.f[k] = v === true ? '1' : v; }

  function shuffle() {
    LLF.api('ledger/shuffle?' + qstr()).then(function (j) {
      var box = LLF.qs('[data-shuffled]');
      if (!j.item) { box.innerHTML = '<div class="empty-state">Nothing to shuffle in this slice. Remove a filter and try again.</div>'; return; }
      st.shuffled = j.item;
      box.innerHTML = '<div class="shuffle-result"><div class="cap"><div>Shuffled<span> · One random entry from the ' + j.total + ' clip' + (j.total === 1 ? '' : 's') + ' in your current filters.</span></div><div><button class="shuffle" data-shuffle type="button">Shuffle again ↝</button> <button class="clear" data-hide-shuffle>Dismiss</button></div></div>' + LLF.entryRow(j.item, {mode: 'explore'}) + '</div>';
    }).catch(function (er) { LLF.toast(er.message); });
  }

  // ---- events
  app.addEventListener('click', function (e) {
    var t = e.target;
    var m = t.closest('[data-mode]'); if (m) { st.mode = m.dataset.mode; st.f = {}; st.offset = 0; LLF.qsa('[data-mode]').forEach(function (x) { x.setAttribute('aria-selected', x === m); }); load(false); return; }
    var rm = t.closest('[data-rm]'); if (rm) { setF(rm.dataset.rm, ''); load(false); return; }
    if (t.closest('[data-clear]')) { st.f = {}; var qi = LLF.qs('#lq'); if (qi) qi.value = ''; load(false); return; }
    if (t.closest('[data-more]')) { load(true); return; }
    if (t.closest('[data-shuffle]')) { shuffle(); return; }
    if (t.closest('[data-hide-shuffle]')) { LLF.qs('[data-shuffled]').innerHTML = ''; return; }
    if (t.closest('[data-more-filters]')) { drawer(); return; }
    if (t.closest('[data-close]')) { LLF.qs('[data-drawer]').classList.remove('open'); return; }
    if (t.closest('[data-apply]')) {
      LLF.qsa('[data-drawer] [data-f]').forEach(function (el) { setF(el.dataset.f, el.type === 'checkbox' ? el.checked : el.value.trim()); });
      LLF.qs('[data-drawer]').classList.remove('open'); load(false); return;
    }
    var si = t.closest('[data-signin]'); if (si) { LLF.authModal(null, function () { LLF.me(true).then(function () { load(false); }); }); return; }
  });
  app.addEventListener('change', function (e) {
    var t = e.target;
    if (t.dataset.sel) { setF(t.dataset.sel, t.value); load(false); }
    else if (t.id === 'sortsel') { st.sort = t.value; load(false); }
    else if (t.id === 'viewsel') { st.view = t.value; writeUrl(); drawRows(false); }
  });
  app.addEventListener('submit', function (e) {
    if (e.target.hasAttribute('data-qf')) { e.preventDefault(); setF('q', LLF.qs('#lq').value.trim()); load(false); }
  });
  LLF.bindRows(app, {find: find, reload: function () { load(false); }});

  // ---- boot
  readUrl();
  LLF.siteData().then(function (sd) {
    st.sd = sd;
    return LLF.me();
  }).then(function () {
    shell(); drawControls();
    LLF.api('ledger/desk').then(function (j) { st.desk = j.desk; drawDesk(); }).catch(function () {});
    load(false);
  });
})();
