/**
 * LiteDocs - Main application JavaScript
 * Handles: dark mode, TOC scroll spy, sidebar toggle, language menu, doc menu, search modal
 */

// ---- Dark Mode ----

function initDarkMode() {
  const stored = localStorage.getItem('ld-dark-mode');
  if (stored === 'true' || (stored === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
    updateHljsTheme(true);
  } else {
    document.documentElement.classList.remove('dark');
    updateHljsTheme(false);
  }
}

function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('ld-dark-mode', isDark);
  updateHljsTheme(isDark);
}

function updateHljsTheme(isDark) {
  const light = document.getElementById('hljs-light');
  const dark = document.getElementById('hljs-dark');
  if (light && dark) {
    light.disabled = isDark;
    dark.disabled = !isDark;
  }
}

// ---- Mobile Drawer Toggle ----

function toggleDrawer() {
  var drawer = document.getElementById('mobile-drawer');
  if (!drawer) return;

  var isOpen = drawer.classList.contains('ld-drawer-open');
  if (isOpen) {
    drawer.classList.remove('ld-drawer-open');
    document.body.style.overflow = '';
  } else {
    drawer.classList.add('ld-drawer-open');
    document.body.style.overflow = 'hidden';
  }
}

// ---- Language Menu ----

function toggleLangMenu() {
  const menu = document.getElementById('lang-menu');
  if (menu) menu.classList.toggle('hidden');
}

// ---- Doc Switcher Menu ----

function toggleDocMenu() {
  const menu = document.getElementById('doc-menu');
  if (menu) menu.classList.toggle('hidden');
}

// Close dropdown menus on outside click
document.addEventListener('click', function (e) {
  var dropdowns = [
    { trigger: 'lang-switcher', menu: 'lang-menu' },
    { trigger: 'doc-switcher', menu: 'doc-menu' }
  ];
  dropdowns.forEach(function (dd) {
    var trigger = document.getElementById(dd.trigger);
    var menu = document.getElementById(dd.menu);
    if (trigger && menu && !trigger.contains(e.target)) {
      menu.classList.add('hidden');
    }
  });
});

// ---- Search Modal ----

function openSearch() {
  const modal = document.getElementById('search-modal');
  if (modal) {
    modal.classList.remove('hidden');
    const input = document.getElementById('search-input');
    if (input) {
      input.value = '';
      input.focus();
    }
    document.body.style.overflow = 'hidden';
  }
}

function closeSearch() {
  const modal = document.getElementById('search-modal');
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

// Ctrl+K / Cmd+K to open search
document.addEventListener('keydown', function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const modal = document.getElementById('search-modal');
    if (modal && modal.classList.contains('hidden')) {
      openSearch();
    } else {
      closeSearch();
    }
  }
  if (e.key === 'Escape') {
    closeSearch();
  }
});

// ---- TOC Scroll Spy ----

function initTocScrollSpy() {
  const tocLinks = document.querySelectorAll('#toc-list a[data-toc-id]');
  if (tocLinks.length === 0) return;

  const headingIds = Array.from(tocLinks).map(a => a.dataset.tocId);
  const headings = headingIds
    .map(id => document.getElementById(id))
    .filter(el => el !== null);

  if (headings.length === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          tocLinks.forEach(a => a.classList.remove('ld-toc-active'));
          const active = document.querySelector(`#toc-list a[data-toc-id="${entry.target.id}"]`);
          if (active) active.classList.add('ld-toc-active');
        }
      }
    },
    { rootMargin: '-110px 0px -60% 0px', threshold: 0 }
  );

  headings.forEach(h => observer.observe(h));
}

// ---- Sidebar Active State ----

function updateSidebarActive() {
  var path = window.location.pathname.replace(/\/$/, '');
  var links = document.querySelectorAll('.ld-nav-link[href]');
  links.forEach(function (a) {
    var href = a.getAttribute('href').replace(/\/$/, '');
    // Clear any inline border/margin styles that may have leaked
    a.style.borderLeft = '';
    a.style.marginLeft = '';
    a.style.paddingLeft = '';
    a.style.border = '';
    if (href === path) {
      // Set active: only toggle the CSS class, styling is in style.css
      a.classList.add('ld-nav-active');
      a.classList.remove('text-zinc-600', 'dark:text-zinc-400', 'hover:bg-zinc-100', 'dark:hover:bg-zinc-800/60', 'hover:text-zinc-900', 'dark:hover:text-zinc-100');
      // Expand parent groups
      var parent = a.parentElement;
      while (parent) {
        if (parent.classList.contains('ld-nav-group') && parent.hasAttribute('data-collapsed')) {
          parent.removeAttribute('data-collapsed');
        }
        parent = parent.parentElement;
      }
    } else {
      // Remove active
      a.classList.remove('ld-nav-active');
      // Restore default styling classes
      a.classList.add('text-zinc-600', 'dark:text-zinc-400', 'hover:bg-zinc-100', 'dark:hover:bg-zinc-800/60', 'hover:text-zinc-900', 'dark:hover:text-zinc-100');
    }
  });
}

// ---- Nav Active State ----

function updateNavActive() {
  var path = window.location.pathname.replace(/\/$/, '');
  var navLinks = document.querySelectorAll('header nav a[href]');
  var bestIdx = -1;
  var bestLen = -1;
  var internalLinks = [];

  navLinks.forEach(function (a, i) {
    if (a.getAttribute('target') === '_blank') return;
    var href = (a.getAttribute('href') || '').replace(/\/$/, '');
    internalLinks.push({ el: a, href: href, idx: i });
    if (href === path) {
      bestIdx = i; bestLen = 99999;
    } else if (href && path.startsWith(href + '/') && href.length > bestLen) {
      bestIdx = i; bestLen = href.length;
    }
  });

  navLinks.forEach(function (a, i) {
    var indicator = a.querySelector('span.bg-primary-500');
    if (i === bestIdx) {
      a.classList.remove('text-zinc-500', 'dark:text-zinc-400');
      a.classList.add('text-zinc-900', 'dark:text-zinc-50', 'font-medium');
      if (!indicator) {
        var span = document.createElement('span');
        span.className = 'absolute bottom-0 left-3 right-3 h-0.5 bg-primary-500 rounded-full';
        a.style.position = 'relative';
        a.appendChild(span);
      }
    } else {
      a.classList.remove('text-zinc-900', 'dark:text-zinc-50', 'font-medium');
      a.classList.add('text-zinc-500', 'dark:text-zinc-400');
      if (indicator) indicator.remove();
    }
  });
}

// ---- HTMX Integration ----

document.addEventListener('htmx:afterSwap', function (e) {
  if (e.detail.target.id === 'content') {
    // Re-highlight code blocks
    if (typeof hljs !== 'undefined') {
      e.detail.target.querySelectorAll('pre code').forEach(block => hljs.highlightElement(block));
    }
    // Re-init copy buttons
    if (typeof initCopyButtons === 'function') initCopyButtons(e.detail.target);
    // Re-init TOC
    initTocScrollSpy();
    // Update active states
    updateSidebarActive();
    updateNavActive();
    // Close mobile drawer if open
    var drawer = document.getElementById('mobile-drawer');
    if (drawer && drawer.classList.contains('ld-drawer-open')) {
      toggleDrawer();
    }
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    // Add fade-in animation
    e.detail.target.classList.add('ld-fade-in');
  }
});

// ---- Initialize ----

document.addEventListener('DOMContentLoaded', function () {
  initDarkMode();
  initTocScrollSpy();
});

// Also run on initial load (for cases where DOMContentLoaded already fired)
if (document.readyState !== 'loading') {
  initDarkMode();
  initTocScrollSpy();
}
