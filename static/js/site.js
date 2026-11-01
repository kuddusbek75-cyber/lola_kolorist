// Время: пользователь печатает цифры, двоеточие ставится само (1430 -> 14:30)
document.querySelectorAll('[data-time-mask]').forEach(function (el) {
  el.addEventListener('input', function () {
    var d = el.value.replace(/\D/g, '').slice(0, 4);
    el.value = d.length > 2 ? d.slice(0, 2) + ':' + d.slice(2) : d;
  });
});
// Плавное появление блоков при прокрутке
var items = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.15 });
  items.forEach(function (el) { io.observe(el); });
} else {
  items.forEach(function (el) { el.classList.add('in'); });
}
