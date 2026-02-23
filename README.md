# AppVault

> Professional Windows Application Backup & Reinstallation Tool  
> Single-file Python. Fully local. Clean dark-mode interface.

---

## Overview

AppVault is a professional desktop tool for Windows that helps users:

- Scan installed applications (HKLM + HKCU)
- Match apps with WinGet packages
- Generate consolidated PowerShell install commands
- Directly reinstall apps with live progress and logging
- Export templates and scripts for migration to other systems

Everything runs locally, no telemetry, no background services, no EXE required.

---

## Features

### System Scan
- Detects manually installed applications
- Excludes built-in Windows apps
- Extracts app name, publisher, version, uninstall string
- Searchable, sortable, selectable list

### WinGet Integration
- Auto-matches installed apps to WinGet packages
- Flags apps that require manual installation
- Suggests official website if no package exists

### Installation Options
- **PowerShell Command Mode:** copy, save `.ps1`, or run outside AppVault  
- **Direct Install Mode:** per-app live status, overall progress, logs  

### Export Options
1. **JSON Template:** portable across machines  
2. **PowerShell Script (.ps1):** fully self-contained installer  
3. **Full Migration Bundle:** JSON + PS1 + human-readable app list  

### Logging
- Timestamped log files for each install session  
- Includes success/failure codes and error messages  

---

## Why AppVault?

- Single `.py` file, fully portable  
- Modular, production-ready architecture  
- Clean professional dark-mode interface  
- Secure: no telemetry, no cloud dependency, elevation only when needed  

---

## Requirements

- Windows 10 / 11  
- Python 3.9+  
- WinGet installed  
- Administrator privileges recommended  

---

## Installation

```bash
pip install -r requirements.txt
python AppVault.py
