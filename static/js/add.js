/* /look/add/ — paste a link, confirm what we found, say why it was worth keeping, choose private or public. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, app = document.getElementById('add-app');
  if (!app) return;
  var pv = null, tp = null, sd = null;

  function shell(step, inner) {
    app.innerHTML = '<div class="add-card"><div class="kicker">Look / The Ledger<i></i></div><h1 class="display" style="font-size:clamp(40px,6vw,64px)">Put one in the Ledger.</h1><p class="dek" style="margin:14px 0 24px">Paste the link. Tell us what made you stop. One sentence is enough.</p>' +
      '<div class="steps">' + ['1 Link', '2 What we found', '3 Why it stayed', '4 Who sees it'].map(function (x, i) { return '<span class="' + (i + 1 <= step ? 'on' : '') + '">' + x + '</span>'; }).join('') + '</div>' + inner + '</div>';
  }
  function needSignin() {
    shell(1, '<div class="empty-state">Sign in or create a profile to save links. Saves are private until you choose to share them.<div class="btns"><button class="btn" data-si>Create a profile</button><button class="btn ghost" data-si>Sign in</button></div></div>');
    app.querySelector('[data-si]').onclick = app.querySelectorAll('[data-si]')[1].onclick = function () { LLF.authModal(null, function () { LLF.me(true).then(start); }); };
  }
  function start() {
    LLF.me().then(function (u) {
      if (!u) return needSignin();
      LLF.siteData().then(function (d) { sd = d; step1(LLF.params().get('url') || ''); if (LLF.params().get('url')) check(LLF.params().get('url')); });
    });
  }
  function step1(val) {
    shell(1, '<form data-f1><div class="field"><label for="a-url">Link to a short video</label><input class="input" id="a-url" name="url" type="url" inputmode="url" placeholder="https://www.youtube.com/shorts/…" value="' + esc(val) + '" required><div class="hint">YouTube Shorts and videos, Instagram Reels, and TikTok. We link to the original; we never host the video.</div></div><div class="notice err" data-err hidden></div><button class="btn" type="submit">Check the link</button></form>');
    app.querySelector('[data-f1]').onsubmit = function (e) { e.preventDefault(); check(e.target.url.value); };
  }
  function check(url) {
    var b = app.querySelector('[data-f1] button'); if (b) { b.disabled = true; b.textContent = 'Checking…'; }
    LLF.api('ledger/preview', {body: {url: url}}).then(function (j) { pv = j; pv.url = url; step2(); }).catch(function (er) {
      step1(url); var x = app.querySelector('[data-err]'); x.hidden = false; x.textContent = er.message;
    });
  }
  function src(v, k) { return v.field_src && v.field_src[k] ? '<span class="src-tag ' + (v.field_src[k] === 'human' ? 'human' : '') + '">' + (v.field_src[k] === 'human' ? 'Added by a person' : 'From ' + esc(v.platform.split(' ')[0])) + '</span>' : ''; }
  function step2() {
    var v = pv.video, miss = pv.missing || [];
    var dup = pv.duplicate;
    var box = '<div class="preview-box">' + LLF.thumb(v) + '<dl><dt>Platform</dt><dd>' + esc(v.platform) + '</dd><dt>Title</dt><dd>' + (v.title ? esc(v.title) + src(v, 'title') : '<em>Not found</em>') + '</dd><dt>Original creator</dt><dd>' + (v.creator_handle ? esc(v.creator_handle) + src(v, 'creator_handle') : '<em>Not found</em>') + '</dd><dt>Length</dt><dd>' + (v.duration != null ? LLF.dur(v.duration) + src(v, 'duration_sec') : 'Length unknown') + '</dd></dl></div>';
    var notice = dup ? '<div class="notice ok"><b>This video is already here.</b> Save it to your Ledger and add your own note.' + (pv.in_index ? ' <a href="/look/L-' + v.ledger_no + '/">See the entry →</a>' : '') + '</div>' : '';
    if (pv.unavailable) notice += '<div class="notice err">The original post looks unavailable. You can still save the link, and an editor will check it.</div>';
    if (!dup && !pv.metadata_found) notice += '<div class="notice">We could not read details from ' + esc(v.platform.split(' ')[0]) + '. That is normal for some platforms. Fill in what you know below; it is saved as added by a person.</div>';
    var fill = '';
    if (miss.indexOf('title') >= 0) fill += '<div class="field"><label for="a-title">Title or short description</label><input class="input" id="a-title" name="title" maxlength="200"></div>';
    if (miss.indexOf('creator_handle') >= 0) fill += '<div class="field"><label for="a-cr">Original creator’s handle</label><input class="input" id="a-cr" name="creator_handle" placeholder="@handle" maxlength="60"><div class="hint">The person who posted it. This is different from you, the person who saved it.</div></div>';
    if (miss.indexOf('duration') >= 0) fill += '<div class="field"><label for="a-dur">Length, if you know it</label><input class="input" id="a-dur" name="duration" placeholder="0:48"><div class="hint">Leave blank rather than guess.</div></div>';
    var topicOpts = sd.categories.map(function (c) { return '<optgroup label="' + esc(c.label) + '">' + sd.topics.filter(function (t) { return t.category === c.slug; }).map(function (t) { return '<option value="' + t.slug + '">' + esc(t.label) + '</option>'; }).join('') + '</optgroup>'; }).join('');
    var mine = pv.my_save;
    shell(2, box + notice + '<form data-f2>' + fill +
      '<div class="two"><div class="field"><label for="a-topic">Topic</label><select class="select" id="a-topic" name="topic" required><option value="">Choose one</option>' + topicOpts + '</select></div>' +
      '<div class="field"><label for="a-lang">Language</label><select class="select" id="a-lang" name="language"><option value="en">English</option><option value="es">Spanish</option><option value="">Other / unknown</option></select></div></div>' +
      '<div class="field"><label>Kind of post</label><div class="radio-row">' + sd.kinds.map(function (k, i) { return '<label><input type="radio" name="kind" value="' + esc(k) + '"' + (i === 0 ? ' required' : '') + '><span>' + esc(k) + '</span></label>'; }).join('') + '</div></div>' +
      '<div class="field"><label for="a-note">Why was this worth keeping?</label><textarea class="input" id="a-note" name="note" maxlength="600" placeholder="One or two sentences. What made you stop?"></textarea></div>' +
      '<div class="field"><label>Thread (optional)</label><div data-tp></div></div>' +
      '<div class="field"><label>Who sees it</label><div class="radio-row"><label><input type="radio" name="visibility" value="private" checked><span>Keep private</span></label><label><input type="radio" name="visibility" value="public"><span>Submit to public Ledger</span></label></div><div class="hint">Private saves are visible only to you. Public additions are reviewed first, and appear with your profile and note.</div></div>' +
      '<div class="notice err" data-err hidden></div><button class="btn" type="submit">' + (mine ? 'Update my save' : 'Save') + '</button> <a class="btn ghost" href="/look/add/">Start over</a></form>');
    tp = LLF.threadPicker(app.querySelector('[data-tp]'), []);
    var f = app.querySelector('[data-f2]');
    f.onsubmit = function (e) {
      e.preventDefault();
      var d = {url: pv.url};
      new FormData(f).forEach(function (val, k) { d[k] = val; });
      var t = tp.get(); d.threads = t.threads; d.propose_threads = t.propose;
      function go() {
        LLF.api('ledger/save', {body: d}).then(function (j) { done(j, d.visibility); }).catch(function (er) {
          if (er.status === 409 && er.message.indexOf('profile') >= 0) { if (confirm('Public saves appear with your public profile. Turn it on and submit?')) { d.make_profile_public = true; go(); } return; }
          var x = f.querySelector('[data-err]'); x.hidden = false; x.textContent = er.message;
        });
      }
      go();
    };
  }
  function done(j, vis) {
    var msg = vis === 'private' ? 'Saved privately. It is in <a href="/look/?mode=mine">My Ledger</a>, where you can add it to the public Ledger any time.' :
      (j.status === 'approved' ? 'Added to the public Ledger.' : 'Submitted. Your link will appear publicly after review; it is already saved for you.');
    shell(4, '<div class="notice ok">' + msg + '</div><p style="margin-top:18px"><a class="btn" href="/look/?mode=mine">Open My Ledger</a> <a class="btn ghost" href="/look/add/">Add another</a>' + (j.entry && j.entry.video.ledger_no ? ' <a class="btn ghost" href="/look/L-' + String(j.entry.video.ledger_no).padStart(3, '0') + '/">See the entry</a>' : '') + '</p>');
  }
  start();
})();
