(function() {
  const docReady = fn => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
      fn();
    }
  };

  const selectTab = (button, tablist) => {
    const targetId = button.getAttribute('data-tab-target');
    const buttons = tablist.querySelectorAll('[role="tab"]');
    const panels = tablist.parentElement.querySelectorAll('[role="tabpanel"]');

    buttons.forEach(btn => {
      const isActive = btn === button;
      btn.setAttribute('aria-selected', String(isActive));
      btn.setAttribute('tabindex', isActive ? '0' : '-1');
    });

    panels.forEach(panel => {
      const isActive = panel.id === targetId;
      panel.setAttribute('aria-hidden', String(!isActive));
    });
  };

  docReady(() => {
    const tablists = document.querySelectorAll('[data-tablist]');
    tablists.forEach(tablist => {
      const buttons = tablist.querySelectorAll('[role="tab"]');
      if (!buttons.length) {
        return;
      }

      buttons.forEach(button => {
        button.addEventListener('click', () => selectTab(button, tablist));
        button.addEventListener('keydown', event => {
          const currentIndex = Array.from(buttons).indexOf(button);
          if (event.key === 'ArrowRight') {
            const next = buttons[(currentIndex + 1) % buttons.length];
            next.focus();
            selectTab(next, tablist);
            event.preventDefault();
          }
          if (event.key === 'ArrowLeft') {
            const prev = buttons[(currentIndex - 1 + buttons.length) % buttons.length];
            prev.focus();
            selectTab(prev, tablist);
            event.preventDefault();
          }
        });
      });
    });
  });
})();
