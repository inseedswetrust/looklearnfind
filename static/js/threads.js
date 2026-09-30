/* /threads/ — append editor-approved threads that have no built page, and let signed-in people propose one. */
(function () {
  'use strict';
  var LLF = window.LLF, esc = LLF.esc, host = document.querySelector('[data-more-threads]');
  if (!host) return;
  var built = LLF.qsa('a.row[href^="/threads/"]').map(function (a) { return a.getAttribute('href'); });
  LLF.api('threads').then(function (j) {
    var extra = j.threads.filter(function (t) { return built.indexOf('/threads/' + t.slug + '/') < 0; });
    if (extra.length) host.innerHTML = '<h2 class="h3" style="margin:0 0 14px">Newly added</h2><div class="rows">' + extra.map(function (t, i) { return '<a class="row" href="/threads/' + esc(t.slug) + '/"><span class="n">' + String(i + 1).padStart(2, '0') + '</span><span class="t">' + esc(t.title) + '</span><span class="d">' + esc(t.summary || '') + '</span><span class="ar">↗</span></a>'; }).join('') + '</div>';
  }).catch(function () {});
  var btn = document.createElement('p'); btn.style.marginTop = '26px';
  btn.innerHTML = '<button class="btn ghost" data-propose>Propose a thread</button> <span class="small">Editors review every proposal.</span>';
  host.parentNode.appendChild(btn);
  btn.querySelector('button').onclick = function () {
    LLF.requireUser('Propose a thread? Create a profile first; editors review every proposal.', function () {
      var m = LLF.modal('<h2>Propose a thread</h2><p class="small" style="font-size:14px;margin-bottom:12px">A thread is one subject, such as “Tartaria” or “Home estimates”.</p><form data-f><div class="field"><label for="pt-t">Name</label><input class="input" id="pt-t" name="title" required maxlength="80"></div><div class="field"><label for="pt-s">One line on what it covers</label><input class="input" id="pt-s" name="summary" maxlength="280"></div><div class="field"><label for="pt-a">Other names people use (comma separated)</label><input class="input" id="pt-a" name="aliases"></div><div class="notice err" data-err hidden></div><button class="btn" type="submit">Send to editors</button></form>');
      var f = m.querySelector('[data-f]');
      f.onsubmit = function (e) {
        e.preventDefault();
        LLF.api('threads/propose', {body: {title: f.title.value, summary: f.summary.value, aliases: f.aliases.value.split(',')}}).then(function () { m.close(); LLF.toast('Sent. Editors will take a look.'); }).catch(function (er) { var x = m.querySelector('[data-err]'); x.hidden = false; x.textContent = er.message; });
      };
    });
  };
})();
