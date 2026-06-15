document.addEventListener('DOMContentLoaded', function () {

  /* ── Footer year ──────────────────────────────────────── */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ── Article slider (homepage only) ───────────────────── */
  var viewport  = document.getElementById('sliderViewport');
  var track     = document.getElementById('sliderTrack');
  var btnPrev   = document.getElementById('btnPrev');
  var btnNext   = document.getElementById('btnNext');
  var counter   = document.getElementById('sliderCounter');
  var nav       = document.getElementById('sliderNav');

  if (!viewport || !track) return;

  var cards   = Array.from(track.querySelectorAll('.article-card'));
  var total   = cards.length;
  var VISIBLE = 5;
  var current = 0;          /* index of the topmost visible card */

  /* Height of a single card (set in CSS as height: 116px) */
  function cardH() {
    return cards[0] ? cards[0].offsetHeight : 116;
  }

  /* How many cards can still scroll down */
  function maxIndex() {
    return Math.max(0, total - VISIBLE);
  }

  /* Update counter label */
  function updateCounter() {
    if (!counter || total <= VISIBLE) return;
    var last = Math.min(current + VISIBLE, total);
    counter.textContent = (current + 1) + '–' + last + ' of ' + total;
  }

  /* Apply transform and button states */
  function slideTo(index) {
    current = Math.max(0, Math.min(index, maxIndex()));
    track.style.transform = 'translateY(-' + (current * cardH()) + 'px)';
    if (btnPrev) btnPrev.disabled = current === 0;
    if (btnNext) btnNext.disabled = current >= maxIndex();
    updateCounter();
  }

  /* Set viewport height to show exactly VISIBLE cards (or fewer) */
  function setHeight() {
    var h = cardH();
    if (h > 0) {
      viewport.style.height = (Math.min(total, VISIBLE) * h) + 'px';
    }
  }

  /* Hide nav entirely if all articles fit in the window */
  if (nav && total <= VISIBLE) {
    nav.style.visibility = 'hidden';
  }

  if (btnPrev) btnPrev.addEventListener('click', function () { slideTo(current - 1); });
  if (btnNext) btnNext.addEventListener('click', function () { slideTo(current + 1); });

  /* Re-measure on resize (e.g. font scaling, orientation change) */
  window.addEventListener('resize', function () {
    setHeight();
    slideTo(current);
  });

  setHeight();
  slideTo(0);

  /* ── External link click tracking ─────────────────────── */
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a[data-track="external"]');
    if (!link || typeof gtag !== 'function') return;
    gtag('event', 'external_link_click', {
      link_url:  link.getAttribute('href'),
      link_text: link.getAttribute('data-title')
    });
  });
});
