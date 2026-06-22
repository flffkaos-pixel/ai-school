(function() {
  var p = new URLSearchParams(location.search).get('path');
  var contentEl = document.getElementById('content');
  if (!p) {
    contentEl.innerHTML = '<div class="error"><h2>No path specified</h2><p>Use ?path= to specify a file.</p></div>';
    return;
  }
  var apiUrl = 'https://api.github.com/repos/aishwaryanr/awesome-generative-ai-guide/contents/' + p;
  var xhr = new XMLHttpRequest();
  xhr.open('GET', apiUrl, true);
  xhr.setRequestHeader('Accept', 'application/vnd.github.v3+json');
  xhr.timeout = 15000;
  xhr.ontimeout = function() { contentEl.innerHTML = '<div class="error"><h2>Request timed out</h2><p>Could not reach GitHub API.</p></div>'; };
  xhr.onerror = function() { contentEl.innerHTML = '<div class="error"><h2>Network error</h2><p>Could not reach the content server.</p></div>'; };
  xhr.onload = function() {
    if (xhr.status !== 200) {
      var msg = '';
      try { var e = JSON.parse(xhr.responseText); msg = e.message; } catch(ex) {}
      contentEl.innerHTML = '<div class="error"><h2>Failed to load (HTTP ' + xhr.status + ')</h2><p>' + (msg || 'File not found or access denied.') + '</p></div>';
      return;
    }
    try {
      var data = JSON.parse(xhr.responseText);
      if (data.encoding !== 'base64' || !data.content) throw new Error('Unexpected response format');
      var md = atob(data.content.replace(/\n/g, ''));
      if (typeof marked === 'undefined') throw new Error('marked.js not loaded');
      var html = marked.parse(md);
      html = html.replace(
        /src="https:\/\/github\.com\/aishwaryanr\/awesome-generative-ai-guide\/blob\/main\/([^"]+)"/g,
        'src="https://raw.githubusercontent.com/aishwaryanr/awesome-generative-ai-guide/main/$1"'
      );
      contentEl.innerHTML = html;
    } catch(e) {
      contentEl.innerHTML = '<div class="error"><h2>Parse error</h2><p>' + e.message + '</p></div>';
    }
  };
  xhr.send();
})();
