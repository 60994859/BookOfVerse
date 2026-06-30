[CmdletBinding()]
param(
    [ValidateSet('all', 'en', 'zh', 'zh-llm')]
    [string]$Language = 'all',
    [string]$Python,
    [string]$Node
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $Root

if (-not $Python) {
    $VenvPython = Join-Path $Root '.venv\Scripts\python.exe'
    if (-not (Test-Path $VenvPython)) {
        $BootstrapPython = (Get-Command python -ErrorAction Stop).Source
        & $BootstrapPython -m venv (Join-Path $Root '.venv')
    }
    $Python = $VenvPython
}

& $Python -m pip install --disable-pip-version-check -r (Join-Path $Root 'requirements-pdf.txt')

if (-not $Node) {
    $NodeCommand = Get-Command node -ErrorAction SilentlyContinue
    if ($NodeCommand) {
        $Node = $NodeCommand.Source
    }
    else {
        $BundledNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
        if (Test-Path $BundledNode) {
            $Node = $BundledNode
            $BundledModules = Split-Path (Split-Path $BundledNode -Parent) -Parent
            $BundledModules = Join-Path $BundledModules 'node_modules'
            if (Test-Path (Join-Path $BundledModules 'playwright')) {
                $env:NODE_PATH = if ($env:NODE_PATH) { "$BundledModules;$env:NODE_PATH" } else { $BundledModules }
            }
        }
        else {
            throw 'Node.js was not found. Install Node.js 20+ or pass -Node with its executable path.'
        }
    }
}

$CodexModules = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
if ((-not (Test-Path (Join-Path $Root 'node_modules\playwright'))) -and (Test-Path (Join-Path $CodexModules 'playwright'))) {
    $env:NODE_PATH = if ($env:NODE_PATH) { "$CodexModules;$env:NODE_PATH" } else { $CodexModules }
    # The Codex runtime is installed through pnpm.  Its package symlinks are
    # intentionally omitted from this desktop workspace, so expose the core
    # package as an additional Node resolution root.
    $PlaywrightCore = Get-ChildItem (Join-Path $CodexModules '.pnpm') -Directory -Filter 'playwright-core@*' -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($PlaywrightCore) {
        $CoreModules = Join-Path $PlaywrightCore.FullName 'node_modules'
        $env:NODE_PATH = "$CoreModules;$env:NODE_PATH"
    }
}

if (-not (Test-Path (Join-Path $Root 'node_modules\playwright'))) {
    $BundledModulesPresent = $false
    if ($env:NODE_PATH) {
        $BundledModulesPresent = @($env:NODE_PATH -split ';' | Where-Object { Test-Path (Join-Path $_ 'playwright') }).Count -gt 0
    }
    if (-not $BundledModulesPresent) {
        $Npm = Get-Command npm -ErrorAction SilentlyContinue
        if (-not $Npm) {
            throw 'Playwright is not installed. Install Node.js/npm, then run: npm install --no-save playwright'
        }
        $env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'
        & $Npm.Source install --no-save --ignore-scripts playwright
    }
}

& $Python (Join-Path $Root 'scripts\build_pdf.py') --lang $Language --node $Node
