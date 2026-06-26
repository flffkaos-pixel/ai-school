(function() {
  var p = new URLSearchParams(location.search).get('path');
  var contentEl = document.getElementById('content');
  if (!p) {
    contentEl.innerHTML = '<div class="error"><h2>No path specified</h2><p>Use ?path= to specify a file.</p></div>';
    return;
  }
  var localUrl = 'content/en/' + p;
  var xhr = new XMLHttpRequest();
  xhr.open('GET', localUrl, true);
  xhr.timeout = 10000;
  xhr.ontimeout = function() { contentEl.innerHTML = '<div class="error"><h2>Request timed out</h2></div>'; };
  xhr.onerror = function() { contentEl.innerHTML = '<div class="error"><h2>Failed to load content</h2></div>'; };
  xhr.onload = function() {
    if (xhr.status !== 200) {
      contentEl.innerHTML = '<div class="error"><h2>File not found</h2><p>' + localUrl + '</p></div>';
      return;
    }
    try {
      var md = xhr.responseText;
      if (typeof marked === 'undefined') throw new Error('marked.js not loaded');
      var html = marked.parse(md);
      // Convert GitHub blob image URLs to raw.githubusercontent.com
      html = html.replace(
        /src="https:\/\/github\.com\/aishwaryanr\/(?:awesome-generative-ai-guide|awesome-generative-ai-resources)\/blob\/main\/([^"]+)"/g,
        'src="https://raw.githubusercontent.com/aishwaryanr/awesome-generative-ai-guide/main/$1"'
      );
      // Resolve relative image paths to GitHub raw URLs
      var dir = p.substring(0, p.lastIndexOf('/'));
      var imgBase = 'https://raw.githubusercontent.com/aishwaryanr/awesome-generative-ai-guide/main/' + dir + '/';
      html = html.replace(/src="\.\//g, 'src="' + imgBase);
      contentEl.innerHTML = html;
    } catch(e) {
      contentEl.innerHTML = '<div class="error"><h2>Parse error</h2><p>' + e.message + '</p></div>';
    }
  };
  xhr.send();
})();
