/* LookLearnFind election pages: chart tabs only. Pages are complete without JavaScript. */
(function () {
  document.querySelectorAll('[data-tabs]').forEach(function (wrap) {
    var tabs = wrap.querySelectorAll('[role=tab]');
    var panes = wrap.querySelectorAll('[data-p]');
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        tabs.forEach(function (x) { x.setAttribute('aria-selected', x === t ? 'true' : 'false'); });
        panes.forEach(function (p) { p.hidden = p.getAttribute('data-p') !== t.getAttribute('data-t'); });
      });
    });
  });
})();
