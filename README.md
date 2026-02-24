<p align="center">
  <img src="banner.png" alt="AppVault Banner" width="400" style="height:auto;">
</p>

# AppVault

> **Professional Windows Application Backup & Reinstallation Tool**  
> Single-file Python architecture • Fully local • Modern dark-mode interface

---

## Overview

AppVault is a streamlined Windows desktop utility built to simplify application backup and system migration.

It enables users to:

- Scan installed applications from **HKLM** and **HKCU**
- Match applications against official **WinGet** packages
- Generate consolidated PowerShell installation commands
- Reinstall applications with live progress tracking and logging
- Export reusable migration templates and scripts

All operations are performed locally.  
No telemetry. No background services. No compiled executables required.

---

## Features

### System Scan

- Detects manually installed desktop applications  
- Excludes built-in Windows components  
- Extracts:
  - Application name  
  - Publisher  
  - Version  
  - Uninstall string  
- Fully searchable, sortable, and selectable interface  

---

### WinGet Integration

- Automatically matches installed applications to WinGet packages  
- Flags applications requiring manual installation  
- Suggests official sources when no WinGet package is available  

---

### Installation Modes

#### PowerShell Command Mode

- Generate consolidated WinGet install commands  
- Copy to clipboard  
- Export as `.ps1` script  
- Execute externally  

#### Direct Install Mode

- Per-application live status updates  
- Overall progress tracking  
- Real-time console logging  
- Structured error handling  

---

### Export Options

1. **JSON Template**  
   Portable configuration for cross-system migration  

2. **PowerShell Script (.ps1)**  
   Fully self-contained installation script  

3. **Full Migration Bundle**  
   JSON template + PowerShell script + human-readable app list  

---

### Logging

- Timestamped installation session logs  
- Success and failure codes recorded  
- Detailed error output for troubleshooting  

---

## Installation

### 1. Install Dependencies

```bash
pip install PySide6
