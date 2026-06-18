$tmp = "C:\Users\중진공39\AppData\Local\Temp\ai-school-tmp"
$contentDir = "$tmp\content"

Get-ChildItem -LiteralPath $contentDir -Recurse -Filter "*.html" | ForEach-Object {
  $file = $_.FullName
  $rel = $file.Substring($contentDir.Length + 1)
  $depth = ($rel -split "\\").Count - 1
  $prefix = "../" * ($depth + 1)

  $text = Get-Content -LiteralPath $file -Raw

  # 1. Fix image URLs: github.com/blob/ -> raw.githubusercontent.com (no blob)
  $text = $text -replace 'https://github\.com/aishwaryanr/awesome-generative-ai-guide/blob/main/', 'https://raw.githubusercontent.com/aishwaryanr/awesome-generative-ai-guide/main/'
  $text = $text -replace 'https://github\.com/aishwaryanr/awesome-generative-ai-resources/blob/main/', 'https://raw.githubusercontent.com/aishwaryanr/awesome-generative-ai-resources/main/'

  # 2. Fix relative paths in template (all paths use ../ which is wrong for nested files)
  $text = $text -replace 'href="\.\./css/style\.css"', "href=`"${prefix}css/style.css`""
  $text = $text -replace 'src="\.\./js/main\.js"', "src=`"${prefix}js/main.js`""
  $text = $text -replace '(href=")\.\./index\.html"', "`$1${prefix}index.html`""
  $text = $text -replace '(href=")\.\./courses\.html"', "`$1${prefix}courses.html`""
  $text = $text -replace '(href=")\.\./interview\.html"', "`$1${prefix}interview.html`""
  $text = $text -replace '(href=")\.\./research\.html"', "`$1${prefix}research.html`""
  $text = $text -replace '(href=")\.\./resources\.html"', "`$1${prefix}resources.html`""
  $text = $text -replace '(href=")\.\./about\.html"', "`$1${prefix}about.html`""
  $text = $text -replace '(href=")\.\./viewer\.html', "`$1${prefix}viewer.html"

  # 3. Remove hardcoded data-theme so JS controls it
  $text = $text -replace '<html lang="en" data-theme="light">', '<html lang="en">'
  $text = $text -replace '<html lang="ko" data-theme="light">', '<html lang="ko">'

  # 4. Fix nav link active class - remove default ../ since Home/Courses etc. just need href
  # Already handled above

  Set-Content -LiteralPath $file -Value $text -NoNewline -Encoding UTF8
}

Write-Host "Done fixing all content files"
