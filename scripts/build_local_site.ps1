[CmdletBinding()]
param(
    [string]$Python,
    [switch]$Serve,
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $Root

function Assert-UnderRoot {
    param([string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path)
    $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    if (-not $full.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify path outside workspace: $full"
    }
}

function Reset-Directory {
    param([string]$Path)
    Assert-UnderRoot $Path
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Path | Out-Null
}

function Copy-SharedAssets {
    param([string]$Destination)
    foreach ($item in @('extra.css', 'images', 'js', 'Assets')) {
        $source = Join-Path $Root "docs\$item"
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination $Destination -Recurse -Force
        }
    }
}

function Remove-MarkdownBom {
    param([string]$Directory)
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    Get-ChildItem -LiteralPath $Directory -File -Filter '*.md' | ForEach-Object {
        $text = [System.IO.File]::ReadAllText($_.FullName)
        $text = $text.TrimStart([char]0xFEFF)
        [System.IO.File]::WriteAllText($_.FullName, $text, $utf8NoBom)
    }
}

function Add-EnglishHeadingAnchors {
    param([string]$SourceDirectory, [string]$TranslatedDirectory)
    $script = @'
from pathlib import Path
import re
import sys
from markdown.extensions.toc import slugify, unique

source_dir = Path(sys.argv[1])
translated_dir = Path(sys.argv[2])

fence_re = re.compile(r"^\s*(`{3,}|~{3,})")
heading_re = re.compile(r"^(#{1,6})\s+(.+?)(\s+#+)?\s*$")
link_re = re.compile(r"\[([^\]]+)\]\([^)]+\)")
html_re = re.compile(r"<[^>]+>")

def plain_heading(text: str) -> str:
    text = re.sub(r"\s+\{#[^}]+\}\s*$", "", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = link_re.sub(r"\1", text)
    text = html_re.sub("", text)
    text = text.replace("*", "")
    return text.strip()

def heading_records(path: Path):
    records = []
    in_fence = False
    in_html_comment = False
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    for index, line in enumerate(lines):
        if fence_re.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if stripped.startswith("<!--"):
            in_html_comment = "-->" not in stripped
            continue
        if in_html_comment:
            if "-->" in stripped:
                in_html_comment = False
            continue
        match = heading_re.match(line)
        if match:
            records.append((index, match.group(1), match.group(2), match.group(3) or ""))
    return lines, records

def alias_anchor(text: str) -> str:
    text = text.lower()
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"[^a-z0-9_\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text

def source_anchors(path: Path):
    _lines, records = heading_records(path)
    used = set()
    anchors = []
    for _index, _marks, body, _trail in records:
        text = plain_heading(body)
        primary = unique(slugify(text, "-"), used)
        alias = alias_anchor(text)
        anchors.append((primary, alias if alias and alias != primary else ""))
    return anchors

for translated in sorted(translated_dir.glob("*.md")):
    source = source_dir / translated.name
    if not source.exists():
        continue
    anchors = source_anchors(source)
    lines, records = heading_records(translated)
    if len(anchors) != len(records):
        print(f"heading count mismatch for {translated.name}: source={len(anchors)} translated={len(records)}", file=sys.stderr)
    insertions = {}
    for (anchor, alias), (index, marks, body, trail) in zip(anchors, records):
        if "{#" in body:
            continue
        heading_id = alias if "_" in alias else anchor
        lines[index] = f"{marks} {body}{trail} {{#{heading_id}}}"
        if alias and alias != heading_id:
            insertions.setdefault(index, []).append(f'<span id="{alias}"></span>')
    if insertions:
        expanded = []
        for index, line in enumerate(lines):
            expanded.extend(insertions.get(index, []))
            expanded.append(line)
        lines = expanded
    translated.write_text("\n".join(lines) + "\n", encoding="utf-8")
'@
    $script | & $Python - $SourceDirectory $TranslatedDirectory
}

if (-not $Python) {
    $VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $VenvPython)) {
        $BootstrapPython = (Get-Command python -ErrorAction Stop).Source
        & $BootstrapPython -m venv (Join-Path $Root '.venv')
    }
    $Python = $VenvPython
}

& $Python -m pip install --disable-pip-version-check -r (Join-Path $Root 'requirements.txt')

$StageRoot = Join-Path $Root 'tmp\site-src'
$EnglishStage = Join-Path $StageRoot 'en'
$ChineseStage = Join-Path $StageRoot 'zh'

Reset-Directory $EnglishStage
Reset-Directory $ChineseStage

Get-ChildItem -LiteralPath (Join-Path $Root 'docs') -File -Filter '*.md' |
    Copy-Item -Destination $EnglishStage
Get-ChildItem -LiteralPath (Join-Path $Root 'docs\zh-llm') -File -Filter '*.md' |
    Copy-Item -Destination $ChineseStage
Copy-SharedAssets $EnglishStage
Copy-SharedAssets $ChineseStage
Remove-MarkdownBom $EnglishStage
Remove-MarkdownBom $ChineseStage
Add-EnglishHeadingAnchors $EnglishStage $ChineseStage

& $Python -m mkdocs build -f (Join-Path $Root 'mkdocs.local.en.yml') --clean
& $Python -m mkdocs build -f (Join-Path $Root 'mkdocs.local.zh-llm.yml') --clean

$SiteRoot = Join-Path $Root 'site'
New-Item -ItemType Directory -Path $SiteRoot -Force | Out-Null
$index = @'
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Book of Verse</title>
  <meta http-equiv="refresh" content="0; url=zh/">
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 3rem; line-height: 1.6; }
    a { color: #b33a00; }
  </style>
</head>
<body>
  <h1>Book of Verse</h1>
  <p><a href="zh/">进入简体中文站点</a> / <a href="en/">Open English site</a></p>
</body>
</html>
'@
[System.IO.File]::WriteAllText((Join-Path $SiteRoot 'index.html'), $index, [System.Text.UTF8Encoding]::new($false))

Write-Host "Generated bilingual site:"
Write-Host "  $SiteRoot"
Write-Host "  http://127.0.0.1:$Port/zh/"
Write-Host "  http://127.0.0.1:$Port/en/"

if ($Serve) {
    Write-Host "Serving site. Press Ctrl+C to stop."
    & $Python -m http.server $Port --bind 127.0.0.1 --directory $SiteRoot
}
