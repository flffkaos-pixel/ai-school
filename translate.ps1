$fso = New-Object -ComObject Scripting.FileSystemObject
$tmp = $fso.GetFolder("C:\Users\중진공39\AppData\Local\Temp\ai-school-tmp").ShortPath
$contentDir = "$tmp\content"

Add-Type -AssemblyName System.Web

$apiDelay = 300
$callCount = 0
$startTime = Get-Date
$totalChars = 0
$errors = @()

function TranslateText($text) {
  if ([string]::IsNullOrWhiteSpace($text)) { return $text }
  $t = $text.Trim()
  if ($t.Length -eq 0 -or $t.Length -gt 4000) { return $text }
  try {
    $url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q=" + [System.Web.HttpUtility]::UrlEncode($t)
    $result = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 20
    $script:callCount++
    $script:totalChars += $t.Length
    return $result[0][0][0]
  } catch { return $text }
}

function TranslateElement($innerHtml) {
  if ($innerHtml -match '<pre>' -or $innerHtml -match '<code>' -or $innerHtml -match '<img') { return $innerHtml }
  $tags = @()
  $textOnly = [regex]::Replace($innerHtml, '<[^>]+>', { param($m) $tags += $m.Value; return "`x00$($tags.Count - 1)`x00" })
  $translated = TranslateText $textOnly
  if ($translated -eq $textOnly) { return $innerHtml }
  Start-Sleep -Milliseconds $script:apiDelay
  $result = [regex]::Replace($translated, "`x00(\d+)`x00", { param($m) $idx = [int]$m.Groups[1].Value; if ($idx -lt $tags.Count) { return $tags[$idx] } else { return $m.Value } })
  return $result
}

function TranslateHtml($html) {
  $html = [regex]::Replace($html, "(?s)<p[^>]*>(.*?)</p>", { param($m) $tag = [regex]::Match($m.Value, "(?s)^(<p[^>]*>)").Value; return $tag + (TranslateElement $m.Groups[1].Value) + "</p>" })
  foreach ($lv in 1..6) {
    $html = [regex]::Replace($html, "(?s)<h$lv[^>]*>(.*?)</h$lv>", { param($m) $tag = [regex]::Match($m.Value, "(?s)^(<h$lv[^>]*>)").Value; return $tag + (TranslateElement $m.Groups[1].Value) + "</h$lv>" })
  }
  $html = [regex]::Replace($html, "(?s)<li[^>]*>(.*?)</li>", { param($m) $tag = [regex]::Match($m.Value, "(?s)^(<li[^>]*>)").Value; return $tag + (TranslateElement $m.Groups[1].Value) + "</li>" })
  $html = [regex]::Replace($html, "(?s)<blockquote[^>]*>(.*?)</blockquote>", { param($m) $tag = [regex]::Match($m.Value, "(?s)^(<blockquote[^>]*>)").Value; return $tag + (TranslateElement $m.Groups[1].Value) + "</blockquote>" })
  foreach ($c in @('th','td')) {
    $html = [regex]::Replace($html, "(?s)<$c[^>]*>(.*?)</$c>", { param($m) $tag = [regex]::Match($m.Value, "(?s)^(<$c[^>]*>)").Value; return $tag + (TranslateElement $m.Groups[1].Value) + "</$c>" })
  }
  $html = [regex]::Replace($html, '(?s)<a\s[^>]*href="[^"]*"[^>]*>(.*?)</a>', { param($m) $inner = $m.Groups[1].Value; if ($inner -match '<' -or $inner.Length -le 2) { return $m.Value }; $tag = [regex]::Match($m.Value, '(?s)^(<a[^>]+>)').Value; $t = TranslateText $inner; Start-Sleep -Milliseconds $script:apiDelay; return $tag + $t + "</a>" })
  return $html
}

$files = Get-ChildItem -LiteralPath $contentDir -Recurse -Filter "*.html"
$total = $files.Count
$count = 0

foreach ($file in $files) {
  $count++
  $rel = $file.FullName.Substring($contentDir.Length + 1)
  $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
  Write-Host ("[$count/$total ${elapsed}m] " + $rel)

  try {
    $text = Get-Content -LiteralPath $file.FullName -Raw
    if ($text -match '(?s)<div class="content-viewer">.*?[\uAC00-\uD7AF].*?</div>') {
      Write-Host "  SKIP (already Korean)"
      continue
    }
    $m = [regex]::Match($text, '(?s)(<div class="content-viewer">)(.*?)(</div>\s*<footer)')
    if ($m.Success) {
      $before = $m.Groups[1].Value
      $content = $m.Groups[2].Value
      $after = $m.Groups[3].Value
      $translated = TranslateHtml $content
      Set-Content -LiteralPath $file.FullName -Value ($before + $translated + $after) -NoNewline -Encoding UTF8
      if ($count % 3 -eq 0) { Write-Host ("  ... " + $callCount + " calls, " + [math]::Round($totalChars/1000,0) + "K chars") }
    }
  } catch {
    Write-Host ("  ERROR: " + $_)
    $errors += ($rel + " : " + $_)
  }
}

$totalTime = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
Write-Host ("`nDone! " + $count + " files, " + $callCount + " API calls, " + [math]::Round($totalChars/1000,0) + "K chars, " + $totalTime + "m")
if ($errors.Count -gt 0) { Write-Host "ERRORS:"; $errors | ForEach-Object { Write-Host "  $_" } }
