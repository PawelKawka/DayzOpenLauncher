$ErrorActionPreference = "Continue"

Write-Host "--- DayzOpenLauncher Uninstallation ---" -ForegroundColor Yellow

$INSTALL_DIR = [System.IO.Path]::Combine($env:APPDATA, "DayzOpenLauncher_App")
$CONFIG_DIR = [System.IO.Path]::Combine($env:APPDATA, "DayzOpenLauncher")

$ShortcutPath = [System.IO.Path]::Combine([Environment]::GetFolderPath("Desktop"), "DayzOpenLauncher.lnk")
if (Test-Path $ShortcutPath) {
    Write-Host "Removing Desktop shortcut..." -ForegroundColor Gray
    Remove-Item $ShortcutPath -Force
}

if (Test-Path $CONFIG_DIR) {
    $choice = Read-Host "Do you want to remove all settings and favorites? (y/N)"
    if ($choice -eq 'y' -or $choice -eq 'Y') {
        Write-Host "Removing settings folder..." -ForegroundColor Gray
        Remove-Item -Recurse -Force $CONFIG_DIR
    }
}

if (Test-Path $INSTALL_DIR) {
    Write-Host "Removing installation folder ($INSTALL_DIR)..." -ForegroundColor Gray
    Remove-Item -Recurse -Force $INSTALL_DIR
}

Write-Host "Done" -ForegroundColor Green
