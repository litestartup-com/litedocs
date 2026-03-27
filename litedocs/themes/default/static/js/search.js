/**
 * LiteDocs - Client-side search with MiniSearch
 * Lazy-loads the search index on first interaction.
 */

(function () {
  var _index = null;
  var _docs = null;
  var _loading = false;
  var _currentLocale = '';

  function getBasePath() {
    return window.__LD_BASE_PATH__ || '';
  }

  function getDocSlug() {
    // Extract doc_slug from URL: {base_path}/{doc_slug}/{locale}/{path}
    var bp = getBasePath();
    var path = window.location.pathname;
    if (bp && path.startsWith(bp)) {
      path = path.substring(bp.length);
    }
    var parts = path.split('/').filter(Boolean);
    return parts.length > 0 ? parts[0] : '';
  }

  function getCurrentLocale() {
    var bp = getBasePath();
    var path = window.location.pathname;
    if (bp && path.startsWith(bp)) {
      path = path.substring(bp.length);
    }
    var parts = path.split('/').filter(Boolean);
    return parts.length > 1 ? parts[1] : 'en';
  }

  function loadIndex(callback) {
    if (_index) {
      callback();
      return;
    }
    if (_loading) return;
    _loading = true;

    var slug = getDocSlug();
    _currentLocale = getCurrentLocale();
    var bp = getBasePath();
    var url = bp + '/' + slug + '/api/search-index.json';

    fetch(url)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        _docs = data;
        _index = new MiniSearch({
          fields: ['title', 'description', 'headings', 'body'],
          storeFields: ['title', 'description', 'locale', 'product'],
          searchOptions: {
            boost: { title: 3, headings: 2, description: 1.5 },
            fuzzy: 0.2,
            prefix: true,
          },
        });
        _index.addAll(data);
        _loading = false;
        callback();
      })
      .catch(function () {
        _loading = false;
      });
  }

  function doSearch(query) {
    if (!_index || !query.trim()) {
      renderResults([]);
      return;
    }

    var locale = getCurrentLocale();
    var results = _index.search(query, {
      filter: function (result) {
        return result.locale === locale;
      },
    });

    renderResults(results.slice(0, 10));
  }

  function renderResults(results) {
    var container = document.getElementById('search-results');
    if (!container) return;

    if (results.length === 0) {
      var input = document.getElementById('search-input');
      var query = input ? input.value.trim() : '';
      if (query) {
        container.innerHTML = '<div class="p-8 text-center text-sm text-zinc-400">No results found</div>';
      } else {
        container.innerHTML = '<div class="p-8 text-center text-sm text-zinc-400">Type to search...</div>';
      }
      return;
    }

    var html = '';
    results.forEach(function (r) {
      var title = escapeHtml(r.title || 'Untitled');
      var desc = escapeHtml((r.description || '').substring(0, 120));
      var href = getBasePath() + r.id;
      // Build breadcrumb from path
      var parts = r.id.split('/').filter(Boolean);
      var breadcrumb = parts.slice(2).join(' › ') || 'Home';

      html += '<a href="' + href + '" class="ld-search-result block px-3 py-2.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer" onclick="closeSearch()">'
        + '<div class="text-sm font-medium text-zinc-900 dark:text-zinc-100">' + title + '</div>'
        + (desc ? '<div class="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 line-clamp-1">' + desc + '</div>' : '')
        + '<div class="text-[11px] text-zinc-400 dark:text-zinc-500 mt-0.5">' + escapeHtml(breadcrumb) + '</div>'
        + '</a>';
    });

    container.innerHTML = html;
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Bind search input
  function initSearch() {
    var input = document.getElementById('search-input');
    if (!input) return;

    var debounceTimer = null;
    input.addEventListener('input', function () {
      var query = input.value;
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        loadIndex(function () {
          doSearch(query);
        });
      }, 150);
    });

    // Keyboard navigation in results
    input.addEventListener('keydown', function (e) {
      var results = document.querySelectorAll('.ld-search-result');
      if (results.length === 0) return;

      var active = document.querySelector('.ld-search-result.ld-search-active');
      var idx = -1;
      if (active) {
        results.forEach(function (r, i) { if (r === active) idx = i; });
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (active) active.classList.remove('ld-search-active', 'bg-zinc-100', 'dark:bg-zinc-800');
        idx = (idx + 1) % results.length;
        results[idx].classList.add('ld-search-active', 'bg-zinc-100', 'dark:bg-zinc-800');
        results[idx].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (active) active.classList.remove('ld-search-active', 'bg-zinc-100', 'dark:bg-zinc-800');
        idx = idx <= 0 ? results.length - 1 : idx - 1;
        results[idx].classList.add('ld-search-active', 'bg-zinc-100', 'dark:bg-zinc-800');
        results[idx].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (active) {
          window.location.href = active.getAttribute('href');
          closeSearch();
        } else if (results.length > 0) {
          window.location.href = results[0].getAttribute('href');
          closeSearch();
        }
      }
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
  } else {
    initSearch();
  }

  // Re-init after HTMX swap (in case search modal is re-rendered)
  document.addEventListener('htmx:afterSwap', function () {
    initSearch();
  });
})();
