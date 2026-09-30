/* Shared Ledger UI: entry rows, thumbnails, sign-in modal, save/edit dialogs, thread picker. Needs site.js first. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc;

  LLF.dur = function (s) {
    if (s == null) return '';
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
    return h ? h + ':' + String(m).padStart(2, '0') + ':' + String(x).padStart(2, '0') : m + ':' + String(x).padStart(2, '0');
  };
  LLF.fdate = function (iso) {
    if (!iso) return '';
    var d = new Date(iso.replace(' ', 'T') + (iso.indexOf('Z') < 0 && iso.length <= 19 ? 'Z' : ''));
    return isNaN(d) ? '' : d.toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'});
  };
  LLF.data = null;
  LLF.siteData = function () {
    if (!LLF.data) LLF.data = fetch('/site-data.json').then(function (r) { return r.json(); }).catch(function () { return {categories: [], topics: [], kinds: [], platforms: []}; });
    return LLF.data;
  };
  LLF.lengthLabels = {lt1: 'Under 1 minute', m1_3: '1 to 3 minutes', m3_10: '3 to 10 minutes', gt10: 'Longer', unknown: 'Length unknown'};
  LLF.platformLabels = {youtube: 'YouTube', instagram: 'Instagram', tiktok: 'TikTok'};

  // ---- thumbnails: provider image when we have a portrait one, typographic fallback otherwise. Never a fabricated frame.
  LLF.thumb = function (v, cls) {
    var dur = v.duration != null ? '<span class="duration">' + LLF.dur(v.duration) + '</span>' : '';
    var plat = '<span class="platform">' + esc(v.platform.replace('Instagram ', 'IG ')) + '</span>';
    var play = (v.illustrative || v.availability !== 'ok') ? '' : '<a class="play" href="' + esc(v.url) + '" target="_blank" rel="noopener" aria-label="Watch the original on ' + esc(v.platform) + '">▶</a>';
    if (v.thumb && v.orientation === 'portrait') {
      return '<div class="thumb ' + (cls || '') + '"><img src="' + esc(v.thumb) + '" alt="" loading="lazy" data-thumb>' + dur + play + plat + '</div>';
    }
    return '<div class="thumb fallback ' + (cls || '') + '"><span class="nothumb">No preview</span><span class="ft">' + esc(v.title || v.creator_handle || 'Short video') + '</span>' + dur + plat + '</div>';
  };
  document.addEventListener('error', function (e) {
    var t = e.target;
    if (t && t.tagName === 'IMG' && t.hasAttribute('data-thumb')) {
      var box = t.parentNode; box.classList.add('fallback'); t.remove();
      if (!box.querySelector('.ft')) box.insertAdjacentHTML('afterbegin', '<span class="nothumb">No preview</span>');
    }
  }, true);

  function watchLink(v, cls) {
    if (v.illustrative) return '<span class="' + (cls === 'watch' ? 'nolink' : 'dim') + '" title="Sample row: there is no real post behind it">Sample clip</span>';
    if (v.availability !== 'ok') return '<span class="dim">Original unavailable' + (v.last_checked ? ' · checked ' + esc(LLF.fdate(v.last_checked)) : '') + '</span>';
    return '<a class="' + (cls === 'watch' ? 'watch' : 'act') + '" href="' + esc(v.url) + '" target="_blank" rel="noopener">Watch original ↗</a>';
  }
  function entryHref(it) { return it.video.ledger_no ? '/look/L-' + String(it.video.ledger_no).padStart(3, '0') + '/' : '/look/entry/?id=' + it.video.id; }
  function saverHtml(sv) {
    var n = esc(sv.display_name);
    return sv.profile_public ? '<a href="/u/' + esc(sv.handle) + '/">' + n + ' ↗</a>' : n;
  }
  function creatorHtml(v) {
    var c = v.creator_handle || v.creator_name || 'Creator not listed';
    return '<strong>' + (v.creator_url ? '<a href="' + esc(v.creator_url) + '" target="_blank" rel="noopener">' + esc(c) + '</a>' : esc(c)) + '</strong> / ' + esc(v.platform.split(' ')[0]);
  }
  function tagLinks(it) {
    var s = it.save, out = '';
    if (s.category) out += '<a class="tag" href="/look/?category=' + esc(s.category) + '">' + esc(catLabel(s.category)) + '</a>';
    if (s.topic && (s.topic_label || s.topic) !== catLabel(s.category)) out += '<a class="tag" href="/look/?topic=' + esc(s.topic) + '">' + esc(s.topic_label || s.topic) + '</a>';
    return out;
  }
  var CATL = {politics: 'Politics', economy: 'Economy', society: 'Society', 'everyday-life': 'Everyday life'};
  function catLabel(c) { return CATL[c] || c; }
  LLF.catLabel = catLabel;
  function threadTags(it) {
    return it.save.threads.map(function (t) { return '<a class="thread-chip" href="/threads/' + esc(t.slug) + '/">' + esc(t.title) + '</a>'; }).join('');
  }
  function statusChip(s) {
    if (!s.mine) return '';
    var m = {private: ['Private', ''], pending: ['Pending review', 'pending'], approved: ['In public Ledger', 'public'], rejected: ['Not accepted', 'rejected']}[s.status] || ['', ''];
    return '<span class="status ' + m[1] + '">' + m[0] + '</span>' + (s.status === 'rejected' && s.reject_reason ? '<div class="small" style="margin-top:4px">' + esc(s.reject_reason) + '</div>' : '');
  }

  LLF.entryRow = function (it, o) {
    o = o || {};
    var v = it.video, s = it.save, mine = o.mode === 'mine';
    var eyebrow = (v.ledger ? esc(v.ledger) : 'Private') + ' &nbsp;·&nbsp; <b>' + esc(s.label) + '</b>' + (it.deep_dive ? ' &nbsp;·&nbsp; <span class="deep-badge">Deep dive attached</span>' : '') + (v.illustrative ? '<span class="illus-tag">Illustrative</span>' : '');
    var meta2 = [s.kind, v.duration != null ? LLF.dur(v.duration) : 'Length unknown', v.language ? v.language.toUpperCase() : ''].filter(Boolean);
    meta2 = meta2.join(' · ');
    var acts = watchLink(v) + '<button class="act" data-act="notes" aria-expanded="false">Open notes' + (it.other_notes ? ' (' + (it.other_notes + 1) + ')' : '') + ' ↗</button>';
    if (it.deep_dive) acts += '<a class="act" href="' + esc(it.links.learn[0].url) + '">Read the deep dive →</a>';
    if (it.find_link) acts += '<a class="act" href="' + esc(it.links.find[0].url) + '">Find it in the world →</a>';
    if (mine) {
      acts += '<div>' + statusChip(s) + '</div>';
      acts += s.status === 'private' || s.status === 'rejected' ? '<button class="act" data-act="vis" data-to="public">Add to public Ledger</button>' : '<button class="act" data-act="vis" data-to="private">Make private</button>';
      acts += '<button class="act" data-act="edit">Edit</button><button class="act" data-act="del">Delete</button>';
      if (LLF.user && LLF.user.collections.length) acts += '<select class="cselect" data-act="col" aria-label="Add to collection" style="height:30px;font-size:9px"><option value="">+ Collection</option>' + LLF.user.collections.map(function (c) { return '<option value="' + c.id + '">' + esc(c.title) + '</option>'; }).join('') + '</select>';
    } else {
      var mineSave = it.my_save;
      acts += '<button class="row-save' + (mineSave ? ' on' : '') + '" data-act="save">' + (mineSave ? (mineSave.status === 'private' ? 'Saved ✓' : 'In your Ledger ✓') : 'Save +') + '</button>';
    }
    acts += '<span class="added">Added ' + esc(LLF.fdate(s.added_at)) + '</span>';
    return '<div class="entry-wrap" data-vid="' + v.id + '" data-sid="' + s.id + '"><article class="entry">' + LLF.thumb(v) +
      '<div class="entry-main"><span class="eyebrow">' + eyebrow + '</span><h3 class="entry-title"><a href="' + entryHref(it) + '">' + esc(v.title || (v.creator_handle ? 'Post by ' + v.creator_handle : 'Untitled short')) + '</a></h3>' +
      (s.note ? '<p class="entry-note">“' + esc(s.note) + '”</p>' : '<p class="entry-note small">No note yet.</p>') + (s.threads.length ? '<div class="thread-chips" style="margin-top:10px">' + threadTags(it) + '</div>' : '') + '</div>' +
      '<div class="entry-meta">' + tagLinks(it) + '<div class="meta-secondary">' + esc(meta2) + '</div></div>' +
      '<div class="entry-people"><div><div class="by-label">Original creator</div><div class="person">' + creatorHtml(v) + '</div></div><div class="saver"><div class="by-label">Saved by</div><div class="person">' + saverHtml(s.saver) + '</div></div></div>' +
      '<div class="row-actions">' + acts + '</div></article><div class="entry-extra" data-extra></div></div>';
  };

  LLF.featured = function (it) {
    var v = it.video, s = it.save;
    var facts = '<div><span class="fact-label">Subject / Length</span><div class="fact-value">' + esc([catLabel(s.category), s.topic_label].filter(Boolean).join(' · ')) + (v.duration != null ? ' / ' + LLF.dur(v.duration) : '') + '</div></div>' +
      '<div><span class="fact-label">Kind</span><div class="fact-value">' + esc(s.kind) + '</div></div>';
    if (it.deep_dive) facts += '<div><span class="fact-label">Context</span><div class="fact-value"><a href="' + esc(it.links.learn[0].url) + '">Deep dive attached ↗</a></div></div>';
    return '<div class="featured-row entry-wrap" data-vid="' + v.id + '" data-sid="' + s.id + '">' + LLF.thumb(v, 'feat-visual') +
      '<div class="feat-main"><span class="eyebrow">' + esc(v.ledger || '') + ' &nbsp;•&nbsp; ' + esc(s.label) + (v.illustrative ? '<span class="illus-tag">Illustrative</span>' : '') + '</span><h2><a href="' + entryHref(it) + '" style="text-decoration:none">' + esc(v.title) + '</a></h2>' +
      '<p class="note">“' + esc(s.note) + '”</p><div class="attribution">Originally posted by ' + esc(v.creator_handle || 'unknown') + ' &nbsp;·&nbsp; Saved by ' + esc(s.saver.display_name) + '</div></div>' +
      '<div class="feat-facts">' + facts + '</div><div class="feat-actions">' + watchLink(v, 'watch') + '<button class="save' + (it.my_save ? ' on' : '') + '" data-act="save">' + (it.my_save ? 'Saved ✓' : 'Save +') + '</button></div></div>';
  };

  // compact card used by shelves on thread/topic/category pages
  LLF.miniRow = function (it) {
    var v = it.video, s = it.save;
    return '<div class="entry-wrap" data-vid="' + v.id + '" data-sid="' + s.id + '"><article class="entry mini">' + LLF.thumb(v) +
      '<div class="entry-main"><span class="eyebrow">' + esc(v.ledger || '') + ' · <b>' + esc(s.label) + '</b>' + (it.deep_dive ? ' · <span class="deep-badge">Deep dive attached</span>' : '') + (v.illustrative ? '<span class="illus-tag">Illustrative</span>' : '') + '</span><h3 class="entry-title" style="font-size:21px"><a href="' + entryHref(it) + '">' + esc(v.title || 'Untitled short') + '</a></h3><p class="entry-note">“' + esc(s.note) + '”</p>' +
      '<div class="meta-secondary">Originally posted by ' + esc(v.creator_handle || 'unknown') + ' · Saved by ' + esc(s.saver.display_name) + '</div></div>' +
      '<div class="row-actions">' + watchLink(v) + '<a class="act" href="' + entryHref(it) + '">Open notes ↗</a><button class="row-save' + (it.my_save ? ' on' : '') + '" data-act="save">' + (it.my_save ? 'Saved ✓' : 'Save +') + '</button></div></article><div class="entry-extra" data-extra></div></div>';
  };

  // ---- modal
  LLF.modal = function (html, onclose) {
    var m = document.createElement('div'); m.className = 'modal open'; m.setAttribute('role', 'dialog'); m.setAttribute('aria-modal', 'true');
    m.innerHTML = '<div class="box"><button class="x" aria-label="Close">×</button>' + html + '</div>';
    function close() { m.remove(); document.removeEventListener('keydown', key); if (onclose) onclose(); }
    function key(e) { if (e.key === 'Escape') close(); }
    m.addEventListener('click', function (e) { if (e.target === m || e.target.classList.contains('x')) close(); });
    document.addEventListener('keydown', key); document.body.appendChild(m);
    var first = m.querySelector('input,select,textarea,button:not(.x)'); if (first) first.focus();
    m.close = close; return m;
  };

  // ---- sign in / create profile, inline
  LLF.authModal = function (why, done) {
    var mode = 'signup';
    var m = LLF.modal('<div data-body></div>');
    function draw() {
      var su = mode === 'signup';
      m.querySelector('[data-body]').innerHTML = '<h2>' + (su ? 'Keep this one?' : 'Welcome back.') + '</h2><p class="small" style="font-size:14px;margin-bottom:16px">' +
        esc(why || (su ? 'Create a profile to save it and follow other people’s finds. Saves are private unless you choose otherwise.' : 'Sign in to your Ledger.')) + '</p>' +
        '<form data-f><div class="field"><label for="am-e">Email</label><input class="input" id="am-e" name="email" type="email" required autocomplete="email"></div>' +
        (su ? '<div class="two"><div class="field"><label for="am-h">Handle</label><input class="input" id="am-h" name="handle" required pattern="[A-Za-z0-9_]{3,24}" autocomplete="username"><div class="hint">Letters, numbers, underscore.</div></div><div class="field"><label for="am-n">Display name</label><input class="input" id="am-n" name="display_name" autocomplete="name"></div></div>' : '') +
        '<div class="field"><label for="am-p">Password</label><input class="input" id="am-p" name="password" type="password" required minlength="8" autocomplete="' + (su ? 'new-password' : 'current-password') + '"></div>' +
        '<div class="notice err" data-err hidden></div><button class="btn" type="submit">' + (su ? 'Create profile' : 'Sign in') + '</button> ' +
        '<button type="button" class="btn ghost" data-toggle>' + (su ? 'I have an account' : 'Create a profile') + '</button></form>';
      var f = m.querySelector('[data-f]');
      m.querySelector('[data-toggle]').onclick = function () { mode = su ? 'signin' : 'signup'; draw(); };
      f.onsubmit = function (e) {
        e.preventDefault();
        var d = {}; new FormData(f).forEach(function (v, k) { d[k] = v; });
        LLF.api(su ? 'auth/signup' : 'auth/login', {body: d}).then(function (j) { LLF.csrf = j.csrf; LLF.user = j.user; m.close(); if (done) done(j.user); })
          .catch(function (er) { var x = m.querySelector('[data-err]'); x.hidden = false; x.textContent = er.message; });
      };
    }
    draw(); return m;
  };
  LLF.requireUser = function (why, cb) {
    LLF.me().then(function (u) { if (u) cb(u); else LLF.authModal(why, function () { LLF.me(true).then(function (u2) { if (u2) cb(u2); }); }); });
  };

  // ---- thread picker (curated list; contributors may propose)
  LLF.threadPicker = function (host, initial) {
    var state = {sel: (initial || []).slice(), propose: []}, all = [];
    host.classList.add('thread-picker');
    host.innerHTML = '<div class="sel" data-sel></div><input class="input" data-q placeholder="Add a thread, e.g. Tartaria" aria-label="Add a thread" autocomplete="off"><div class="opts" data-opts hidden></div><div class="hint">Threads are curated subjects. Pick an existing one, or propose a new one for editors to review.</div>';
    var sel = host.querySelector('[data-sel]'), q = host.querySelector('[data-q]'), opts = host.querySelector('[data-opts]');
    LLF.api('threads').then(function (j) { all = j.threads; draw(); });
    function title(slug) { var t = all.filter(function (x) { return x.slug === slug; })[0]; return t ? t.title : slug; }
    function draw() {
      sel.innerHTML = state.sel.map(function (s) { return '<span class="thread-chip" data-rm="' + esc(s) + '" role="button" tabindex="0">' + esc(title(s)) + '</span>'; }).join('') +
        state.propose.map(function (s) { return '<span class="thread-chip" data-rmp="' + esc(s) + '" role="button" tabindex="0" title="Proposed: editors will review">' + esc(s) + ' (proposed)</span>'; }).join('');
    }
    function list() {
      var t = q.value.trim().toLowerCase(); if (!t) { opts.hidden = true; return; }
      var hits = all.filter(function (x) { return state.sel.indexOf(x.slug) < 0 && (x.title + ' ' + x.aliases.join(' ')).toLowerCase().indexOf(t) >= 0; }).slice(0, 6);
      var html = hits.map(function (x) { return '<button type="button" data-pick="' + esc(x.slug) + '">' + esc(x.title) + '<small>' + esc(LLF.catLabel(x.category)) + '</small></button>'; }).join('');
      if (t.length >= 3 && !all.some(function (x) { return x.title.toLowerCase() === t; })) html += '<button type="button" data-new="' + esc(q.value.trim()) + '">Propose “' + esc(q.value.trim()) + '” as a new thread</button>';
      opts.innerHTML = html; opts.hidden = !html;
    }
    q.addEventListener('input', list);
    q.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); var b = opts.querySelector('button'); if (b) b.click(); } });
    opts.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      if (b.dataset.pick && state.sel.length < 6) state.sel.push(b.dataset.pick);
      if (b.dataset['new'] && state.propose.length < 3) state.propose.push(b.dataset['new']);
      q.value = ''; opts.hidden = true; draw();
    });
    sel.addEventListener('click', function (e) {
      var r = e.target.closest('[data-rm]'), p = e.target.closest('[data-rmp]');
      if (r) state.sel = state.sel.filter(function (x) { return x !== r.dataset.rm; });
      if (p) state.propose = state.propose.filter(function (x) { return x !== p.dataset.rmp; });
      draw();
    });
    draw();
    return {get: function () { return {threads: state.sel.slice(), propose_threads: state.propose.slice()}; }};
  };

  // ---- save form used for edit + publish-from-mine
  LLF.editSave = function (it, done) {
    LLF.siteData().then(function (sd) {
      var s = it.save, v = it.video;
      var topicOpts = sd.categories.map(function (c) { return '<optgroup label="' + esc(c.label) + '">' + sd.topics.filter(function (t) { return t.category === c.slug; }).map(function (t) { return '<option value="' + t.slug + '"' + (t.slug === s.topic ? ' selected' : '') + '>' + esc(t.label) + '</option>'; }).join('') + '</optgroup>'; }).join('');
      var m = LLF.modal('<h2>Edit your save</h2><p class="small" style="font-size:14px">' + esc(v.title || v.url) + '</p><form data-f>' +
        '<div class="field"><label for="es-n">Why was this worth keeping?</label><textarea class="input" id="es-n" name="note" maxlength="600">' + esc(s.note) + '</textarea></div>' +
        '<div class="two"><div class="field"><label for="es-t">Topic</label><select class="select" id="es-t" name="topic"><option value="">Choose</option>' + topicOpts + '</select></div>' +
        '<div class="field"><label for="es-k">Kind of post</label><select class="select" id="es-k" name="kind"><option value="">Choose</option>' + sd.kinds.map(function (k) { return '<option' + (k === s.kind ? ' selected' : '') + '>' + esc(k) + '</option>'; }).join('') + '</select></div></div>' +
        '<div class="field"><label>Threads</label><div data-tp></div></div>' +
        (s.status === 'approved' ? '<div class="notice">This save is public. Changing the note or tags sends it back for a quick review before it shows again.</div>' : '') +
        '<div class="notice err" data-err hidden></div><button class="btn" type="submit">Save changes</button></form>');
      var tp = LLF.threadPicker(m.querySelector('[data-tp]'), s.threads.map(function (t) { return t.slug; }));
      var f = m.querySelector('[data-f]');
      f.onsubmit = function (e) {
        e.preventDefault();
        var d = {video_id: v.id, note: f.note.value, topic: f.topic.value, kind: f.kind.value, visibility: s.visibility === 'public' || s.status !== 'private' ? 'public' : 'private'};
        var t = tp.get(); d.threads = t.threads; d.propose_threads = t.propose;
        if (s.status === 'rejected') d.visibility = 'private';
        LLF.api('ledger/save', {body: d}).then(function () { m.close(); LLF.toast('Saved.'); done && done(); })
          .catch(function (er) {
            if (er.status === 409) { d.make_profile_public = true; return LLF.api('ledger/save', {body: d}).then(function () { m.close(); done && done(); }); }
            var x = m.querySelector('[data-err]'); x.hidden = false; x.textContent = er.message;
          });
      };
    });
  };

  // ---- delegated row behaviour (save, notes, visibility, delete, edit, add to collection)
  LLF.bindRows = function (root, ctx) {
    ctx = ctx || {};
    root.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]'); if (!b || b.tagName === 'SELECT') return;
      var wrap = b.closest('[data-vid]'); if (!wrap) return;
      var vid = +wrap.dataset.vid, sid = +wrap.dataset.sid, act = b.dataset.act;
      var item = ctx.find ? ctx.find(vid, sid) : null;
      if (act === 'save') {
        LLF.requireUser('Keep this one? Create a profile to save it and follow other people’s finds.', function () {
          var on = b.classList.contains('on');
          if (on && item && item.my_save) {
            if (item.my_save.status !== 'private') { LLF.toast('This is in the public Ledger. Manage it from My Ledger.'); return; }
            LLF.api('ledger/delete', {body: {save_id: item.my_save.id}}).then(function () { item.my_save = null; b.classList.remove('on'); b.textContent = 'Save +'; LLF.toast('Removed from your Ledger.'); });
          } else {
            LLF.api('ledger/save', {body: {video_id: vid, visibility: 'private'}}).then(function (j) {
              if (item) item.my_save = {id: j.save_id, visibility: 'private', status: 'private'};
              LLF.qsa('[data-vid="' + vid + '"] [data-act="save"]').forEach(function (x) { x.classList.add('on'); x.textContent = 'Saved ✓'; });
              LLF.toast('Saved privately. Add a note or make it public from My Ledger.');
            }).catch(function (er) { LLF.toast(er.message); });
          }
        });
      } else if (act === 'notes') {
        var ex = wrap.querySelector('[data-extra]');
        if (ex.classList.toggle('open')) {
          b.setAttribute('aria-expanded', 'true');
          if (!ex.dataset.loaded) {
            ex.innerHTML = '<div class="notes-panel">Loading notes…</div>';
            Promise.all([LLF.api('ledger/notes?video=' + vid), item ? null : null]).then(function (r) {
              var notes = r[0].notes, v = item ? item.video : null;
              ex.dataset.loaded = '1';
              ex.innerHTML = '<div class="notes-panel">' + notes.map(function (n) {
                return '<div class="n"><div class="who">' + esc(n.label) + ' · ' + esc(n.saver.display_name) + ' · ' + esc(LLF.fdate(n.added_at)) + '</div><p>“' + esc(n.note) + '”</p></div>';
              }).join('') + (v && v.caption ? '<div class="cap"><b>Caption from ' + esc(v.platform) + ':</b> ' + esc(v.caption) + '</div>' : '') +
                '<div class="cap">A saved note is one person’s reason for keeping a link. It is not a fact-check.</div>' +
                (item && (item.links.learn.length || item.links.find.length) ? '<div class="links-line">' + item.links.learn.map(function (l) { return '<a href="' + esc(l.url) + '">Deep dive: ' + esc(l.title) + ' →</a>'; }).join('') + item.links.find.map(function (l) { return '<a href="' + esc(l.url) + '">Find it in the world: ' + esc(l.title) + ' →</a>'; }).join('') + '</div>' : '') +
                '<details class="report"><summary>Report a problem with this entry</summary><form data-report><select name="reason"><option value="broken_link">Broken link</option><option value="wrong_attribution">Wrong attribution</option><option value="spam">Spam</option><option value="needs_context">Needs context</option><option value="other">Other</option></select><input name="detail" placeholder="Details (optional)" maxlength="300"><button class="btn sm" type="submit">Send report</button></form></details></div>';
              ex.querySelector('[data-report]').onsubmit = function (ev) {
                ev.preventDefault(); var f = ev.target;
                LLF.api('report', {body: {video_id: vid, reason: f.reason.value, detail: f.detail.value}}).then(function () { LLF.toast('Thanks. An editor will take a look.'); f.closest('details').open = false; }).catch(function (er) { LLF.toast(er.message); });
              };
            }).catch(function (er) { ex.innerHTML = '<div class="notes-panel">' + esc(er.message) + '</div>'; });
          }
        } else b.setAttribute('aria-expanded', 'false');
      } else if (act === 'vis') {
        var to = b.dataset.to;
        function go(mp) { LLF.api('ledger/visibility', {body: {save_id: sid, to: to, make_profile_public: !!mp}}).then(function (j) { LLF.toast(to === 'public' ? (j.status === 'approved' ? 'Added to the public Ledger.' : 'Submitted. Your link will appear publicly after review; it is already saved for you.') : 'Now private.'); ctx.reload && ctx.reload(); })
          .catch(function (er) { if (er.status === 409 && confirm('Public saves appear with your public profile. Turn it on?')) go(true); else if (er.status === 422 && item) LLF.editSave(item, ctx.reload); else LLF.toast(er.message); }); }
        go(false);
      } else if (act === 'del') {
        if (confirm('Delete this save? This removes your note too.')) LLF.api('ledger/delete', {body: {save_id: sid}}).then(function () { LLF.toast('Deleted.'); ctx.reload && ctx.reload(); });
      } else if (act === 'edit') {
        if (item) LLF.editSave(item, ctx.reload);
      }
    });
    root.addEventListener('change', function (e) {
      var s = e.target.closest('select[data-act="col"]'); if (!s || !s.value) return;
      var wrap = s.closest('[data-vid]');
      LLF.api('collections/add', {body: {id: +s.value, save_id: +wrap.dataset.sid}}).then(function () { LLF.toast('Added to collection.'); s.value = ''; }).catch(function (er) { LLF.toast(er.message); });
    });
  };
})();
