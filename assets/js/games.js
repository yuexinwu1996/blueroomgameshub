(function() {
  const docReady = fn => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
      fn();
    }
  };

  const parseQuery = () => {
    const params = new URLSearchParams(window.location.search);
    const filters = {
      categories: params.getAll('category'),
      mechanisms: params.getAll('mechanism'),
      difficulty: params.getAll('difficulty'),
      language: params.getAll('language')
    };
    return {
      search: params.get('search') || '',
      sort: params.get('sort') || 'trending',
      page: Math.max(1, parseInt(params.get('page') || '1', 10)),
      filters
    };
  };

  const updateQuery = state => {
    const params = new URLSearchParams();
    if (state.search) {
      params.set('search', state.search);
    }
    if (state.sort && state.sort !== 'trending') {
      params.set('sort', state.sort);
    }
    Object.entries(state.filters).forEach(([key, values]) => {
      const paramKey = {categories: 'category', mechanisms: 'mechanism', difficulty: 'difficulty', language: 'language'}[key];
      if (paramKey) {
        values.forEach(value => params.append(paramKey, value));
      }
    });
    if (state.page > 1) {
      params.set('page', String(state.page));
    }
    const newUrl = `${window.location.pathname}${params.toString() ? `?${params}` : ''}`;
    window.history.replaceState({}, '', newUrl);
  };

  const computeTrendingScore = game => (0.7 * (game.pv7_norm || 0)) + (0.2 * (game.guide_clicks7_norm || 0)) + (0.1 * (game.recency || 0));

  const sorters = {
    trending: (a, b) => computeTrendingScore(b) - computeTrendingScore(a),
    new: (a, b) => new Date(b.created_at) - new Date(a.created_at),
    'most-rated': (a, b) => (b.rating || 0) - (a.rating || 0),
    alpha: (a, b) => a.title.localeCompare(b.title)
  };

  const normalise = value => value.toLowerCase();

  const matchesFilters = (game, filters) => {
    if (filters.categories.length && !filters.categories.some(cat => game.categories?.includes(cat))) {
      return false;
    }
    if (filters.mechanisms.length && !filters.mechanisms.some(mech => game.mechanisms?.includes(mech))) {
      return false;
    }
    if (filters.difficulty.length && !filters.difficulty.includes(game.difficulty)) {
      return false;
    }
    if (filters.language.length && !filters.language.some(lang => game.languages?.includes(lang))) {
      return false;
    }
    return true;
  };

  const matchesSearch = (game, query) => {
    if (!query) {
      return true;
    }
    const haystack = [
      game.title,
      game.summary,
      game.author,
      ...(game.categories || []),
      ...(game.mechanisms || [])
    ].join(' ').toLowerCase();
    return haystack.includes(query.toLowerCase());
  };

  const buildCard = game => {
    const mechanismHtml = (game.mechanisms || []).slice(0, 3).map(item => `<span class="pill">${item}</span>`).join('');
    const difficultyPill = `<span class="badge-soft">${game.difficulty}</span>`;
    return `<article class="game-card" data-game-card>
      <img src="${game.thumbnail}" alt="${game.title} cover" loading="lazy" width="320" height="180">
      <div>
        ${difficultyPill}
        <h3>${game.title}</h3>
        <p>${game.summary || ''}</p>
      </div>
      <div class="pill-row">${mechanismHtml}</div>
      <div class="card-actions">
        <a class="button-link primary" href="${game.play_url}" target="_blank" rel="noopener">Play now</a>
        <a class="button-link secondary" href="/games/${game.slug}/">Details</a>
      </div>
    </article>`;
  };

  const renderPagination = (container, state, totalItems, pageSize) => {
    if (!container) {
      return;
    }
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
    const parts = [];
    const appendLink = (page, label, isCurrent = false) => {
      const params = new URLSearchParams(window.location.search);
      if (page === 1) {
        params.delete('page');
      } else {
        params.set('page', String(page));
      }
      const href = `${window.location.pathname}${params.toString() ? `?${params}` : ''}`;
      parts.push(isCurrent ? `<span class="current">${label}</span>` : `<a href="${href}">${label}</a>`);
    };

    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }

    if (state.page > 1) {
      appendLink(state.page - 1, 'Previous');
    }

    for (let page = 1; page <= totalPages; page += 1) {
      appendLink(page, page, page === state.page);
    }

    if (state.page < totalPages) {
      appendLink(state.page + 1, 'Next');
    }

    container.innerHTML = parts.join('');
  };

  const initialiseGames = async () => {
    const grid = document.querySelector('[data-games-grid]');
    if (!grid) {
      return;
    }
    const pagination = document.querySelector('[data-games-pagination]');
    const searchInput = document.querySelector('[data-games-search]');
    const sortSelect = document.querySelector('[data-games-sort]');
    const facetInputs = document.querySelectorAll('[data-facet]');
    const pageSize = parseInt(grid.getAttribute('data-page-size') || '24', 10);

    const state = parseQuery();

    try {
      const games = await fetch('/assets/data/games.json').then(res => res.json());

      const applyStateToControls = () => {
        if (searchInput) {
          searchInput.value = state.search;
        }
        if (sortSelect) {
          sortSelect.value = state.sort;
        }
        facetInputs.forEach(input => {
          const facet = input.getAttribute('data-facet');
          const value = input.value;
          if (facet === 'categories' && state.filters.categories.includes(value)) {
            input.checked = true;
          }
          if (facet === 'mechanisms' && state.filters.mechanisms.includes(value)) {
            input.checked = true;
          }
          if (facet === 'difficulty' && state.filters.difficulty.includes(value)) {
            input.checked = true;
          }
          if (facet === 'language' && state.filters.language.includes(value)) {
            input.checked = true;
          }
        });
      };

      const render = () => {
        const filtered = games
          .filter(game => matchesFilters(game, state.filters))
          .filter(game => matchesSearch(game, state.search));

        const sorter = sorters[state.sort] || sorters.trending;
        filtered.sort(sorter);

        const total = filtered.length;
        const totalPages = Math.max(1, Math.ceil(total / pageSize));
        state.page = Math.min(state.page, totalPages);

        const start = (state.page - 1) * pageSize;
        const pageItems = filtered.slice(start, start + pageSize);
        grid.innerHTML = pageItems.map(buildCard).join('');
        updateQuery(state);
        renderPagination(pagination, state, total, pageSize);

        const summary = document.querySelector('[data-results-count]');
        if (summary) {
          summary.textContent = `${total} ${total === 1 ? 'game' : 'games'} found`;
        }
      };

      applyStateToControls();
      render();

      searchInput?.addEventListener('input', event => {
        state.search = event.target.value.trim();
        state.page = 1;
        render();
      });

      sortSelect?.addEventListener('change', event => {
        state.sort = event.target.value;
        state.page = 1;
        render();
      });

      facetInputs.forEach(input => {
        input.addEventListener('change', () => {
          const facet = input.getAttribute('data-facet');
          const value = input.value;
          const target = state.filters[facet];
          if (!target) {
            return;
          }
          if (input.checked) {
            if (!target.includes(value)) {
              target.push(value);
            }
          } else {
            state.filters[facet] = target.filter(item => item !== value);
          }
          state.page = 1;
          render();
        });
      });

      pagination?.addEventListener('click', event => {
        if (event.target instanceof HTMLAnchorElement) {
          event.preventDefault();
          const url = new URL(event.target.href);
          state.page = Math.max(1, parseInt(url.searchParams.get('page') || '1', 10));
          render();
        }
      });
    } catch (error) {
      console.error('[Games] Failed to load games data', error);
    }
  };

  docReady(initialiseGames);
})();
