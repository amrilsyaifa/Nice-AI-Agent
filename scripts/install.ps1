# Nice AI Agent — installer for Windows
# Usage: iwr https://raw.githubusercontent.com/amrilsyaifa/Nice-AI-Agent/main/scripts/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo       = "amrilsyaifa/Nice-AI-Agent"
$Asset      = "nice-windows-x86_64.exe"
$InstallDir = "$env:LOCALAPPDATA\Programs\nice"
$BinPath    = "$InstallDir\nice.exe"

# ── Get latest version ────────────────────────────────────────────────────
Write-Host "Fetching latest release..."
$Release = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest"
$Version = $Release.tag_name

Write-Host "Installing nice $Version..."

# ── Download ──────────────────────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$DownloadUrl = "https://github.com/$Repo/releases/download/$Version/$Asset"
Invoke-WebRequest -Uri $DownloadUrl -OutFile $BinPath

# ── Add to PATH ───────────────────────────────────────────────────────────
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$InstallDir", "User")
    Write-Host "Added $InstallDir to your PATH."
    Write-Host "Restart your terminal for PATH changes to take effect."
}

# ── Verify ────────────────────────────────────────────────────────────────
Write-Host ""
$Ver = & $BinPath version
Write-Host "Installed: $Ver"
Write-Host ""
Write-Host "Get started:"
Write-Host "  nice config set api_key YOUR_API_KEY"
Write-Host "  nice ask 'What is 2 + 2?'"
