(function () {
  var sel = document.getElementById('compare-select');
  var btn = document.getElementById('compare-btn');
  var out = document.getElementById('compare-results');
  if (!sel || !btn || !out || typeof DRIVERS === 'undefined') return;

  DRIVERS.sort(function (a, b) { return a.name.localeCompare(b.name); });
  DRIVERS.forEach(function (d) {
    var opt = document.createElement('option');
    opt.value = d.slug;
    opt.textContent = d.name;
    sel.appendChild(opt);
  });

  function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

  function getVal(d, key) {
    if (['cup', 'xfinity', 'truck'].indexOf(key) !== -1) {
      var s = d.by_series && d.by_series[key];
      return s ? s : null;
    }
    return d.total ? d.total[key] : null;
  }

  function render() {
    var selected = Array.prototype.slice.call(sel.selectedOptions);
    if (selected.length < 2 || selected.length > 3) {
      out.innerHTML = '<p style="color:#746c5c">Select 2 or 3 drivers and click Compare.</p>';
      return;
    }
    var slugs = selected.map(function (o) { return o.value; });
    var drivers = slugs.map(function (slug) { return DRIVERS.filter(function (x) { return x.slug === slug; })[0]; });
    var names = drivers.map(function (d) { return d.name; });
    var headerCells = names.map(function (n) { return '<th>' + esc(n) + '</th>'; }).join('');

    function row(label, key, fmt) {
      var cells = ['<td class="cmp-label">' + label + '</td>'];
      drivers.forEach(function (d) {
        var v = getVal(d, key);
        if (fmt && v != null) v = fmt(v);
        cells.push('<td class="num">' + (v != null ? v : '-') + '</td>');
      });
      return '<tr>' + cells.join('') + '</tr>';
    }

    var totalRows = '';
    totalRows += row('Starts', 'starts');
    totalRows += row('Wins', 'wins');
    totalRows += row('Top 5s', 'top5');
    totalRows += row('Top 10s', 'top10');
    totalRows += row('Avg Finish', 'avg_f');
    totalRows += row('Poles', 'poles');
    totalRows += row('Points', 'points');

    var html = '<div class="panel"><h2>Career Totals</h2><div class="body"><table class="data"><thead><tr><th>Stat</th>' + headerCells + '</tr></thead><tbody>' + totalRows + '</tbody></table></div></div>';

    ['cup', 'xfinity', 'truck'].forEach(function (s) {
      var srows = '';
      var sdrivers = drivers.map(function (d) {
        var bs = d.by_series && d.by_series[s];
        var r = { total: bs };
        function sg(key) { return bs ? bs[key] : null; }
        return {
          name: d.name,
          total: { starts: sg('starts'), wins: sg('wins'), top5: sg('top5'), top10: sg('top10'), avg_f: sg('avg_f'), poles: sg('poles'), points: sg('points') }
        };
      });

      function srow(label, key, fmt) {
        var cells = ['<td class="cmp-label">' + label + '</td>'];
        sdrivers.forEach(function (sd) {
          var v = sd.total ? sd.total[key] : null;
          if (fmt && v != null) v = fmt(v);
          cells.push('<td class="num">' + (v != null ? v : '-') + '</td>');
        });
        return '<tr>' + cells.join('') + '</tr>';
      }

      srows += srow('Starts', 'starts');
      srows += srow('Wins', 'wins');
      srows += srow('Top 5s', 'top5');
      srows += srow('Top 10s', 'top10');
      srows += srow('Avg Finish', 'avg_f');
      srows += srow('Poles', 'poles');
      srows += srow('Points', 'points');

      if (sdrivers.some(function (sd) { return sd.total.starts; })) {
        html += '<div class="panel"><h2>' + COMPARE_SERIES[s] + '</h2><div class="body"><table class="data"><thead><tr><th>Stat</th>' + headerCells + '</tr></thead><tbody>' + srows + '</tbody></table></div></div>';
      }
    });

    out.innerHTML = html;
  }

  btn.addEventListener('click', render);
  sel.addEventListener('dblclick', render);
})();
