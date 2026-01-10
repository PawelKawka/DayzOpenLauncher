# DayzOpenLauncher

A simple Python TUI launcher for Windows PowerShell and Linux terminals that allows you to browse DayZ servers, manage favorites, settings, and mods.

## Features

- Browse DayZ servers using DZSA API
- Manage favorite servers
- View server details
- Multi platform support (windows/linux)

## Screenshots

![DayzOpenLauncher Screenshot](assets/screen.png)

## Requirements

- Python 3.14
- Steam installed with dayz game

## API

DayzOpenLauncher uses the DZSAL API to download the list of servers. After that all live info is retrieved directly from the servers via the a2s module

## Installation & Uninstallation

### Linux

**Install:**

- Run:
	```bash
	sudo chmod +x install.sh && ./install.sh
	```

**Uninstall:**

- Run:
	```bash
	sudo chmod +x uninstall.sh && ./uninstall.sh
	```

### Windows

**Install:**

- Run:
	```powershell
	.\install.ps1
	```
- If you get a security error, use:
	```powershell
	Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force; .\install.ps1
	```

**Uninstall:**

- Run:
	```powershell
	.\uninstall.ps1
	```
- If you get a security error, use:
	```powershell
	Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force; .\uninstall.ps1
	```

---

## About
- The program is cross-platform (Windows/Linux).
- This is NOT a finished version; it may be limited and have bugs. Everything is in development.
- The Linux launcher and scripts have been tested on Debian/Ubuntu.

