/* /u/handle — a public Ledger profile: what they tend to look for, their public saves and collections, follow. No follower counts. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, app = document.getElementById('profile-app');
  if (!app) return;
  var m = location.pathname.match(/\/u\/([A-Za-z0-9_]+)/), handle = m ? m[1] : LLF.params().get('h') || '';
  var st = {items: [], total: 0, p: null, sd: null};

  function topicLabel(s) { var t = (st.sd.topics || []).filter(function (x) { return x.slug === s; })[0]; return t ? t.label : s; }
  function draw() {
    var p = st.p;
    document.title = p.display_name + '’s Ledger | LookLearnFind';
    if (p.private) { app.innerHTML = '<div class="prof-wrap"><h1 class="display" style="font-size:54px">' + esc(p.display_name) + '</h1><div class="empty-state">This profile is private.</div></div>'; return; }
    var ints = p.interests.map(function (i) { return '<span class="tag">' + esc(topicLabel(i)) + '</span>'; }).join('');
    app.innerHTML = '<div class="prof-wrap"><div class="prof-head"><div class="kicker">Look / Profile<i></i></div><h1>' + esc(p.display_name) + '’s Ledger' + (p.is_editor ? '<span class="illus-tag" style="background:var(--green);color:#fff">Editor</span>' : '') + '</h1>' +
      '<p class="dek" style="margin:12px 0;font-size:17px">' + esc(p.bio || '') + '</p>' + (p.looks_for ? '<p class="small" style="font-size:14px"><b>Tends to look for:</b> ' + esc(p.looks_for) + '</p>' : '') + '<div style="margin:10px 0">' + ints + '</div>' +
      '<p class="small">' + p.total + ' public save' + (p.total === 1 ? '' : 's') + '. Interested in ' + (p.interests.length ? esc(p.interests.map(topicLabel).join(', ')) : 'a bit of everything') + '.</p>' +
      '<div style="margin-top:14px" data-acts>' + (p.is_me ? '<a class="btn ghost" href="/account/">Edit profile</a>' : '<button class="btn" data-follow>' + (p.following ? 'Following ✓' : 'Follow public saves') + '</button> ' + (p.following ? '<button class="btn ghost" data-mute>' + (p.muted ? 'Unmute' : 'Mute') + '</button>' : '')) + '</div>' +
      (p.is_me ? '<p class="small" style="margin-top:8px">Your private saves are visible only to you.</p>' : '') + '</div>' +
      (p.collections.length ? '<div class="by-label" style="margin-top:20px">Collections</div><div class="col-list">' + p.collections.map(function (c) { return '<button class="col-card" data-col="' + c.id + '"><b>' + esc(c.title) + '</b>' + esc(c.premise || '') + ' <span class="small">(' + c.count + ')</span></button>'; }).join('') + '</div><div data-colbox></div>' : '') +
      '<div class="table-head" style="margin-top:24px"><span>Preview</span><span>The clip &amp; why it stayed</span><span>Filed under</span><span>People behind it</span><span>Open / save</span></div><div data-rows></div><div class="end" data-end></div></div>';
    drawRows();
  }
  function drawRows(append) {
    var rows = app.querySelector('[data-rows]');
    rows.innerHTML = st.items.map(function (it) { return LLF.entryRow(it, {mode: 'explore'}); }).join('') || '<div class="empty-state">No public saves yet.</div>';
    app.querySelector('[data-end]').innerHTML = st.items.length ? '<span>Showing ' + st.items.length + ' of ' + st.total + '. Newest public save first.</span>' + (st.items.length < st.total ? '<button class="more" data-more>More entries ↓</button>' : '') : '';
  }
  function find(v, s) { return st.items.filter(function (x) { return x.video.id === v && x.save.id === s; })[0]; }
  app.addEventListener('click', function (e) {
    var t = e.target;
    if (t.closest('[data-more]')) { LLF.api('profile?handle=' + handle + '&offset=' + st.items.length).then(function (j) { st.items = st.items.concat(j.items); drawRows(); }); }
    var f = t.closest('[data-follow]');
    if (f) LLF.requireUser('Follow ' + st.p.display_name + '’s public saves? Create a profile to follow people whose eye you trust.', function () {
      LLF.api(st.p.following ? 'unfollow' : 'follow', {body: {handle: handle}}).then(function () { st.p.following = !st.p.following; if (!st.p.following) st.p.muted = false; draw(); }).catch(function (er) { LLF.toast(er.message); });
    });
    var mu = t.closest('[data-mute]');
    if (mu) LLF.api('mute', {body: {handle: handle, muted: !st.p.muted}}).then(function () { st.p.muted = !st.p.muted; draw(); });
    var c = t.closest('[data-col]');
    if (c) LLF.api('collection?id=' + c.dataset.col).then(function (j) {
      var box = app.querySelector('[data-colbox]');
      st.items = j.items; st.total = j.items.length;
      box.innerHTML = '<div class="notice"><b>' + esc(j.title) + '</b> · curated by ' + esc(j.curator.display_name) + '. ' + esc(j.premise || '') + ' <button class="clear" data-back>Show all saves</button></div>';
      drawRows();
    });
    if (t.closest('[data-back]')) location.reload();
  });
  LLF.bindRows(app, {find: find, reload: function () { location.reload(); }});
  LLF.me().then(function () { return LLF.siteData(); }).then(function (sd) {
    st.sd = sd; return LLF.api('profile?handle=' + encodeURIComponent(handle));
  }).then(function (p) { st.p = p; st.items = p.items || []; st.total = p.total || 0; draw(); })
    .catch(function (er) { app.innerHTML = '<div class="empty-state">' + esc(er.status === 404 ? 'We could not find that profile.' : er.message) + '<div class="btns"><a class="btn" href="/look/">Back to the Ledger</a></div></div>'; });
})();
