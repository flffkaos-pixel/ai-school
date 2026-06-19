document.addEventListener('DOMContentLoaded', () => {

  // Theme toggle
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;
  const saved = localStorage.getItem('theme');
  if (saved) html.setAttribute('data-theme', saved);

  themeToggle?.addEventListener('click', () => {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    themeToggle.textContent = next === 'dark' ? '☀️' : '🌙';
  });

  // Set initial toggle icon
  if (themeToggle) {
    themeToggle.textContent = saved === 'dark' ? '☀️' : '🌙';
  }

  // Mobile menu
  const menuBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');
  menuBtn?.addEventListener('click', () => {
    navLinks?.classList.toggle('open');
  });

  // Close menu on link click
  navLinks?.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => navLinks.classList.remove('open'));
  });

  // Active nav link
  const pageName = location.pathname.split('/').pop() || 'index.html';
  navLinks?.querySelectorAll('a').forEach(a => {
    if (a.getAttribute('href') === pageName) a.classList.add('active');
  });

  // Language toggle: point EN/KO correctly when viewing content
  const contentPath = new URLSearchParams(location.search).get('path');
  if (contentPath) {
    const isViewer = location.pathname.includes('viewer.html');
    navLinks?.querySelectorAll('a').forEach(a => {
      if (a.textContent === 'EN') {
        if (isViewer) {
          a.href = location.href;
        } else {
          a.href = '/viewer.html?path=' + contentPath;
        }
        a.removeAttribute('target');
      }
      if (a.textContent === 'KO') {
        if (isViewer) {
          const dir = contentPath.substring(0, contentPath.lastIndexOf('/'));
          const base = contentPath.split('/').pop().replace(/\.md$/i, '');
          const slug = base.replace(/[^a-z0-9가-힣\/_\- ]/gi, '').trim().replace(/\s+/g, '-').toLowerCase().replace(/-+/g, '-') + '.html';
          a.href = '/content/' + (dir ? dir + '/' : '') + slug + '?path=' + encodeURIComponent(contentPath);
        } else {
          a.href = location.href;
        }
        a.removeAttribute('target');
      }
    });
  }

});
