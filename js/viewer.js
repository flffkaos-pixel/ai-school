(function() {
  const p = new URLSearchParams(location.search).get('path');
  const contentEl = document.getElementById('content');
  if (!p) {
    contentEl.innerHTML = '<div class="error" style="text-align:center;padding:80px 0;color:#e74c3c"><h2>No path specified</h2><p>Use ?path= to specify a file.</p></div>';
    return;
  }
  var url = 'https://cdn.jsdelivr.net/gh/aishwaryanr/awesome-generative-ai-guide@main/' + p;
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.onerror = function() { contentEl.innerHTML = '<div class="error"><h2>Network error</h2><p>Could not reach the content server.</p></div>'; };
  xhr.onload = function() {
    if (xhr.status !== 200) {
      contentEl.innerHTML = '<div class="error"><h2>Failed to load (HTTP ' + xhr.status + ')</h2><p><a href="' + url + '" target="_blank">Open directly</a></p></div>';
      return;
    }
    var md = xhr.responseText;
    try {
      if (typeof marked === 'undefined') throw new Error('marked.js not loaded');
      var html = marked.parse(md);
      html = html.replace(
        /src="https:\/\/github\.com\/aishwaryanr\/awesome-generative-ai-guide\/blob\/main\/([^"]+)"/g,
        'src="https://cdn.jsdelivr.net/gh/aishwaryanr/awesome-generative-ai-guide@main/$1"'
      );
      contentEl.innerHTML = html;
    } catch(e) {
      contentEl.innerHTML = '<div class="error"><h2>Parse error</h2><p>' + e.message + '</p></div>';
    }
  };
  xhr.send();
})();
