(function() {
  const docReady = fn => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
      fn();
    }
  };

  docReady(() => {
    const overlay = document.querySelector('[data-cta-overlay]');
    if (!overlay) {
      return;
    }
    const dismissButton = overlay.querySelector('[data-cta-dismiss]');
    const focusTarget = overlay.querySelector('a.button-link.primary');

    const timer = window.setTimeout(() => {
      overlay.setAttribute('aria-hidden', 'false');
      focusTarget?.focus();
    }, 120000);

    const closeOverlay = () => {
      overlay.setAttribute('aria-hidden', 'true');
      window.clearTimeout(timer);
    };

    dismissButton?.addEventListener('click', event => {
      event.preventDefault();
      closeOverlay();
    });

    overlay.addEventListener('click', event => {
      if (event.target === overlay) {
        closeOverlay();
      }
    });

    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && overlay.getAttribute('aria-hidden') === 'false') {
        closeOverlay();
      }
    });
  });
})();
