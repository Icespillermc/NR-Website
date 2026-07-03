(function () {
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  if (!input || !results || typeof SEARCH_DATA === 'undefined') return;

  var base = input.closest('.wrap').querySelector('.brand').getAttribute('href').replace('index.html', '');

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function render(items) {
    results.innerHTML = '';
    if (!items.length) {
      results.style.display = 'none';
      return;
    }
    items.forEach(function (item) {
      var a = document.createElement('a');
      a.href = base + item.path;
      a.className = 'search-result-item';
      a.innerHTML = '<span class="sri-label">' + esc(item.name) + '</span><span class="sri-type">' + esc(item.type) + '</span>';
      results.appendChild(a);
    });
    results.style.display = 'block';
  }

  function query(q) {
    q = q.toLowerCase().trim();
    if (!q || q.length < 1) { results.style.display = 'none'; return; }
    var out = [];
    var cats = {'drivers': 'Driver', 'teams': 'Team', 'tracks': 'Track', 'pages': 'Page'};
    Object.keys(cats).forEach(function (key) {
      (SEARCH_DATA[key] || []).forEach(function (item) {
        if (item.name.toLowerCase().indexOf(q) !== -1) {
          out.push({ name: item.name, type: cats[key], path: key + '/' + item.slug + '.html' });
        }
      });
    });
    out.sort(function (a, b) {
      var ai = a.name.toLowerCase().indexOf(q);
      var bi = b.name.toLowerCase().indexOf(q);
      if (ai !== bi) return ai - bi;
      return a.name.length - b.name.length;
    });
    render(out.slice(0, 15));
  }

  input.addEventListener('input', function () {
    query(input.value);
  });

  input.addEventListener('blur', function () {
    setTimeout(function () { results.style.display = 'none'; }, 200);
  });

  input.addEventListener('focus', function () {
    if (input.value.trim()) query(input.value);
  });

  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      input.focus();
    }
  });
})();
