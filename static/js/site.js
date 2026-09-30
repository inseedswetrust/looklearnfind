/* LookLearnFind site script: nav, account link, newsletter, contact forms, and the small LLF helper used everywhere. */
(function () {
  'use strict';
  var LLF = window.LLF = window.LLF || {};
  var ESC = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'};
  LLF.esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ESC[c]; }); };
  LLF.qs = function (sel, root) { return (root || document).querySelector(sel); };
  LLF.qsa = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  LLF.csrf = null;
  LLF.api = function (path, opts) {
    opts = opts || {};
    var init = {method: opts.method || (opts.body ? 'POST' : 'GET'), credentials: 'same-origin', headers: {}};
    if (opts.body) { init.body = JSON.stringify(opts.body); init.headers['Content-Type'] = 'application/json'; }
    if (LLF.csrf) init.headers['X-CSRF'] = LLF.csrf;
    return fetch('/api/' + path, init).then(function (r) {
      return r.text().then(function (t) {
        var j = null; try { j = JSON.parse(t); } catch (e) { /* not JSON */ }
        if (!r.ok) { var err = new Error((j && j.error) || 'The Ledger is not reachable right now.'); err.status = r.status; throw err; }
        if (j === null) { var e2 = new Error('The Ledger is not reachable right now.'); e2.status = 0; throw e2; }
        return j;
      });
    });
  };
  var meP = null;
  LLF.me = function (force) {
    if (!meP || force) meP = LLF.api('me').then(function (j) { LLF.csrf = j.csrf; LLF.user = j.user; return j.user; }).catch(function () { LLF.user = null; return null; });
    return meP;
  };
  LLF.toast = function (msg) {
    var t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); t.textContent = msg; document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 3200);
  };
  LLF.params = function () { return new URLSearchParams(location.search); };

  // menu
  var btn = LLF.qs('.menu-btn'), nav = LLF.qs('#nav');
  if (btn && nav) btn.addEventListener('click', function () { var o = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', o ? 'true' : 'false'); });

  // account link
  LLF.me().then(function (u) {
    var a = LLF.qs('[data-acct]'); if (!a) return;
    if (u) { a.textContent = '@' + u.handle; a.href = '/account/'; } else { a.textContent = 'Sign in'; a.href = '/account/'; }
    if (u && u.is_editor && nav && !LLF.qs('[data-admin-link]')) {
      var x = document.createElement('a'); x.href = '/admin/'; x.textContent = 'Editors'; x.setAttribute('data-admin-link', ''); nav.insertBefore(x, a);
    }
  });

  // newsletter
  LLF.qsa('[data-newsletter]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = LLF.qs('[data-newsletter-msg]');
      LLF.api('newsletter', {body: {email: f.email.value}}).then(function () {
        msg.textContent = 'Thanks. You are on the list.'; f.reset();
      }).catch(function (er) { msg.textContent = er.message; });
    });
  });

  // contact / contribute forms
  LLF.qsa('[data-contact-form]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var box = LLF.qs('[data-form-msg]', f); var d = {kind: f.getAttribute('data-kind')};
      new FormData(f).forEach(function (v, k) { d[k] = v; });
      LLF.api('contact', {body: d}).then(function () {
        box.hidden = false; box.className = 'notice ok'; box.textContent = 'Sent. Thank you. We credit contributors and review claims before elevating them.'; f.reset();
      }).catch(function (er) { box.hidden = false; box.className = 'notice err'; box.textContent = er.message; });
    });
  });
})();
