/* /look/L-042/ — a single Ledger entry with every saver's note, links into Learn and Find, and report. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, app = document.getElementById('entry-app');
  if (!app) return;
  var m = location.pathname.match(/\/look\/(L-?\d+)\/?$/i), ref = m ? m[1] : (LLF.params().get('id') || '');
  var item = null;
  function draw(it, notes) {
    var v = it.video, s = it.save;
    document.title = (v.title || 'Ledger entry') + ' | LookLearnFind';
    var learn = it.links.learn.map(function (l) { return '<p style="margin:6px 0"><a class="link teal" href="' + esc(l.url) + '">Read the deep dive: ' + esc(l.title) + ' →</a></p>'; }).join('');
    var find = it.links.find.map(function (l) { return '<p style="margin:6px 0"><a class="link teal" href="' + esc(l.url) + '">Find it in the world: ' + esc(l.title) + ' →</a></p>'; }).join('');
    app.innerHTML = '<div data-vid="' + v.id + '" data-sid="' + s.id + '"><div class="breadcrumb"><a href="/look/">Look</a> / <a href="/look/">The Ledger</a> / ' + esc(v.ledger || 'Private') + '</div><div class="entry-page"><div>' + LLF.thumb(v) + '</div><div>' +
      '<span class="eyebrow" style="color:var(--green)">' + esc(v.ledger || 'Private') + ' &nbsp;·&nbsp; ' + esc(s.label) + (it.deep_dive ? ' &nbsp;·&nbsp; Deep dive attached' : '') + (v.illustrative ? '<span class="illus-tag">Illustrative</span>' : '') + '</span>' +
      '<h1>' + esc(v.title || 'Untitled short') + '</h1><p class="note">“' + esc(s.note) + '”</p>' +
      '<div class="cols"><div><div class="by-label">Originally posted by</div><div class="person"><strong>' + esc(v.creator_handle || v.creator_name || 'Creator not listed') + '</strong> on ' + esc(v.platform) + '</div></div>' +
      '<div><div class="by-label">Added by</div><div class="person">' + (s.saver.profile_public ? '<a href="/u/' + esc(s.saver.handle) + '/">' + esc(s.saver.display_name) + ' ↗</a>' : esc(s.saver.display_name)) + (s.saver.is_editor ? ' (editor)' : '') + ' · ' + esc(LLF.fdate(s.added_at)) + '</div></div>' +
      '<div><div class="by-label">Filed under</div><div class="person">' + esc([LLF.catLabel(s.category), s.topic_label, s.kind].filter(Boolean).join(' · ')) + '</div></div>' +
      '<div><div class="by-label">Length / language</div><div class="person">' + (v.duration != null ? LLF.dur(v.duration) : 'Length unknown') + (v.language ? ' · ' + esc(v.language.toUpperCase()) : '') + '</div></div></div>' +
      (s.threads.length ? '<div class="thread-chips">' + s.threads.map(function (t) { return '<a class="thread-chip" href="/threads/' + esc(t.slug) + '/">' + esc(t.title) + '</a>'; }).join('') + '</div>' : '') +
      '<div class="row-actions" style="flex-direction:row;flex-wrap:wrap;align-items:center;margin:22px 0">' +
      (v.illustrative ? '<span class="nolink" style="padding:12px 18px">Sample clip. No real post behind it.</span>' : (v.availability === 'ok' ? '<a class="watch" style="padding:13px 22px" href="' + esc(v.url) + '" target="_blank" rel="noopener">Watch original ↗</a>' : '<span class="dim">The original post is unavailable. This entry was last checked on ' + esc(LLF.fdate(v.last_checked)) + '.</span>')) +
      '<button class="row-save' + (it.my_save ? ' on' : '') + '" data-act="save">' + (it.my_save ? 'Saved ✓' : 'Save +') + '</button></div>' +
      (learn || find ? '<div class="look-strip" style="margin-top:0">' + learn + find + '</div>' : '<p class="small">No deep dive is attached to this clip. That does not mean it has been checked.</p>') +
      '<div class="notes-panel" style="margin-top:26px"><div class="by-label" style="margin-bottom:8px">Notes from people who saved this</div>' + notes.map(function (n) {
        return '<div class="n"><div class="who">' + esc(n.label) + ' · ' + (n.saver.profile_public ? '<a href="/u/' + esc(n.saver.handle) + '/">' + esc(n.saver.display_name) + '</a>' : esc(n.saver.display_name)) + ' · ' + esc(LLF.fdate(n.added_at)) + '</div><p>“' + esc(n.note) + '”</p></div>';
      }).join('') + (v.caption ? '<div class="cap"><b>Caption from ' + esc(v.platform) + ':</b> ' + esc(v.caption) + '</div>' : '') +
      '<div class="cap">A saved note is one person’s reason for keeping a link. It is not a fact-check. <a href="/about/how-we-work/">How we label things</a>.</div>' +
      '<details class="report"><summary>Report a problem with this entry</summary><form data-report><select name="reason"><option value="broken_link">Broken link</option><option value="wrong_attribution">Wrong attribution</option><option value="spam">Spam</option><option value="needs_context">Needs context</option><option value="other">Other</option></select><input name="detail" placeholder="Details (optional)" maxlength="300"><button class="btn sm" type="submit">Send report</button></form></details></div>' +
      '</div></div></div>';
    app.querySelector('[data-report]').onsubmit = function (e) {
      e.preventDefault(); var f = e.target;
      LLF.api('report', {body: {video_id: v.id, reason: f.reason.value, detail: f.detail.value}}).then(function () { LLF.toast('Report received. We will review the entry and its source link.'); }).catch(function (er) { LLF.toast(er.message); });
    };
  }
  LLF.me().then(function () { return LLF.api('ledger/entry?ref=' + encodeURIComponent(ref)); }).then(function (it) {
    item = it; draw(it, it.notes);
    LLF.bindRows(app, {find: function () { return item; }, reload: function () { location.reload(); }});
  }).catch(function (er) {
    app.innerHTML = '<div class="empty-state">' + esc(er.status === 404 ? 'That entry is not in the Ledger. It may be private, or it may have been removed.' : er.message) + '<div class="btns"><a class="btn" href="/look/">Back to the Ledger</a></div></div>';
  });
})();
