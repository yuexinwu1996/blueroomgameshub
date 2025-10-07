(function() {
  const docReady = fn => {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  };

  const fetchJson = async path => {
    const response = await fetch(path, { headers: { "Accept": "application/json" } });
    if (!response.ok) {
      throw new Error(`Failed to load ${path}: ${response.status}`);
    }
    return response.json();
  };

  const normaliseString = value => (value || "")
    .toString()
    .trim()
    .toLowerCase();

  const createResultMarkup = item => {
    const typeLabel = item.type === "guide" ? "Guide" : "Game";
    const descriptor = item.type === "guide" ? `${item.difficulty} guide` : `${item.difficulty} game`;
    return `<a class="search-result-item" href="${item.url}">
      <span style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
        <span>
          <strong>${item.title}</strong><br>
          <span style="color:var(--text-500);font-size:0.85rem;">${descriptor}</span>
        </span>
        <span class="pill">${typeLabel}</span>
      </span>
    </a>`;
  };

  const initialiseSearch = async () => {
    const searchForms = document.querySelectorAll('[data-search-form]');
    if (!searchForms.length) {
      return;
    }

    try {
      const [games, guides] = await Promise.all([
        fetchJson('/assets/data/games.json'),
        fetchJson('/assets/data/guides.json')
      ]);

      const searchIndex = [
        ...games.map(g => ({
          type: 'game',
          title: g.title,
          difficulty: g.difficulty,
          mechanisms: g.mechanisms || [],
          categories: g.categories || [],
          author: g.author,
          url: `/games/${g.slug}/`
        })),
        ...guides.map(g => ({
          type: 'guide',
          title: g.title,
          difficulty: g.difficulty,
          mechanisms: [],
          categories: [],
          author: g.author,
          url: `/guides/${g.slug}/`
        }))
      ];

      searchForms.forEach(form => {
        const input = form.querySelector('input[type="search"]');
        const panel = form.closest('[data-search]')?.querySelector('[data-search-results]');
        const closePanel = () => {
          if (panel) {
            panel.setAttribute('aria-expanded', 'false');
            panel.innerHTML = '';
          }
        };

        form.addEventListener('submit', event => {
          event.preventDefault();
          if (!input || !panel) {
            return;
          }
          const query = normaliseString(input.value);
          if (!query) {
            closePanel();
            return;
          }
          const matches = searchIndex.filter(item => {
            const haystack = [item.title, item.author, ...(item.mechanisms || []), ...(item.categories || [])]
              .map(normaliseString)
              .join(' ');
            return haystack.includes(query);
          }).slice(0, 6);

          if (!matches.length) {
            panel.innerHTML = '<div class="search-result-item" role="status">No matches found.</div>';
          } else {
            panel.innerHTML = matches.map(createResultMarkup).join('');
          }
          panel.setAttribute('aria-expanded', 'true');
        });

        input?.addEventListener('input', () => {
          if (!input.value) {
            closePanel();
          }
        });

        input?.addEventListener('focus', () => {
          if (panel && panel.innerHTML.trim()) {
            panel.setAttribute('aria-expanded', 'true');
          }
        });

        document.addEventListener('click', event => {
          if (!panel) {
            return;
          }
          if (!panel.contains(event.target) && !form.contains(event.target)) {
            closePanel();
          }
        });

        input?.addEventListener('keydown', event => {
          if (event.key === 'Escape') {
            closePanel();
            input.blur();
          }
        });
      });
    } catch (error) {
      console.error('[Search] Failed to initialise site search', error);
    }
  };

  docReady(() => {
    const yearNode = document.getElementById('current-year');
    if (yearNode) {
      yearNode.textContent = String(new Date().getFullYear());
    }
    initialiseSearch();
  });
})();
