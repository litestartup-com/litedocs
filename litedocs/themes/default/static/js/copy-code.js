/**
 * LiteDocs - Code block copy button
 * Adds a copy-to-clipboard button on all <pre><code> blocks.
 */

function initCopyButtons(root) {
  const container = root || document;
  const blocks = container.querySelectorAll('pre');

  blocks.forEach(function(pre) {
    // Skip if already has a copy button
    if (pre.querySelector('.ld-code-copy')) return;

    const code = pre.querySelector('code');
    if (!code) return;

    // Add language label
    const langMatch = code.className.match(/language-(\w+)/);
    if (langMatch) {
      const langLabel = document.createElement('span');
      langLabel.className = 'ld-code-lang';
      langLabel.textContent = langMatch[1];
      pre.style.position = 'relative';
      pre.appendChild(langLabel);
    }

    // Add copy button
    const btn = document.createElement('button');
    btn.className = 'ld-code-copy';
    btn.setAttribute('aria-label', 'Copy code');
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path></svg>';

    btn.addEventListener('click', function() {
      const text = code.textContent || '';
      navigator.clipboard.writeText(text).then(function() {
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        btn.style.opacity = '1';
        setTimeout(function() {
          btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"></path></svg>';
          btn.style.opacity = '';
        }, 2000);
      });
    });

    pre.style.position = 'relative';
    pre.appendChild(btn);
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  initCopyButtons();
});

if (document.readyState !== 'loading') {
  initCopyButtons();
}
