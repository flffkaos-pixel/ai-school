import os, re, sys, traceback

tmp = r'C:\Users\중진공39\AppData\Local\Temp\ai-school-tmp'
f = os.path.join(tmp, 'content', 'readme.html')
print(f'File: {f}')
print(f'Exists: {os.path.exists(f)}')

with open(f, 'r', encoding='utf-8') as fh:
    text = fh.read()

print(f'File length: {len(text)}')

cv = re.search(r'<div class="content-viewer">(.*?)</div>\s*<footer', text, re.DOTALL)
if cv:
    print(f'Content length: {len(cv.group(1))}')
    
    # Now try to count elements
    content = cv.group(1)
    for tag in ['h1', 'h2', 'h3', 'p', 'li', 'blockquote']:
        count = len(re.findall(f'<{tag}[> ]', content))
        if count > 0:
            print(f'  {tag}: {count}')
    
    # Test process_elements
    print('\nTesting h1 processing...')
    pattern = re.compile(r'<h1[^>]*>(.*?)</h1>', re.DOTALL)
    for m in pattern.finditer(content):
        inner = m.group(1)
        print(f'  h1 inner: {inner[:80]}')
        break
    
    print('\nTesting p processing...')
    pattern = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL)
    matches = list(pattern.finditer(content))
    print(f'  Found {len(matches)} p elements')
    if matches:
        try:
            inner = matches[0].group(1)
            print(f'  First p inner: {inner[:100]}')
        except Exception as e:
            print(f'  ERROR accessing group: {e}')
            print(f'  Match groups: {matches[0].groups()}')
            print(f'  Match: >>>{matches[0].group(0)[:200]}<<<')
else:
    print('No content-viewer match')
    idx = text.find('class="content-viewer"')
    print(f'content-viewer at: {idx}')
    if idx >= 0:
        close_div = text.find('</div>', idx)
        footer = text.find('<footer', close_div)
        gap = text[close_div:footer+30]
        print(f'close div at: {close_div}, footer at: {footer}')
        print(f'Gap: >>>{gap}<<<')
        print(f'Gap repr: {repr(gap)}')
