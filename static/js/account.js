/* /account/ — sign in, create a profile, reset password; then profile settings, collections, following, export. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, app = document.getElementById('account-app');
  if (!app) return;
  var P = LLF.params();

  function authView(mode) {
    var su = mode === 'signup', rq = mode === 'reset-request', rs = mode === 'reset';
    var title = su ? 'Start your Ledger.' : rq ? 'Reset your password.' : rs ? 'Choose a new password.' : 'Welcome back.';
    var sub = su ? 'Create a profile to save links, keep notes, and follow other people’s finds. Saves are private unless you choose otherwise.' : rq ? 'We will email you a link that works for an hour.' : rs ? '' : 'Sign in to your Ledger.';
    app.innerHTML = '<div class="kicker">Account<i></i></div><h1 class="display" style="font-size:clamp(40px,6vw,64px);margin-bottom:12px">' + title + '</h1><p class="dek" style="margin-bottom:24px;font-size:17px">' + sub + '</p>' +
      '<form class="form-card" data-f>' +
      (rs ? '' : '<div class="field"><label for="ac-e">Email</label><input class="input" id="ac-e" name="email" type="email" required autocomplete="email"></div>') +
      (su ? '<div class="two"><div class="field"><label for="ac-h">Handle</label><input class="input" id="ac-h" name="handle" required pattern="[A-Za-z0-9_]{3,24}" autocomplete="username"><div class="hint">3 to 24 letters, numbers, or underscores.</div></div><div class="field"><label for="ac-n">Display name</label><input class="input" id="ac-n" name="display_name" autocomplete="name"></div></div>' : '') +
      (rq ? '' : '<div class="field"><label for="ac-p">' + (rs ? 'New password' : 'Password') + '</label><input class="input" id="ac-p" name="password" type="password" required minlength="8" autocomplete="' + (su || rs ? 'new-password' : 'current-password') + '"></div>') +
      '<div class="notice err" data-err hidden></div><div class="notice ok" data-ok hidden></div>' +
      '<button class="btn" type="submit">' + (su ? 'Create profile' : rq ? 'Email me a link' : rs ? 'Set password' : 'Sign in') + '</button>' +
      '<p class="small" style="margin-top:14px">' + (su ? '<a href="?mode=signin">I already have an account</a>' : rq || rs ? '<a href="?mode=signin">Back to sign in</a>' : '<a href="?mode=signup">Create a profile</a> · <a href="?mode=reset-request">Forgot password?</a>') + '</p></form>';
    var f = app.querySelector('[data-f]');
    f.onsubmit = function (e) {
      e.preventDefault();
      var d = {}; new FormData(f).forEach(function (v, k) { d[k] = v; });
      var path = su ? 'auth/signup' : rq ? 'auth/reset-request' : rs ? 'auth/reset' : 'auth/login';
      if (rs) d.token = P.get('reset');
      LLF.api(path, {body: d}).then(function (j) {
        if (rq) { var o = app.querySelector('[data-ok]'); o.hidden = false; o.textContent = 'If that email has an account, a reset link is on its way.'; if (j.dev_link) o.innerHTML += ' <a href="' + esc(j.dev_link) + '">(dev link)</a>'; return; }
        LLF.csrf = j.csrf; LLF.user = j.user;
        var next = P.get('next'); if (next && next.charAt(0) === '/' && next.charAt(1) !== '/') location.href = next; else { history.replaceState(null, '', '/account/'); home(j.user); }
      }).catch(function (er) { var x = app.querySelector('[data-err]'); x.hidden = false; x.textContent = er.message; });
    };
  }

  function home(u) {
    LLF.siteData().then(function (sd) {
      LLF.api('following').then(function (fj) {
        app.innerHTML = '<div class="kicker">Account<i></i></div><h1 class="display" style="font-size:clamp(40px,6vw,64px);margin-bottom:10px">Hello, ' + esc(u.display_name) + '.</h1>' +
          '<p class="dek" style="font-size:17px;margin-bottom:26px"><a class="btn" href="/look/?mode=mine">Open My Ledger</a> <a class="btn ghost" href="/look/add/">+ Add a post</a> ' + (u.profile_public ? '<a class="btn ghost" href="/u/' + esc(u.handle) + '/">My public profile ↗</a>' : '') + '</p>' +
          '<div class="tabs" role="tablist" style="max-width:720px"><button class="sel" data-t="profile">Profile</button><button data-t="collections">Collections</button><button data-t="following">Following</button><button data-t="data">Your data</button></div><div data-pane></div>';
        function pane(t) {
          LLF.qsa('[data-t]', app).forEach(function (b) { b.classList.toggle('sel', b.dataset.t === t); });
          var box = app.querySelector('[data-pane]');
          if (t === 'profile') {
            box.innerHTML = '<form class="form-card" style="max-width:720px" data-pf><div class="field"><label for="p-n">Display name</label><input class="input" id="p-n" name="display_name" value="' + esc(u.display_name) + '" maxlength="60"></div>' +
              '<div class="field"><label for="p-b">About you</label><textarea class="input" id="p-b" name="bio" maxlength="400">' + esc(u.bio) + '</textarea></div>' +
              '<div class="field"><label for="p-l">What do you tend to look for?</label><input class="input" id="p-l" name="looks_for" value="' + esc(u.looks_for) + '" maxlength="240" placeholder="e.g. Candidate forums, weeknight cooking, ingredient lists"></div>' +
              '<div class="field"><label>Topics of interest</label><div class="radio-row">' + sd.topics.map(function (t) { return '<label><input type="checkbox" name="interests" value="' + t.slug + '"' + (u.interests.indexOf(t.slug) >= 0 ? ' checked' : '') + '><span>' + esc(t.label) + '</span></label>'; }).join('') + '</div></div>' +
              '<div class="field"><label>Profile</label><div class="radio-row"><label><input type="radio" name="profile_public" value="0"' + (u.profile_public ? '' : ' checked') + '><span>Private</span></label><label><input type="radio" name="profile_public" value="1"' + (u.profile_public ? ' checked' : '') + '><span>Public</span></label></div><div class="hint">Your private saves are visible only to you. A public profile shows your display name, bio, and the saves you deliberately made public. Going private removes your public saves from the Ledger.</div></div>' +
              '<div class="notice ok" data-ok hidden></div><button class="btn" type="submit">Save profile</button> <button type="button" class="btn ghost" data-out>Sign out</button></form>';
            var f = box.querySelector('[data-pf]');
            f.onsubmit = function (e) {
              e.preventDefault();
              var d = {display_name: f.display_name.value, bio: f.bio.value, looks_for: f.looks_for.value, profile_public: f.profile_public.value === '1', interests: LLF.qsa('[name=interests]:checked', f).map(function (x) { return x.value; })};
              if (u.profile_public && !d.profile_public && !confirm('Going private removes your public saves from the Ledger. Continue?')) return;
              LLF.api('profile/update', {body: d}).then(function (j) { u = j.user; LLF.user = u; var o = f.querySelector('[data-ok]'); o.hidden = false; o.textContent = 'Saved.'; }).catch(function (er) { LLF.toast(er.message); });
            };
            box.querySelector('[data-out]').onclick = function () { LLF.api('auth/logout', {body: {}}).then(function () { location.href = '/'; }); };
          } else if (t === 'collections') {
            box.innerHTML = '<div style="max-width:720px"><p class="small" style="margin-bottom:14px">Collections are ordered sets of your saves. A public collection shows only saves that are already public.</p>' +
              (u.collections.length ? '<table class="plain"><tr><th>Title</th><th>Visibility</th><th></th></tr>' + u.collections.map(function (c) { return '<tr><td><a href="/look/?mode=mine&collection=' + c.id + '">' + esc(c.title) + '</a></td><td>' + c.visibility + '</td><td><button class="btn sm ghost" data-tog="' + c.id + '" data-v="' + (c.visibility === 'public' ? 'private' : 'public') + '">Make ' + (c.visibility === 'public' ? 'private' : 'public') + '</button> <button class="btn sm danger" data-delc="' + c.id + '">Delete</button></td></tr>'; }).join('') + '</table>' : '<p>No collections yet.</p>') +
              '<form class="form-card" style="margin-top:20px" data-cf><div class="field"><label for="c-t">New collection</label><input class="input" id="c-t" name="title" required maxlength="80" placeholder="e.g. Midterms worth checking"></div><div class="field"><label for="c-p">One-line premise</label><input class="input" id="c-p" name="premise" maxlength="240"></div><div class="radio-row" style="margin-bottom:14px"><label><input type="radio" name="visibility" value="private" checked><span>Private</span></label><label><input type="radio" name="visibility" value="public"><span>Public</span></label></div><button class="btn" type="submit">Create</button></form></div>';
            box.querySelector('[data-cf]').onsubmit = function (e) { e.preventDefault(); var f = e.target; LLF.api('collections/create', {body: {title: f.title.value, premise: f.premise.value, visibility: f.visibility.value}}).then(function () { LLF.me(true).then(function (nu) { u = nu; pane('collections'); }); }).catch(function (er) { LLF.toast(er.message); }); };
            LLF.qsa('[data-tog]', box).forEach(function (b) { b.onclick = function () { LLF.api('collections/update', {body: {id: +b.dataset.tog, visibility: b.dataset.v}}).then(function () { LLF.me(true).then(function (nu) { u = nu; pane('collections'); }); }).catch(function (er) { LLF.toast(er.message); }); }; });
            LLF.qsa('[data-delc]', box).forEach(function (b) { b.onclick = function () { if (confirm('Delete this collection? Your saves stay.')) LLF.api('collections/delete', {body: {id: +b.dataset.delc}}).then(function () { LLF.me(true).then(function (nu) { u = nu; pane('collections'); }); }); }; });
          } else if (t === 'following') {
            box.innerHTML = '<div style="max-width:720px">' + (fj.following.length ? '<table class="plain"><tr><th>Profile</th><th></th></tr>' + fj.following.map(function (f) { return '<tr><td><a href="/u/' + esc(f.handle) + '/">' + esc(f.display_name) + '</a> <span class="small">@' + esc(f.handle) + '</span>' + (f.muted ? ' <span class="status">Muted</span>' : '') + '</td><td><button class="btn sm ghost" data-mute="' + esc(f.handle) + '" data-m="' + (f.muted ? '0' : '1') + '">' + (f.muted ? 'Unmute' : 'Mute') + '</button> <button class="btn sm danger" data-unf="' + esc(f.handle) + '">Unfollow</button></td></tr>'; }).join('') + '</table>' : '<div class="empty-state" style="margin:0">Your Following shelf is quiet. Find someone whose eye you trust, then their public saves will appear here in time order. <div class="btns"><a class="btn" href="/look/">Explore the Ledger</a></div></div>') + '<p class="small" style="margin-top:14px">Muting hides a profile from your Following feed without unfollowing. It never changes the public Ledger.</p></div>';
            LLF.qsa('[data-mute]', box).forEach(function (b) { b.onclick = function () { LLF.api('mute', {body: {handle: b.dataset.mute, muted: b.dataset.m === '1'}}).then(function () { LLF.api('following').then(function (x) { fj = x; pane('following'); }); }); }; });
            LLF.qsa('[data-unf]', box).forEach(function (b) { b.onclick = function () { LLF.api('unfollow', {body: {handle: b.dataset.unf}}).then(function () { LLF.api('following').then(function (x) { fj = x; pane('following'); }); }); }; });
          } else {
            box.innerHTML = '<div style="max-width:720px"><p>Your archive is yours to keep. Export every save, private and public, with your notes.</p><p style="margin:14px 0"><a class="btn" href="/api/export?format=json">Download JSON</a> <a class="btn ghost" href="/api/export?format=csv">Download CSV</a></p><p class="small">Your private saves are visible only to you. See the <a href="/privacy/">privacy page</a>.</p></div>';
          }
        }
        LLF.qsa('[data-t]', app).forEach(function (b) { b.onclick = function () { pane(b.dataset.t); }; });
        pane('profile');
      });
    });
  }

  LLF.me().then(function (u) {
    if (P.get('reset')) return authView('reset');
    if (u) return home(u);
    authView(P.get('mode') || 'signin');
  });
})();
