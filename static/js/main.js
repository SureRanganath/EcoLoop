/* EcoLoop — Premium UI JavaScript */
'use strict';

// ── Navbar scroll effect ──────────────────────────────────────
const navbar = document.querySelector('.navbar-premium');
if (navbar) {
  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

// ── Scroll reveal ─────────────────────────────────────────────
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      revealObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => {
  revealObserver.observe(el);
});

// ── Animated counters ─────────────────────────────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.target || el.textContent, 10);
  if (isNaN(target)) return;
  const duration = 1800;
  const start = performance.now();
  const update = (now) => {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(eased * target);
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = target;
  };
  requestAnimationFrame(update);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      animateCounter(e.target);
      counterObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.counter').forEach(el => {
  el.dataset.target = el.textContent.trim();
  counterObserver.observe(el);
});

// ── Score bar animation ───────────────────────────────────────
const scoreObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const fill = e.target.querySelector('.score-fill');
      if (fill) {
        const w = fill.dataset.width || fill.style.width;
        fill.style.width = '0%';
        setTimeout(() => { fill.style.width = w; }, 100);
      }
      scoreObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('.score-bar').forEach(el => scoreObserver.observe(el));

// ── Auto-dismiss alerts ───────────────────────────────────────
document.querySelectorAll('.alert-premium').forEach(alert => {
  setTimeout(() => {
    alert.style.transition = 'opacity 0.5s, transform 0.5s';
    alert.style.opacity = '0';
    alert.style.transform = 'translateY(-8px)';
    setTimeout(() => alert.remove(), 500);
  }, 5000);
});

// ── Favourite toggle AJAX ─────────────────────────────────────
document.querySelectorAll('.fav-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    const url = btn.dataset.url;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    try {
      const res = await fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      const data = await res.json();
      const icon = btn.querySelector('i');
      if (data.action === 'added') {
        icon.className = 'bi bi-heart-fill';
        btn.classList.add('active');
      } else {
        icon.className = 'bi bi-heart';
        btn.classList.remove('active');
      }
    } catch (_) { window.location = url; }
  });
});

// ── Smooth page transitions ───────────────────────────────────
document.querySelectorAll('a[href]').forEach(link => {
  if (link.hostname === window.location.hostname &&
      !link.href.includes('#') &&
      !link.dataset.bsToggle &&
      link.target !== '_blank') {
    link.addEventListener('click', () => {
      document.body.style.opacity = '0.85';
      document.body.style.transition = 'opacity 0.2s';
    });
  }
});
window.addEventListener('pageshow', () => {
  document.body.style.opacity = '1';
});

// ── Tooltip init ──────────────────────────────────────────────
if (typeof bootstrap !== 'undefined') {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });
}
