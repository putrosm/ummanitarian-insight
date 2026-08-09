/* Ummanitarian Insight — client-side search (generated feature)
   Reads /search-index.json, filters by title/deck/category/date. */
(function () {
  var input = document.getElementById('search-input');
  if (!input) return;
  var box = document.getElementById('search-results');
  var idx = null;

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function load() {
    return fetch('/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (d) { idx = d; })
      .catch(function () {});
  }
  function render(q) {
    q = q.trim().toLowerCase();
    if (q.length < 2 || !idx) { box.classList.remove('open'); return; }
    var hits = idx.filter(function (e) {
      return (e.title + ' ' + e.deck + ' ' + e.category + ' ' + (e.date || '')).toLowerCase().indexOf(q) !== -1;
    }).slice(0, 12);
    if (!hits.length) {
      box.innerHTML = '<div class="search-empty">No matching insights.</div>';
      box.classList.add('open');
      return;
    }
    box.innerHTML = hits.map(function (e) {
      return '<a class="search-result" href="' + esc(e.url) + '">' +
        '<div class="sr-cat">' + esc(e.category) + '</div>' +
        '<div class="sr-title">' + esc(e.title) + '</div>' +
        (e.deck ? '<div class="sr-deck">' + esc(e.deck) + '</div>' : '') +
        '</a>';
    }).join('');
    box.classList.add('open');
  }
  input.addEventListener('input', function () { render(input.value); });
  input.addEventListener('focus', function () { render(input.value); });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.header-search')) box.classList.remove('open');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') box.classList.remove('open');
  });
  load();
})();
