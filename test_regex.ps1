$tmp = "C:\Users\중진공39\AppData\Local\Temp\ai-school-tmp"
$f = "$tmp\content\resources\genai_roadmap.html"
$text = Get-Content -LiteralPath $f -Raw
$m = [regex]::Match($text, '(?s)<div class="content-viewer">(.*?)</div>\s*<footer')
if ($m.Success) {
  Write-Host "MATCH: content length = $($m.Groups[1].Value.Length)"
} else {
  Write-Host "NO MATCH"
  $divIdx = $text.IndexOf('class="content-viewer"')
  $closeIdx = $text.IndexOf('</div>', $divIdx)
  $footerIdx = $text.IndexOf('<footer>', $closeIdx)
  $gap = $footerIdx - $closeIdx
  Write-Host "div at $divIdx, close at $closeIdx, footer at $footerIdx, gap=$gap"
}
