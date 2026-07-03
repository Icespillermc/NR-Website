(function () {
  function cellValue(row, idx) {
    var cell = row.children[idx];
    if (!cell) return null;
    var text = cell.textContent.trim();
    if (text === '' || text === '-') return null;
    var numText = text.replace(/,/g, '');
    if (/^-?\d+(\.\d+)?$/.test(numText)) return parseFloat(numText);
    return text.toLowerCase();
  }

  function sortByColumn(table, colIndex, th) {
    var tbody = table.tBodies[0];
    if (!tbody) return;
    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
    var dir = th.getAttribute('data-sort-dir') === 'asc' ? 'desc' : 'asc';
    table.querySelectorAll('thead th').forEach(function (h) {
      h.removeAttribute('data-sort-dir');
      h.classList.remove('sort-asc', 'sort-desc');
    });
    th.setAttribute('data-sort-dir', dir);
    th.classList.add(dir === 'asc' ? 'sort-asc' : 'sort-desc');

    var mult = dir === 'asc' ? 1 : -1;
    rows.sort(function (a, b) {
      var av = cellValue(a, colIndex), bv = cellValue(b, colIndex);
      if (av === null && bv === null) return 0;
      if (av === null) return 1;
      if (bv === null) return -1;
      if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * mult;
      return String(av).localeCompare(String(bv)) * mult;
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
  }

  function init() {
    document.querySelectorAll('table.data').forEach(function (table) {
      var thead = table.tHead;
      if (!thead) return;
      thead.querySelectorAll('th').forEach(function (th, idx) {
        th.classList.add('sortable');
        th.addEventListener('click', function () { sortByColumn(table, idx, th); });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
