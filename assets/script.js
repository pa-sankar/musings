document.addEventListener('DOMContentLoaded', function () {

  /* ── Footer year ──────────────────────────────────────── */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ── External link click tracking (homepage cards) ────── */
  document.addEventListener('click', function (e) {
    var link = e.target.closest('a[data-track="external"]');
    if (!link || typeof gtag !== 'function') return;
    gtag('event', 'external_link_click', {
      link_url:  link.getAttribute('href'),
      link_text: link.getAttribute('data-title')
    });
  });

  /* ── "You're leaving" confirm + tracking (in-article links) ──
     Applies to every external "Curious? Read further here" link
     inside .article-body, on every article page, with no per-page
     markup needed — it targets target="_blank" links generically. */
  (function () {
    var modal = null;

    function buildModal() {
      modal = document.createElement('div');
      modal.className = 'leaving-modal';
      modal.innerHTML =
        '<div class="leaving-modal-box" role="dialog" aria-modal="true" aria-label="Leaving this site">' +
          '<p class="leaving-modal-text">You\'re about to leave <strong>Musings of an Indian</strong> for <span class="leaving-modal-host"></span>.</p>' +
          '<div class="leaving-modal-actions">' +
            '<button type="button" class="btn btn--secondary leaving-modal-cancel">Stay here</button>' +
            '<a href="#" target="_blank" rel="noopener noreferrer" class="btn btn--primary leaving-modal-continue">Continue</a>' +
          '</div>' +
        '</div>';
      document.body.appendChild(modal);

      modal.querySelector('.leaving-modal-cancel').addEventListener('click', closeModal);
      modal.addEventListener('click', function (e) {
        if (e.target === modal) closeModal();
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeModal();
      });
    }

    function closeModal() {
      if (modal) modal.classList.remove('is-open');
    }

    function openModal(link) {
      if (!modal) buildModal();

      var url = link.getAttribute('href');
      var host = 'an external site';
      try { host = new URL(url, window.location.href).hostname.replace(/^www\./, ''); } catch (err) {}

      modal.querySelector('.leaving-modal-host').textContent = host;

      var continueBtn = modal.querySelector('.leaving-modal-continue');
      continueBtn.setAttribute('href', url);
      continueBtn.onclick = function () {
        if (typeof gtag === 'function') {
          gtag('event', 'external_link_click', {
            link_url:      url,
            link_text:     (link.textContent || '').trim(),
            link_location: 'article_body'
          });
        }
        closeModal();
      };

      modal.classList.add('is-open');
    }

    document.addEventListener('click', function (e) {
      var link = e.target.closest('.article-body a[target="_blank"]');
      if (!link) return;
      /* Let ctrl/cmd/middle/shift-click behave normally (open in background tab etc.) */
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return;
      e.preventDefault();
      openModal(link);
    });
  })();

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

});
