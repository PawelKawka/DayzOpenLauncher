$ErrorActionPreference = "Stop"

Write-Host "--- DayzOpenLauncher Installation ---" -ForegroundColor Cyan

try {
    python --version
} catch {
    Write-Error "Python is not installed or not in PATH. Please install Python."
    exit 1
}

$SOURCE_DIR = (Get-Item .).FullName
$INSTALL_DIR = [System.IO.Path]::Combine($env:APPDATA, "DayzOpenLauncher_App")
$VENV_DIR = [System.IO.Path]::Combine($INSTALL_DIR, ".venvdol")
$DesktopPath = [System.IO.Path]::Combine([Environment]::GetFolderPath("Desktop"), "DayzOpenLauncher.lnk")

if ((Test-Path $INSTALL_DIR) -or (Test-Path $DesktopPath)) {
    $choice = Read-Host "Launcher already installed. Do you want to reinstall? (y/N)"
    if ($choice -notmatch "^[Yy]$") {
        Write-Host "Installation cancelled."
        exit 0
    }
}

if (-not (Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
}

$PathsToCopy = @("Source", "assets", "uninstall.ps1", "steam_appid.txt")
foreach ($p in $PathsToCopy) {
    if (Test-Path "$SOURCE_DIR\$p") {
        Copy-Item -Path "$SOURCE_DIR\$p" -Destination $INSTALL_DIR -Recurse -Force | Out-Null
        if ($p -eq "Source") {
            $LinuxFolder = [System.IO.Path]::Combine($INSTALL_DIR, "Source", "linux")
            if (Test-Path $LinuxFolder) {
                Remove-Item -Path $LinuxFolder -Recurse -Force | Out-Null
            }
        }
    }
}

if (-not (Test-Path $VENV_DIR)) {
    python -m venv $VENV_DIR
}

$RequiredModules = @("rich", "prompt_toolkit", "requests", "python-a2s")
$InstalledModules = & "$VENV_DIR\Scripts\pip.exe" list --format freeze
foreach ($module in $RequiredModules) {
    if ($InstalledModules -notmatch "(?i)$module==") {
        Write-Host "Installing $module..." -ForegroundColor Yellow
        & "$VENV_DIR\Scripts\pip.exe" install $module --quiet
    }
}

$batContent = @"
@echo off
cd /d "$INSTALL_DIR"
start "" "$VENV_DIR\Scripts\python.exe" Source\main.py
"@
$batContent | Out-File -FilePath "$INSTALL_DIR\run_launcher.bat" -Encoding ascii

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($DesktopPath)
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/c `"$INSTALL_DIR\run_launcher.bat`""
$Shortcut.WorkingDirectory = $INSTALL_DIR
$Shortcut.Description = "DayzOpenLauncher"
$IconPath = [System.IO.Path]::Combine($INSTALL_DIR, "assets", "icon.ico")
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = $IconPath
} else {
    $Shortcut.IconLocation = "shell32.dll,44"
}
$Shortcut.Save()

Write-Host "Done" -ForegroundColor Green
