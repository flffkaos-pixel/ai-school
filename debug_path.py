import os, re, subprocess

result = subprocess.run(['powershell', '-Command', 
    "(New-Object -ComObject Scripting.FileSystemObject).GetFolder('C:\\Users\\\uC911\uC9C4\uACF339\\site').ShortPath"
], capture_output=True, text=True)
site_dir = result.stdout.strip()
print(f'site_dir: |{site_dir}|')

content_dir = os.path.join(site_dir, 'content')
print(f'content_dir: {content_dir}')
print(f'content_dir exists: {os.path.isdir(content_dir)}')

count = 0
for root, dirs, fnames in os.walk(content_dir):
    for f in fnames:
        if f.endswith('.html'):
            count += 1
print(f'HTML files: {count}')

# Now test the filter on a specific file
test_file = os.path.join(content_dir, 'resources', 'genai_roadmap.html')
with open(test_file, 'r', encoding='utf-8') as fh:
    text = fh.read()
cv_match = re.search(r'<div class="content-viewer">(.*?)</div>', text, re.DOTALL)
if cv_match:
    content = cv_match.group(1)
    eng = len(re.findall(r'[a-zA-Z]', content))
    kor = len(re.findall(r'[\uAC00-\uD7AF]', content))
    print(f'genai_roadmap: eng={eng} kor={kor} ratio={eng/max(1,kor):.1f} pass={eng > 0 and kor < eng/3}')
else:
    print('genai_roadmap: no content-viewer match')
