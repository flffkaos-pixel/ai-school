import os, re, time, urllib.request, urllib.parse, json, sys

# Use short path for Korean directory
import subprocess
result = subprocess.run(['powershell', '-Command', 
    "(New-Object -ComObject Scripting.FileSystemObject).GetFolder('C:\\Users\\중진공39\\AppData\\Local\\Temp\\ai-school-tmp').ShortPath"
], capture_output=True, text=True)
tmp_dir = result.stdout.strip()

content_dir = os.path.join(tmp_dir, 'content')
API_DELAY = 0.3  # seconds between calls
call_count = 0
total_chars = 0
start_time = time.time()

def translate_text(text):
    global call_count, total_chars
    if not text or not text.strip():
        return text
    text = text.strip()
    if len(text) > 4000:
        return text
    try:
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=' + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            call_count += 1
            total_chars += len(text)
            return data[0][0][0]
    except Exception as e:
        print(f'  [API Error: {text[:50]}]', file=sys.stderr)
        return text

def translate_element(inner_html):
    if '<pre>' in inner_html or '<img ' in inner_html or len(inner_html) > 4000:
        return inner_html
    # Protect code blocks
    code_blocks = []
    def protect_code(m):
        code_blocks.append(m.group(0))
        return f'``CODE{len(code_blocks)-1}``'
    protected = re.sub(r'<code>[^<]*</code>', protect_code, inner_html, flags=re.DOTALL)
    
    translated = translate_text(protected)
    time.sleep(API_DELAY)
    
    # Restore code blocks
    for i, cb in enumerate(code_blocks):
        translated = translated.replace(f'``CODE{i}``', cb)
    return translated

def process_elements(html, tag):
    """Translate text content within <tag> elements"""
    result = []
    last_end = 0
    pattern = re.compile(f'<{tag}[^>]*>(.*?)</{tag}>', re.DOTALL)
    for m in pattern.finditer(html):
        result.append(html[last_end:m.start()])
        inner = m.group(1)
        full_match = m.group(0)
        if inner and inner.strip() and '<pre>' not in inner and len(inner) <= 4000:
            translated = translate_element(inner)
            # Extract opening tag
            open_tag_end = full_match.index('>', full_match.index(f'<{tag}')) + 1
            opening_tag = full_match[:open_tag_end]
            result.append(opening_tag + translated + f'</{tag}>')
        else:
            result.append(full_match)
        last_end = m.end()
    result.append(html[last_end:])
    return ''.join(result)

def translate_html(html):
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote']:
        html = process_elements(html, tag)
    # Table cells
    for tag in ['th', 'td']:
        html = process_elements(html, tag)
    # Simple link text
    html = re.sub(
        r'(<a\s[^>]*href="[^"]*"[^>]*>)(.*?)(</a>)',
        lambda m: m.group(1) + (translate_text(m.group(2)) if not re.search(r'<', m.group(2)) and len(m.group(2)) > 2 else m.group(2)) + m.group(3),
        html, flags=re.DOTALL
    )
    return html

# Find all HTML files
files = []
for root, dirs, fnames in os.walk(content_dir):
    for f in fnames:
        if f.endswith('.html'):
            files.append(os.path.join(root, f))

total = len(files)
print(f'Found {total} HTML files to translate')
print(f'Content dir: {content_dir}')

for idx, filepath in enumerate(files):
    rel = os.path.relpath(filepath, content_dir)
    elapsed = (time.time() - start_time) / 60
    print(f'[{idx+1}/{total} {elapsed:.1f}m] {rel}', flush=True)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Skip if already has Korean characters in content-viewer
        cv_match = re.search(r'<div class="content-viewer">(.*?)</div>\s*<footer', text, re.DOTALL)
        if not cv_match:
            print('  SKIP (no content-viewer)')
            continue
        
        content = cv_match.group(1)
        # Check for Korean
        if re.search(r'[\uAC00-\uD7AF]', content):
            print('  SKIP (already Korean)')
            continue
        
        before = text[:cv_match.start(1)]
        after = text[cv_match.end(1):]
        
        translated = translate_html(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(before + translated + after)
        
        if (idx + 1) % 3 == 0:
            print(f'  ... {call_count} calls, {total_chars//1000}K chars')
    except Exception as e:
        import traceback
        print(f'  ERROR: {e}', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

total_time = (time.time() - start_time) / 60
print(f'\nDone! {total} files, {call_count} API calls, {total_chars//1000}K chars, {total_time:.1f}m')
