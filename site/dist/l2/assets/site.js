/* Хурмыч: таймеры обновлений/профилактик + поиск по гайдам */
(function () {
  var MSK = 3 * 60 * 60 * 1000;

  function fmt(ms) {
    if (ms < 0) ms = 0;
    var s = Math.floor(ms / 1000);
    var d = Math.floor(s / 86400); s -= d * 86400;
    var h = Math.floor(s / 3600); s -= h * 3600;
    var m = Math.floor(s / 60); s -= m * 60;
    if (d > 0) return d + ' д ' + h + ' ч ' + m + ' мин';
    if (h > 0) return h + ' ч ' + m + ' мин ' + s + ' с';
    return m + ' мин ' + s + ' с';
  }

  function nextMaintenance(now) {
    // среда 10:00 МСК = среда 07:00 UTC
    var t = new Date(now.getTime() + now.getTimezoneOffset() * 60000 + MSK); // "как будто МСК"
    var day = t.getDay();               // 0 вс ... 3 ср
    var delta = (3 - day + 7) % 7;
    var cand = new Date(t.getFullYear(), t.getMonth(), t.getDate() + delta, 10, 0, 0);
    if (delta === 0 && cand.getTime() <= t.getTime()) cand.setDate(cand.getDate() + 7);
    return cand.getTime() - MSK - now.getTimezoneOffset() * 60000;
  }

  function tick() {
    var now = new Date();
    document.querySelectorAll('[data-maint]').forEach(function (el) {
      var v = el.querySelector('.cdv');
      if (v) v.textContent = fmt(nextMaintenance(now));
    });
    document.querySelectorAll('[data-date]').forEach(function (el) {
      var v = el.querySelector('.cdv');
      if (!v) return;
      // дата трактуется как МСК 10:00
      var local = new Date(el.getAttribute('data-date') + ':00+03:00');
      v.textContent = fmt(local.getTime() - now.getTime());
    });
  }
  tick();
  setInterval(tick, 1000);

  // поиск по карточкам гайдов
  var q = document.getElementById('q');
  if (q) {
    q.addEventListener('input', function () {
      var s = q.value.trim().toLowerCase();
      document.querySelectorAll('#cards .card').forEach(function (c) {
        c.style.display = (!s || c.textContent.toLowerCase().indexOf(s) !== -1) ? '' : 'none';
      });
    });
  }
})();
