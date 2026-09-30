/* /admin/ — editors: review queue, reports, entries, threads, the desk shelf. Admins also manage people and sample data. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, app = document.getElementById('admin-app');
  if (!app) return;
  var sd = null, sum = {}, tab = 'queue', me = null, content = {learn: [], find: []};

  function api(p, b) { return LLF.api(p, b ? {body: b} : undefined); }
  function sel(name, opts, cur, blank) { return '<select name="' + name + '"><option value="">' + blank + '</option>' + opts.map(function (o) { return '<option value="' + esc(o[0]) + '"' + (o[0] === cur ? ' selected' : '') + '>' + esc(o[1]) + '</option>'; }).join('') + '</select>'; }
  function topicOpts() { return sd.topics.map(function (t) { return [t.slug, t.label]; }); }
  function catOpts() { return sd.categories.map(function (t) { return [t.slug, t.label]; }); }
  function kindOpts() { return sd.kinds.map(function (k) { return [k, k]; }); }

  function frame() {
    var tabs = [['queue', 'Queue', sum.pending], ['reports', 'Reports', sum.reports], ['entries', 'Entries'], ['threads', 'Threads', sum.thread_proposals], ['desk', 'From the desk'], ['audit', 'Audit log']];
    if (me.role === 'admin') tabs.push(['people', 'People'], ['sample', 'Sample data']);
    app.innerHTML = '<div class="kicker">Editors<i></i></div><h1 class="display" style="font-size:clamp(38px,5vw,56px);margin-bottom:20px">The desk.</h1>' +
      '<p class="small" style="margin-bottom:16px">' + sum.entries + ' entries in the public index · ' + sum.unavailable + ' unavailable · Editors correct tags and attribution, merge duplicates, add context, or remove entries. Every action is logged.</p>' +
      '<div class="adm-tabs">' + tabs.map(function (t) { return '<button data-tab="' + t[0] + '" class="' + (t[0] === tab ? 'sel' : '') + '">' + t[1] + (t[2] ? '<span class="ct">' + t[2] + '</span>' : '') + '</button>'; }).join('') + '</div><div data-pane></div>';
    LLF.qsa('[data-tab]', app).forEach(function (b) { b.onclick = function () { tab = b.dataset.tab; frame(); load(); }; });
  }
  function pane() { return app.querySelector('[data-pane]'); }
  function refresh() { api('admin/summary').then(function (s) { sum = s; frame(); load(); }); }

  function thumbCard(it) { return LLF.thumb(it.video); }

  function load() {
    var box = pane(); box.innerHTML = 'Loading…';
    if (tab === 'queue') api('admin/queue').then(function (j) {
      if (!j.items.length) { box.innerHTML = '<div class="empty-state">Nothing waiting. The queue is clear.</div>'; return; }
      box.innerHTML = j.items.map(function (it) {
        var v = it.video, s = it.save, c = it.contributor;
        return '<div class="adm-card" data-sid="' + s.id + '">' + thumbCard(it) + '<div class="f"><h3>' + esc(v.title || v.url) + '</h3><div><a href="' + esc(v.url) + '" target="_blank" rel="noopener">' + esc(v.url) + '</a> · ' + esc(v.platform) + ' · by ' + esc(v.creator_handle || 'unknown') + '</div>' +
          '<div style="margin:8px 0"><b>Submitted by</b> ' + esc(c.display_name) + ' (@' + esc(c.handle) + ') · “' + esc(s.note) + '”' + (it.already_in_index ? ' <span class="status pending">Video already in the index: this adds a note</span>' : '') + '</div>' +
          '<div class="edit">' + sel('category', catOpts(), s.category, 'Subject') + sel('topic', topicOpts(), s.topic, 'Topic') + sel('kind', kindOpts(), s.kind, 'Kind') + '</div>' +
          '<div class="edit" style="grid-template-columns:1fr"><input name="threads" value="' + esc(it.all_threads.join(', ')) + '" placeholder="thread slugs, comma separated" aria-label="Threads">' + (it.proposed_threads.length ? '<div class="small">Proposed threads: ' + it.proposed_threads.map(function (t) { return esc(t.title) + ' (' + esc(t.slug) + ')'; }).join(', ') + '. Approve them in the Threads tab.</div>' : '') + '<textarea name="note" rows="2" aria-label="Note">' + esc(s.note) + '</textarea></div>' +
          '<div class="btns"><button class="btn sm" data-a="approve">Approve</button><button class="btn sm ghost" data-a="edit">Save edits</button><button class="btn sm danger" data-a="reject">Reject…</button></div></div></div>';
      }).join('');
    }).catch(err);
    else if (tab === 'reports') api('admin/reports').then(function (j) {
      if (!j.reports.length) { box.innerHTML = '<div class="empty-state">No open reports.</div>'; return; }
      box.innerHTML = '<table class="plain"><tr><th>Entry</th><th>Reason</th><th>Detail</th><th></th></tr>' + j.reports.map(function (r) {
        return '<tr data-rid="' + r.id + '"><td>' + (r.video ? esc((r.video.ledger || 'Private') + ' · ' + (r.video.title || r.video.url)) : '?') + '</td><td>' + esc(r.reason.replace('_', ' ')) + '<div class="small">' + esc(r.created_at) + (r.reporter ? ' · @' + esc(r.reporter) : '') + '</div></td><td>' + esc(r.detail) + '</td><td><button class="btn sm" data-ra="resolve">Resolve</button> <button class="btn sm ghost" data-ra="dismiss">Dismiss</button> ' + (r.video ? '<button class="btn sm ghost" data-find="' + esc(r.video.ledger_no || r.video.id) + '">Open entry</button>' : '') + '</td></tr>';
      }).join('') + '</table>';
    }).catch(err);
    else if (tab === 'entries') entries('');
    else if (tab === 'threads') api('admin/threads').then(function (j) {
      LLF.api('threads').then(function (all) {
        var opts = all.threads.map(function (t) { return '<option value="' + esc(t.slug) + '">' + esc(t.title) + '</option>'; }).join('');
        box.innerHTML = '<h2 class="h3" style="margin-bottom:12px">Proposals</h2>' + (j.threads.length ? j.threads.map(function (t) {
          return '<div class="adm-card" style="grid-template-columns:1fr" data-slug="' + esc(t.slug) + '"><div class="f"><h3>' + esc(t.title) + '</h3><div class="small">Proposed by ' + esc(t.proposed_by || 'unknown') + ' · used by ' + t.uses + ' save' + (t.uses === 1 ? '' : 's') + '</div>' +
            '<div class="edit"><input name="title" value="' + esc(t.title) + '"><input name="summary" value="' + esc(t.summary) + '" placeholder="One-line summary"><input name="aliases" value="' + esc(t.aliases.join(', ')) + '" placeholder="aliases, comma separated"></div><div class="edit">' + sel('category', catOpts(), t.category, 'Subject') + '<select name="into"><option value="">Merge into…</option>' + opts + '</select></div>' +
            '<div class="btns"><button class="btn sm" data-ta="approve">Approve as thread</button><button class="btn sm ghost" data-ta="merge">Merge as alias</button><button class="btn sm danger" data-ta="reject">Reject</button></div></div></div>';
        }).join('') : '<p class="small">No proposals waiting.</p>') +
          '<h2 class="h3" style="margin:26px 0 12px">Create a thread</h2><form class="form-card" style="max-width:720px" data-tc><div class="field"><label>Name</label><input class="input" name="title" required></div><div class="field"><label>Summary</label><input class="input" name="summary"></div><div class="field"><label>Aliases</label><input class="input" name="aliases" placeholder="comma separated"></div><div class="field">' + sel('category', catOpts(), '', 'Subject') + '</div><button class="btn" type="submit">Create</button></form>' +
          '<p class="small" style="margin-top:16px">Threads created here work immediately on the Ledger. To give a thread a built page with stories and Finds listed, also add it to <code>data/threads.json</code> and rebuild the site.</p>';
        var f = box.querySelector('[data-tc]');
        f.onsubmit = function (e) { e.preventDefault(); api('admin/thread', {action: 'create', title: f.title.value, summary: f.summary.value, aliases: split(f.aliases.value), category: f.category.value}).then(function () { LLF.toast('Thread created.'); refresh(); }).catch(function (er) { LLF.toast(er.message); }); };
      });
    }).catch(err);
    else if (tab === 'desk') api('ledger/list?limit=50&facets=0').then(function (j) {
      api('ledger/desk').then(function (d) {
        var cur = d.desk ? d.desk.items.map(function (i) { return i.video.id; }) : [];
        box.innerHTML = '<form class="form-card" style="max-width:820px" data-df><div class="field"><label>Shelf title</label><input class="input" name="title" value="' + esc(d.desk ? d.desk.title : 'The midterms shelf') + '" required></div><div class="field"><label>Why these</label><input class="input" name="note" value="' + esc(d.desk ? d.desk.note : 'A few links we keep coming back to, and why.') + '"></div>' +
          '<div class="field"><label>Choose up to six entries (the first is featured)</label>' + j.items.map(function (i) { return '<label style="display:flex;gap:8px;font:13px var(--sans);text-transform:none;letter-spacing:0;font-weight:400;margin-bottom:6px"><input type="checkbox" name="v" value="' + i.video.id + '"' + (cur.indexOf(i.video.id) >= 0 ? ' checked' : '') + '>' + esc(i.video.ledger + ' · ' + (i.video.title || i.video.url)) + '</label>'; }).join('') + '</div><button class="btn" type="submit">Publish shelf</button></form>';
        box.querySelector('[data-df]').onsubmit = function (e) { e.preventDefault(); var f = e.target; api('admin/desk', {title: f.title.value, note: f.note.value, video_ids: LLF.qsa('[name=v]:checked', f).map(function (x) { return +x.value; })}).then(function () { LLF.toast('Shelf updated.'); }).catch(function (er) { LLF.toast(er.message); }); };
      });
    }).catch(err);
    else if (tab === 'audit') api('admin/audit').then(function (j) {
      box.innerHTML = '<table class="plain"><tr><th>When</th><th>Who</th><th>Action</th><th>Target</th><th>Detail</th></tr>' + j.audit.map(function (a) { return '<tr><td>' + esc(a.created_at) + '</td><td>' + esc(a.actor || '') + '</td><td>' + esc(a.action) + '</td><td>' + esc(a.target) + '</td><td class="small">' + esc(a.detail || '') + '</td></tr>'; }).join('') + '</table>';
    }).catch(err);
    else if (tab === 'people') api('admin/people').then(function (j) {
      box.innerHTML = '<table class="plain"><tr><th>Handle</th><th>Email</th><th>Role</th><th></th></tr>' + j.people.map(function (p) { return '<tr data-h="' + esc(p.handle) + '"><td>@' + esc(p.handle) + '<div class="small">' + esc(p.display_name) + '</div></td><td>' + esc(p.email) + '</td><td><select data-role>' + ['member', 'editor', 'admin'].map(function (r) { return '<option' + (r === p.role ? ' selected' : '') + '>' + r + '</option>'; }).join('') + '</select></td><td><button class="btn sm ghost" data-setrole>Update</button></td></tr>'; }).join('') + '</table>';
    }).catch(err);
    else if (tab === 'sample') {
      box.innerHTML = '<div style="max-width:640px"><p>Loads nine illustrative Ledger entries, five sample profiles and a desk shelf so you can see the Ledger working. Every row is flagged <b>Illustrative</b> and has no real post behind it. Clear them before launch.</p><p style="margin-top:16px"><button class="btn" data-demo="load">Load sample entries</button> <button class="btn danger" data-demo="clear">Clear sample data</button></p></div>';
    }
  }
  function split(s) { return String(s || '').split(',').map(function (x) { return x.trim(); }).filter(Boolean); }
  function err(er) { pane().innerHTML = '<div class="empty-state">' + esc(er.message) + '</div>'; }

  function entries(q) {
    var box = pane();
    box.innerHTML = '<form data-es style="display:flex;gap:8px;margin-bottom:16px;max-width:560px"><input class="input" name="q" placeholder="Search by title, @creator, URL, or L-number" value="' + esc(q) + '"><button class="btn" type="submit">Search</button></form><div data-er>Searching…</div>';
    box.querySelector('[data-es]').onsubmit = function (e) { e.preventDefault(); entries(e.target.q.value); };
    api('admin/entries?q=' + encodeURIComponent(q)).then(function (j) {
      box.querySelector('[data-er]').innerHTML = j.entries.map(function (v) {
        return '<div class="adm-card" data-vid="' + v.id + '">' + LLF.thumb(v) + '<div class="f"><h3>' + esc((v.ledger || 'Not in index') + ' · ' + (v.title || v.url)) + (v.status === 'removed' ? ' <span class="status rejected">Removed</span>' : '') + (v.availability !== 'ok' ? ' <span class="status pending">Unavailable</span>' : '') + '</h3>' +
          '<div class="small"><a href="' + esc(v.url) + '" target="_blank" rel="noopener">' + esc(v.url) + '</a> · last checked ' + esc(v.last_checked || 'never') + '</div>' +
          '<div class="edit"><input name="title" value="' + esc(v.title) + '" placeholder="Title"><input name="creator_handle" value="' + esc(v.creator_handle) + '" placeholder="@creator"><input name="duration" value="' + (v.duration != null ? LLF.dur(v.duration) : '') + '" placeholder="m:ss"></div>' +
          '<div class="edit" style="grid-template-columns:1fr 1fr"><input name="learn" list="dl-learn" value="' + esc(v.links.learn.map(function (l) { return l.slug; }).join(', ')) + '" placeholder="Learn story slugs (Deep dive attached)"><input name="find" list="dl-find" value="' + esc(v.links.find.map(function (l) { return l.slug; }).join(', ')) + '" placeholder="Find slugs (Find it in the world)"></div>' +
          '<div class="btns"><button class="btn sm" data-ea="edit">Save details + links</button><button class="btn sm ghost" data-ea="recheck">Recheck link</button>' + (v.availability === 'ok' ? '<button class="btn sm ghost" data-ea="unavailable">Mark unavailable</button>' : '<button class="btn sm ghost" data-ea="available">Mark available</button>') + (v.status === 'removed' ? '<button class="btn sm ghost" data-ea="restore">Restore</button>' : '<button class="btn sm danger" data-ea="remove">Remove</button>') + '<button class="btn sm ghost" data-ea="merge">Merge into…</button></div></div></div>';
      }).join('') || '<div class="empty-state">No entries match.</div>';
    }).catch(err);
  }

  app.addEventListener('click', function (e) {
    var t = e.target, b;
    if ((b = t.closest('[data-a]'))) {
      var card = b.closest('[data-sid]'), sid = +card.dataset.sid, act = b.dataset.a, edits = {};
      ['category', 'topic', 'kind'].forEach(function (k) { edits[k] = card.querySelector('[name=' + k + ']').value; });
      edits.note = card.querySelector('[name=note]').value; edits.threads = split(card.querySelector('[name=threads]').value);
      var body = {save_id: sid, action: act, edits: edits};
      if (act === 'reject') { var r = prompt('Reason to show the contributor (optional):', ''); if (r === null) return; body.reason = r; }
      api('admin/review', body).then(function () { LLF.toast(act === 'approve' ? 'Approved.' : act === 'reject' ? 'Rejected.' : 'Saved.'); refresh(); }).catch(function (er) { LLF.toast(er.message); });
    } else if ((b = t.closest('[data-ra]'))) {
      var note = prompt('Note (optional):', ''); if (note === null) return;
      api('admin/report', {report_id: +b.closest('[data-rid]').dataset.rid, action: b.dataset.ra, note: note}).then(function () { refresh(); });
    } else if ((b = t.closest('[data-find]'))) { tab = 'entries'; frame(); entries(String(b.dataset.find)); }
    else if ((b = t.closest('[data-ea]'))) {
      var c = b.closest('[data-vid]'), vid = +c.dataset.vid, a = b.dataset.ea;
      if (a === 'edit') {
        api('admin/entry', {video_id: vid, action: 'edit', title: c.querySelector('[name=title]').value, creator_handle: c.querySelector('[name=creator_handle]').value, duration: c.querySelector('[name=duration]').value})
          .then(function () { return api('admin/entry', {video_id: vid, action: 'set_links', learn: split(c.querySelector('[name=learn]').value), find: split(c.querySelector('[name=find]').value)}); })
          .then(function () { LLF.toast('Saved.'); }).catch(function (er) { LLF.toast(er.message); });
      } else if (a === 'merge') {
        var into = prompt('Merge this entry into which video id? (the duplicate is removed; its notes move over)'); if (!into) return;
        api('admin/entry', {video_id: vid, action: 'merge', into: +into}).then(function () { LLF.toast('Merged.'); refresh(); }).catch(function (er) { LLF.toast(er.message); });
      } else if (a === 'remove' && !confirm('Remove this entry from the Ledger? It can be restored.')) return;
      else api('admin/entry', {video_id: vid, action: a}).then(function (j) { LLF.toast(a === 'recheck' ? 'Link looks ' + j.availability + '.' : 'Done.'); refresh(); }).catch(function (er) { LLF.toast(er.message); });
    } else if ((b = t.closest('[data-ta]'))) {
      var tc = b.closest('[data-slug]'), q = function (n) { return tc.querySelector('[name=' + n + ']').value; };
      api('admin/thread', {action: b.dataset.ta, slug: tc.dataset.slug, title: q('title'), summary: q('summary'), aliases: split(q('aliases')), category: q('category'), into: q('into')}).then(function () { LLF.toast('Done.'); refresh(); }).catch(function (er) { LLF.toast(er.message); });
    } else if ((b = t.closest('[data-setrole]'))) {
      var row = b.closest('[data-h]'); api('admin/user', {handle: row.dataset.h, role: row.querySelector('[data-role]').value}).then(function () { LLF.toast('Updated.'); }).catch(function (er) { LLF.toast(er.message); });
    } else if ((b = t.closest('[data-demo]'))) {
      if (b.dataset.demo === 'clear' && !confirm('Remove all illustrative sample entries and sample profiles?')) return;
      api('admin/demo', {action: b.dataset.demo}).then(function (j) { LLF.toast(j.cleared ? 'Sample data cleared.' : (j.seeded ? 'Loaded ' + j.seeded + ' sample entries.' : j.note)); refresh(); }).catch(function (er) { LLF.toast(er.message); });
    }
  });

  LLF.me().then(function (u) {
    if (!u || !u.is_editor) { app.innerHTML = '<div class="empty-state">Editors only. ' + (u ? '' : 'Sign in with an editor account to continue.') + '<div class="btns"><a class="btn" href="/account/?next=/admin/">Sign in</a></div></div>'; return; }
    me = u;
    Promise.all([LLF.siteData(), api('admin/summary'), fetch('/search-index.json').then(function (r) { return r.json(); }).catch(function () { return []; })]).then(function (r) {
      sd = r[0]; sum = r[1];
      var dl = function (id, t) { return '<datalist id="' + id + '">' + r[2].filter(function (x) { return x.t === t; }).map(function (x) { return '<option value="' + esc(x.url.replace(/\/$/, '').split('/').pop()) + '">' + esc(x.title) + '</option>'; }).join('') + '</datalist>'; };
      document.body.insertAdjacentHTML('beforeend', dl('dl-learn', 'story') + dl('dl-find', 'find'));
      frame(); load();
    });
  });
})();
