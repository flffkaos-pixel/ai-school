import os, re, time, urllib.request, urllib.parse, json, sys

import subprocess
result = subprocess.run(['powershell', '-Command', 
    "(New-Object -ComObject Scripting.FileSystemObject).GetFolder('C:\\Users\\중진공39\\site').ShortPath"
], capture_output=True, text=True)
site_dir = result.stdout.strip()

content_dir = os.path.join(site_dir, 'content')
API_DELAY = 0.3
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
    code_blocks = []
    def protect_code(m):
        code_blocks.append(m.group(0))
        return f'``CODE{len(code_blocks)-1}``'
    protected = re.sub(r'<code>[^<]*</code>', protect_code, inner_html, flags=re.DOTALL)
    
    translated = translate_text(protected)
    time.sleep(API_DELAY)
    
    for i, cb in enumerate(code_blocks):
        translated = translated.replace(f'``CODE{i}``', cb)
    return translated

def process_elements(html, tag):
    result = []
    last_end = 0
    pattern = re.compile(f'<{tag}[^>]*>(.*?)</{tag}>', re.DOTALL)
    for m in pattern.finditer(html):
        result.append(html[last_end:m.start()])
        inner = m.group(1)
        full_match = m.group(0)
        if inner and inner.strip() and '<pre>' not in inner and len(inner) <= 4000:
            translated = translate_element(inner)
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
    for tag in ['th', 'td']:
        html = process_elements(html, tag)
    html = re.sub(
        r'(<a\s[^>]*href="[^"]*"[^>]*>)(.*?)(</a>)',
        lambda m: m.group(1) + (translate_text(m.group(2)) if not re.search(r'<', m.group(2)) and len(m.group(2)) > 2 else m.group(2)) + m.group(3),
        html, flags=re.DOTALL
    )
    return html

# Find files that were skipped (mostly English, only a few garbled Korean chars)
files_to_translate = []
for root, dirs, fnames in os.walk(content_dir):
    for f in fnames:
        if not f.endswith('.html'):
            continue
        filepath = os.path.join(root, f)
        with open(filepath, 'r', encoding='utf-8') as fh:
            text = fh.read()
        
        cv_match = re.search(r'<div class="content-viewer">(.*?)</div>', text, re.DOTALL)
        if not cv_match:
            continue
        
        content = cv_match.group(1)
        eng_letters = len(re.findall(r'[a-zA-Z]', content))
        kor_letters = len(re.findall(r'[\uAC00-\uD7AF]', content))
        
        # "Mostly English" = English letters >> Korean letters
        if eng_letters > 0 and kor_letters < eng_letters / 3:
            files_to_translate.append((filepath, eng_letters, kor_letters))

files_to_translate.sort(key=lambda x: -x[1])
total = len(files_to_translate)
print(f'Found {total} files to retranslate')

for idx, (filepath, eng, kor) in enumerate(files_to_translate):
    rel = os.path.relpath(filepath, site_dir)
    elapsed = (time.time() - start_time) / 60
    print(f'[{idx+1}/{total} {elapsed:.1f}m] {rel} (E:{eng} K:{kor})', flush=True)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            text = fh.read()
        
        cv_match = re.search(r'<div class="content-viewer">(.*?)</div>\s*<footer', text, re.DOTALL)
        if not cv_match:
            print('  SKIP (no content-viewer)')
            continue
        
        content = cv_match.group(1)
        
        translated = translate_html(content)
        
        before = text[:cv_match.start(1)]
        after = text[cv_match.end(1):]
        
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(before + translated + after)
        
        if (idx + 1) % 3 == 0:
            print(f'  ... {call_count} calls, {total_chars//1000}K chars')
    except Exception as e:
        import traceback
        print(f'  ERROR: {e}', file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

total_time = (time.time() - start_time) / 60
print(f'\nDone! {total} files, {call_count} API calls, {total_chars//1000}K chars, {total_time:.1f}m')
