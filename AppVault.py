"""
╔══════════════════════════════════════════════════════════════════╗
║                        AppVault                                  ║
║         Windows Application Backup & Restore Tool               ║
║         Version 1.0.0  |  Production Ready                      ║
╚══════════════════════════════════════════════════════════════════╝

ARCHITECTURE:
  - Section 1: Constants & Theme
  - Section 2: Registry Scanner
  - Section 3: Winget Matcher
  - Section 4: Installation Engine
  - Section 5: Export / Import Engine
  - Section 6: UI Components
  - Section 7: Main Application Window
  - Section 8: Entry Point

Dependencies (pip install):
  pip install PySide6
"""

# ══════════════════════════════════════════════════════════════════
# SECTION 1: CONSTANTS & THEME
# ══════════════════════════════════════════════════════════════════

import sys
import os
import json
import subprocess
import threading
import winreg
import logging
import datetime
import re
import ctypes
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

# ── PySide6 imports ───────────────────────────────────────────────
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
        QCheckBox, QProgressBar, QTextEdit, QSplitter, QFrame,
        QScrollArea, QFileDialog, QMessageBox, QComboBox, QToolTip,
        QSizePolicy, QStatusBar, QTabWidget, QTreeWidget, QTreeWidgetItem,
        QAbstractItemView, QHeaderView, QStyleFactory
    )
    from PySide6.QtCore import (
        Qt, QThread, Signal, QObject, QTimer, QSize, QPoint
    )
    from PySide6.QtGui import (
        QFont, QColor, QPalette, QIcon, QPixmap, QPainter,
        QBrush, QLinearGradient, QFontDatabase, QCursor
    )
except ImportError:
    print("ERROR: PySide6 is required.\n  pip install PySide6")
    sys.exit(1)

APP_NAME = "AppVault"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Windows App Backup & Restore"

# ── Colour palette ─────────────────────────────────────────────────
class C:
    BG          = "#0f1117"
    SIDEBAR     = "#161b22"
    PANEL       = "#1c2230"
    PANEL2      = "#21283a"
    BORDER      = "#2d3748"
    ACCENT      = "#4f7ef0"
    ACCENT_HOV  = "#6b93f5"
    ACCENT_PRE  = "#3a5dc4"
    TEXT        = "#e2e8f0"
    TEXT_DIM    = "#718096"
    TEXT_MUTED  = "#4a5568"
    SUCCESS     = "#38a169"
    SUCCESS_BG  = "#1a2e1f"
    ERROR       = "#e53e3e"
    ERROR_BG    = "#2d1515"
    WARNING     = "#d69e2e"
    WARNING_BG  = "#2d2415"
    GREEN       = "#48bb78"
    RED         = "#fc8181"
    WHITE       = "#ffffff"

# ── Stylesheet ─────────────────────────────────────────────────────
QSS = f"""
QMainWindow, QWidget {{
    background-color: {C.BG};
    color: {C.TEXT};
    font-family: "Segoe UI", "Inter", "Arial";
    font-size: 13px;
}}
QLabel {{ color: {C.TEXT}; background: transparent; }}
QLabel#title  {{ font-size: 20px; font-weight: 700; color: {C.WHITE}; }}
QLabel#subtitle {{ font-size: 11px; color: {C.TEXT_DIM}; }}
QLabel#section {{ font-size: 14px; font-weight: 700; color: {C.WHITE}; padding: 4px 0; }}
QLabel#badge  {{ font-size: 11px; background: {C.ACCENT}; color: {C.WHITE};
                 border-radius: 8px; padding: 1px 8px; }}
QLabel#success_badge {{ background: {C.SUCCESS}; color: {C.WHITE};
                        border-radius: 8px; padding: 1px 8px; font-size: 11px; }}
QLabel#error_badge   {{ background: {C.ERROR};   color: {C.WHITE};
                        border-radius: 8px; padding: 1px 8px; font-size: 11px; }}

/* Sidebar */
QWidget#sidebar {{
    background: {C.SIDEBAR};
    border-right: 1px solid {C.BORDER};
    min-width: 220px;
    max-width: 220px;
}}
QPushButton#navbtn {{
    background: transparent;
    color: {C.TEXT_DIM};
    border: none;
    text-align: left;
    padding: 10px 20px;
    font-size: 13px;
    border-left: 3px solid transparent;
}}
QPushButton#navbtn:hover {{ color: {C.TEXT}; background: {C.PANEL}; }}
QPushButton#navbtn[active="true"] {{
    color: {C.ACCENT};
    background: {C.PANEL};
    border-left: 3px solid {C.ACCENT};
    font-weight: 600;
}}

/* Panels */
QFrame#panel {{
    background: {C.PANEL};
    border: 1px solid {C.BORDER};
    border-radius: 8px;
}}
QFrame#panel2 {{
    background: {C.PANEL2};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
}}

/* Buttons */
QPushButton {{
    background: {C.PANEL};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 13px;
}}
QPushButton:hover  {{ background: {C.PANEL2}; border-color: {C.ACCENT}; }}
QPushButton:pressed {{ background: {C.BG}; }}
QPushButton#primary {{
    background: {C.ACCENT};
    color: {C.WHITE};
    border: none;
    font-weight: 600;
}}
QPushButton#primary:hover  {{ background: {C.ACCENT_HOV}; }}
QPushButton#primary:pressed {{ background: {C.ACCENT_PRE}; }}
QPushButton#danger {{
    background: {C.ERROR};
    color: {C.WHITE};
    border: none;
    font-weight: 600;
}}
QPushButton#danger:hover {{ background: #c53030; }}
QPushButton#success {{
    background: {C.SUCCESS};
    color: {C.WHITE};
    border: none;
    font-weight: 600;
}}
QPushButton#success:hover {{ background: #2f855a; }}

/* Inputs */
QLineEdit {{
    background: {C.PANEL};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    padding: 7px 12px;
    font-size: 13px;
}}
QLineEdit:focus {{ border-color: {C.ACCENT}; }}
QLineEdit::placeholder {{ color: {C.TEXT_MUTED}; }}

/* List */
QListWidget {{
    background: {C.PANEL};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    outline: none;
}}
QListWidget::item {{
    padding: 6px 8px;
    border-bottom: 1px solid {C.BG};
}}
QListWidget::item:selected  {{ background: {C.PANEL2}; color: {C.WHITE}; }}
QListWidget::item:hover     {{ background: {C.PANEL2}; }}

/* Tree */
QTreeWidget {{
    background: {C.PANEL};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    outline: none;
}}
QTreeWidget::item {{ padding: 5px 4px; border-bottom: 1px solid {C.BG}; }}
QTreeWidget::item:selected {{ background: {C.PANEL2}; }}
QTreeWidget::item:hover    {{ background: {C.PANEL2}; }}
QHeaderView::section {{
    background: {C.SIDEBAR};
    color: {C.TEXT_DIM};
    border: none;
    border-bottom: 1px solid {C.BORDER};
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}}

/* Combo */
QComboBox {{
    background: {C.PANEL};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    padding: 6px 12px;
}}
QComboBox:hover {{ border-color: {C.ACCENT}; }}
QComboBox QAbstractItemView {{
    background: {C.PANEL};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    selection-background-color: {C.PANEL2};
}}

/* Scrollbar */
QScrollBar:vertical {{
    background: {C.BG};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {C.BORDER};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {C.TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* Progress */
QProgressBar {{
    background: {C.PANEL};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    text-align: center;
    color: {C.WHITE};
    font-size: 12px;
    height: 22px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {C.ACCENT}, stop:1 {C.ACCENT_HOV});
    border-radius: 6px;
}}

/* TextEdit */
QTextEdit {{
    background: {C.PANEL};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: 6px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 8px;
}}

/* Tab */
QTabWidget::pane  {{ border: 1px solid {C.BORDER}; border-radius: 6px; background: {C.PANEL}; }}
QTabBar::tab {{
    background: {C.SIDEBAR};
    color: {C.TEXT_DIM};
    border: 1px solid {C.BORDER};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 8px 18px;
    margin-right: 2px;
    font-size: 12px;
}}
QTabBar::tab:selected {{ background: {C.PANEL}; color: {C.WHITE}; font-weight: 600; }}
QTabBar::tab:hover    {{ color: {C.TEXT}; }}

/* Status bar */
QStatusBar {{ background: {C.SIDEBAR}; color: {C.TEXT_DIM}; border-top: 1px solid {C.BORDER}; font-size: 11px; }}
QSplitter::handle {{ background: {C.BORDER}; }}
QToolTip {{ background: {C.PANEL2}; color: {C.TEXT}; border: 1px solid {C.BORDER}; padding: 4px 8px; border-radius: 4px; }}
"""


# ══════════════════════════════════════════════════════════════════
# SECTION 2: REGISTRY SCANNER
# ══════════════════════════════════════════════════════════════════

@dataclass
class AppRecord:
    name: str
    publisher: str = ""
    version: str = ""
    uninstall_string: str = ""
    install_location: str = ""
    source: str = ""          # registry hive
    winget_id: str = ""
    winget_status: str = "unknown"   # unknown | found | not_found
    install_status: str = ""         # pending | installing | success | failed | manual
    install_error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "AppRecord":
        return AppRecord(**{k: v for k, v in d.items() if k in AppRecord.__dataclass_fields__})


# Apps to exclude — built-in Windows components
WINDOWS_BUILTIN_PATTERNS = [
    r"microsoft\.net", r"microsoft visual c\+\+", r"windows sdk",
    r"kb\d{6,}", r"update for microsoft", r"security update",
    r"microsoft\.directx", r"directx", r"windows subsystem",
    r"^microsoft windows", r"nvidia physx", r"^intel\(r\)",
    r"microsoft edge webview", r"windows pc health",
]

EXCLUDE_PUBLISHERS = {
    "microsoft corporation",
    "microsoft windows",
    "windows",
}

def _is_builtin(name: str, publisher: str) -> bool:
    nl = name.lower()
    for pat in WINDOWS_BUILTIN_PATTERNS:
        if re.search(pat, nl):
            return True
    if publisher.lower() in EXCLUDE_PUBLISHERS:
        # Allow common Microsoft apps that are user-installed
        allowed_ms = ["microsoft office", "microsoft 365", "visual studio code",
                      "microsoft teams", "onedrive", "onenote", "skype"]
        if not any(a in nl for a in allowed_ms):
            return True
    return False


def _read_hive(hive, flag: int, source_label: str) -> list[AppRecord]:
    results = []
    subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ | flag) as key:
            count = winreg.QueryInfoKey(key)[0]
            for i in range(count):
                try:
                    sub_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, sub_name, 0, winreg.KEY_READ | flag) as sub:
                        def _val(v, default=""):
                            try:
                                return winreg.QueryValueEx(sub, v)[0]
                            except Exception:
                                return default

                        name = _val("DisplayName")
                        if not name:
                            continue
                        publisher = _val("Publisher")
                        version   = _val("DisplayVersion")
                        uninstall = _val("UninstallString")
                        location  = _val("InstallLocation")
                        system    = int(_val("SystemComponent", 0))

                        if system:
                            continue
                        if _is_builtin(name, publisher):
                            continue

                        results.append(AppRecord(
                            name=name.strip(),
                            publisher=publisher.strip(),
                            version=version.strip(),
                            uninstall_string=uninstall.strip(),
                            install_location=location.strip(),
                            source=source_label,
                        ))
                except Exception:
                    continue
    except PermissionError:
        logging.warning("Permission denied reading %s", source_label)
    except Exception as e:
        logging.warning("Registry read error (%s): %s", source_label, e)
    return results


def scan_installed_apps() -> list[AppRecord]:
    """Scan HKLM (32 & 64 bit) and HKCU for installed applications."""
    apps: list[AppRecord] = []
    apps += _read_hive(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY, "HKLM x64")
    apps += _read_hive(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY, "HKLM x86")
    apps += _read_hive(winreg.HKEY_CURRENT_USER,  0,                       "HKCU")

    # Deduplicate by name (case-insensitive, keep first occurrence)
    seen = set()
    unique = []
    for a in apps:
        key = a.name.lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return sorted(unique, key=lambda x: x.name.lower())


# ══════════════════════════════════════════════════════════════════
# SECTION 3: WINGET MATCHER
# ══════════════════════════════════════════════════════════════════

def _winget_available() -> bool:
    try:
        r = subprocess.run(
            ["winget", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return r.returncode == 0
    except Exception:
        return False


def _search_winget(app_name: str) -> tuple[str, str]:
    """
    Returns (winget_id, status) where status is 'found' or 'not_found'.
    Tries an exact match first, then a partial search.
    """
    def _run(args):
        try:
            r = subprocess.run(
                args, capture_output=True, text=True, timeout=20,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return r.stdout
        except Exception:
            return ""

    # Try exact name match
    out = _run(["winget", "search", "--exact", "--name", app_name, "--accept-source-agreements"])
    pkg_id = _parse_winget_id(out, app_name)
    if pkg_id:
        return pkg_id, "found"

    # Fuzzy: first word of name
    short = app_name.split()[0] if app_name.split() else app_name
    out = _run(["winget", "search", "--name", short, "--accept-source-agreements"])
    pkg_id = _parse_winget_id(out, app_name)
    if pkg_id:
        return pkg_id, "found"

    return "", "not_found"


def _parse_winget_id(output: str, name: str) -> str:
    """Extract the best-matching package ID from winget search output."""
    lines = output.strip().splitlines()
    name_lower = name.lower()
    best_id = ""
    best_score = 0

    for line in lines:
        # winget output columns are space-separated, last non-space column is Source
        # Format: Name   Id   Version   Match   Source
        parts = line.split()
        if len(parts) < 2:
            continue
        # heuristic: ID usually contains a dot and no spaces
        for i, p in enumerate(parts):
            if "." in p and not p.startswith("-") and len(p) > 3:
                candidate_id = p
                # Score by how much the name matches
                row_text = " ".join(parts[:i]).lower()
                score = sum(1 for word in name_lower.split() if word in row_text)
                if score > best_score or (score == best_score and not best_id):
                    best_score = score
                    best_id = candidate_id
                break
    return best_id


class WingetMatcher(QThread):
    """Background thread: matches a batch of AppRecords to winget IDs."""
    progress = Signal(int, int)          # current, total
    app_matched = Signal(int, str, str)  # index, winget_id, status
    finished = Signal()

    def __init__(self, apps: list[AppRecord], indices: list[int]):
        super().__init__()
        self.apps = apps
        self.indices = indices
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        total = len(self.indices)
        for n, idx in enumerate(self.indices):
            if self._stop:
                break
            app = self.apps[idx]
            if app.winget_status == "found":
                self.progress.emit(n + 1, total)
                continue
            wid, status = _search_winget(app.name)
            self.app_matched.emit(idx, wid, status)
            self.progress.emit(n + 1, total)
        self.finished.emit()


# ══════════════════════════════════════════════════════════════════
# SECTION 4: INSTALLATION ENGINE
# ══════════════════════════════════════════════════════════════════

def build_winget_command(apps: list[AppRecord]) -> str:
    """Generate a single PowerShell command to install selected apps."""
    valid = [a for a in apps if a.winget_id]
    if not valid:
        return "# No apps with Winget IDs selected."
    lines = ["# AppVault — Generated Install Script",
             f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
             ""]
    for a in valid:
        lines.append(f'winget install --id {a.winget_id} --silent --accept-package-agreements --accept-source-agreements')
    return "\n".join(lines)


class InstallWorker(QThread):
    """Installs apps one by one using winget, emitting signals per app."""
    app_started  = Signal(int, str)         # index, name
    app_finished = Signal(int, str, str)    # index, status (success/failed/manual), error_msg
    overall_progress = Signal(int, int)     # done, total
    log_message  = Signal(str)
    all_done     = Signal()

    def __init__(self, apps: list[AppRecord], indices: list[int]):
        super().__init__()
        self.apps = apps
        self.indices = indices
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        total = len(self.indices)
        done = 0
        log_path = _log_path()
        logging.info("=== AppVault Install Session %s ===", datetime.datetime.now().isoformat())

        for idx in self.indices:
            if self._stop:
                break
            app = self.apps[idx]

            if app.winget_status != "found" or not app.winget_id:
                self.app_started.emit(idx, app.name)
                self.app_finished.emit(idx, "manual", "No Winget package available")
                done += 1
                self.overall_progress.emit(done, total)
                continue

            self.app_started.emit(idx, app.name)
            self.log_message.emit(f"[{_ts()}] Installing: {app.name} ({app.winget_id})")

            try:
                proc = subprocess.run(
                    [
                        "winget", "install",
                        "--id", app.winget_id,
                        "--silent",
                        "--accept-package-agreements",
                        "--accept-source-agreements",
                    ],
                    capture_output=True, text=True, timeout=300,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if proc.returncode == 0:
                    status = "success"
                    err = ""
                    self.log_message.emit(f"[{_ts()}] ✓ Success: {app.name}")
                    logging.info("SUCCESS: %s (%s)", app.name, app.winget_id)
                else:
                    status = "failed"
                    err = _extract_winget_error(proc.stdout + proc.stderr)
                    self.log_message.emit(f"[{_ts()}] ✗ Failed: {app.name} — {err}")
                    logging.error("FAILED: %s | code=%d | %s", app.name, proc.returncode, err)
            except subprocess.TimeoutExpired:
                status = "failed"
                err = "Installation timed out after 5 minutes."
                self.log_message.emit(f"[{_ts()}] ✗ Timeout: {app.name}")
                logging.error("TIMEOUT: %s", app.name)
            except Exception as e:
                status = "failed"
                err = str(e)
                logging.exception("EXCEPTION: %s", app.name)

            self.app_finished.emit(idx, status, err)
            done += 1
            self.overall_progress.emit(done, total)

        self.all_done.emit()


def _ts() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def _log_path() -> str:
    p = Path.home() / "AppVault_logs"
    p.mkdir(exist_ok=True)
    fname = datetime.datetime.now().strftime("install_%Y%m%d_%H%M%S.log")
    log_file = p / fname
    logging.basicConfig(
        filename=str(log_file),
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return str(log_file)


def _extract_winget_error(output: str) -> str:
    for line in output.splitlines():
        if any(kw in line.lower() for kw in ["error", "failed", "no package", "not found", "0x"]):
            return line.strip()[:120]
    return output.strip().splitlines()[-1][:120] if output.strip() else "Unknown error"


# ══════════════════════════════════════════════════════════════════
# SECTION 5: EXPORT / IMPORT ENGINE
# ══════════════════════════════════════════════════════════════════

def export_template(apps: list[AppRecord], filepath: str) -> None:
    data = {
        "appvault_version": APP_VERSION,
        "exported_at": datetime.datetime.now().isoformat(),
        "apps": [a.to_dict() for a in apps],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def export_ps1(apps: list[AppRecord], filepath: str) -> tuple[int, int]:
    """
    Write a self-contained PowerShell install script.
    Returns (winget_count, manual_count).
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    winget_apps  = [a for a in apps if a.winget_id]
    manual_apps  = [a for a in apps if not a.winget_id]

    lines = [
        "# ============================================================",
        f"#  AppVault — Auto-generated Install Script",
        f"#  Generated : {now}",
        f"#  Apps      : {len(winget_apps)} via Winget  |  {len(manual_apps)} manual",
        "# ============================================================",
        "",
        "# Requires winget (App Installer) — https://aka.ms/getwinget",
        "",
        "Write-Host '=== AppVault Install Script ===' -ForegroundColor Cyan",
        "Write-Host ''",
        "",
    ]

    if winget_apps:
        lines += [
            "# ── Winget Installs ─────────────────────────────────────────",
            "",
        ]
        for a in winget_apps:
            comment = f"# {a.name}"
            if a.publisher:
                comment += f"  |  {a.publisher}"
            if a.version:
                comment += f"  |  v{a.version}"
            lines.append(comment)
            lines.append(
                f'winget install --id {a.winget_id} --silent '
                f'--accept-package-agreements --accept-source-agreements'
            )
            lines.append("")

    if manual_apps:
        lines += [
            "# ── Manual Installs Required ────────────────────────────────",
            "# The following apps have no Winget package — install manually:",
            "",
        ]
        for a in manual_apps:
            lines.append(f"# {a.name}")
            if a.publisher:
                lines.append(f"#   Publisher : {a.publisher}")
            if a.version:
                lines.append(f"#   Version   : {a.version}")
            lines.append("")

    lines += [
        "Write-Host '' ",
        "Write-Host 'Done! Check output above for any errors.' -ForegroundColor Green",
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return len(winget_apps), len(manual_apps)


def export_bundle(apps: list[AppRecord], folder: str) -> dict:
    """
    Export a complete bundle into a folder:
      - appvault_template.json
      - install.ps1
      - app_list.txt  (human-readable)
    Returns a dict of {filename: filepath}.
    """
    os.makedirs(folder, exist_ok=True)
    out = {}

    # JSON template
    json_path = os.path.join(folder, "appvault_template.json")
    export_template(apps, json_path)
    out["appvault_template.json"] = json_path

    # PowerShell script
    ps1_path = os.path.join(folder, "install.ps1")
    export_ps1(apps, ps1_path)
    out["install.ps1"] = ps1_path

    # Human-readable list
    txt_path = os.path.join(folder, "app_list.txt")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"AppVault — Exported App List\nGenerated: {now}\n")
        f.write("=" * 60 + "\n\n")
        for a in apps:
            f.write(f"  {a.name}\n")
            if a.publisher: f.write(f"    Publisher  : {a.publisher}\n")
            if a.version:   f.write(f"    Version    : {a.version}\n")
            if a.winget_id: f.write(f"    Winget ID  : {a.winget_id}\n")
            else:           f.write(f"    Winget     : Manual install required\n")
            f.write("\n")
    out["app_list.txt"] = txt_path

    return out


def import_template(filepath: str) -> tuple[list[AppRecord], str]:
    """Returns (apps, error_message). error_message is empty on success."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        apps = [AppRecord.from_dict(d) for d in data.get("apps", [])]
        # Reset install states for the new machine
        for a in apps:
            a.install_status = ""
            a.install_error = ""
        return apps, ""
    except Exception as e:
        return [], str(e)


# ══════════════════════════════════════════════════════════════════
# SECTION 6: UI COMPONENTS
# ══════════════════════════════════════════════════════════════════

def _panel(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("panel")
    return f


def _label(text: str, object_name: str = "", parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    if object_name:
        lbl.setObjectName(object_name)
    return lbl


def _btn(text: str, style: str = "", parent=None) -> QPushButton:
    b = QPushButton(text, parent)
    if style:
        b.setObjectName(style)
    return b


def _separator(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color: {C.BORDER}; background: {C.BORDER}; border: none; max-height: 1px;")
    return f


def _badge(text: str, color: str = C.ACCENT, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setStyleSheet(
        f"background: {color}; color: white; border-radius: 8px; "
        f"padding: 1px 7px; font-size: 11px; font-weight: 600;"
    )
    lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return lbl


class AppListItem(QWidget):
    """Custom widget for each app row in the scan list."""
    check_changed = Signal()

    def __init__(self, app: AppRecord, parent=None):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        self.chk = QCheckBox()
        self.chk.setChecked(True)
        self.chk.stateChanged.connect(self.check_changed)
        layout.addWidget(self.chk)

        info = QVBoxLayout()
        info.setSpacing(1)
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        name_lbl = QLabel(self.app.name)
        name_lbl.setStyleSheet(f"color: {C.WHITE}; font-weight: 600; font-size: 13px;")
        name_row.addWidget(name_lbl)
        if self.app.version:
            ver = QLabel(f"v{self.app.version}")
            ver.setStyleSheet(f"color: {C.TEXT_DIM}; font-size: 11px;")
            name_row.addWidget(ver)
        name_row.addStretch()
        info.addLayout(name_row)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)
        if self.app.publisher:
            pub = QLabel(self.app.publisher)
            pub.setStyleSheet(f"color: {C.TEXT_DIM}; font-size: 11px;")
            meta_row.addWidget(pub)
        src = QLabel(self.app.source)
        src.setStyleSheet(f"color: {C.TEXT_MUTED}; font-size: 10px;")
        meta_row.addWidget(src)
        meta_row.addStretch()
        info.addLayout(meta_row)

        layout.addLayout(info)
        layout.addStretch()

        # Winget badge
        self.winget_badge = QLabel("")
        self.winget_badge.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.winget_badge)
        self._update_badge()

        # Install status indicator
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("font-size: 11px; min-width: 140px;")
        layout.addWidget(self.status_lbl)

    def _update_badge(self):
        if self.app.winget_status == "found":
            self.winget_badge.setText("● Winget")
            self.winget_badge.setStyleSheet(f"color: {C.GREEN}; font-size: 11px; font-weight: 600;")
        elif self.app.winget_status == "not_found":
            self.winget_badge.setText("● Manual")
            self.winget_badge.setStyleSheet(f"color: {C.WARNING}; font-size: 11px;")
        else:
            self.winget_badge.setText("○ Unknown")
            self.winget_badge.setStyleSheet(f"color: {C.TEXT_MUTED}; font-size: 11px;")

    def update_winget(self, winget_id: str, status: str):
        self.app.winget_id = winget_id
        self.app.winget_status = status
        self._update_badge()

    def update_status(self, status: str, error: str = ""):
        self.app.install_status = status
        self.app.install_error = error
        if status == "installing":
            self.status_lbl.setText("⟳ Installing…")
            self.status_lbl.setStyleSheet(f"color: {C.ACCENT}; font-size: 11px;")
        elif status == "success":
            self.status_lbl.setText("✓ Installed")
            self.status_lbl.setStyleSheet(f"color: {C.GREEN}; font-size: 11px; font-weight: 600;")
        elif status == "failed":
            self.status_lbl.setText("✗ Failed")
            self.status_lbl.setStyleSheet(f"color: {C.RED}; font-size: 11px; font-weight: 600;")
            if error:
                self.status_lbl.setToolTip(error)
        elif status == "manual":
            self.status_lbl.setText("⚠ Manual required")
            self.status_lbl.setStyleSheet(f"color: {C.WARNING}; font-size: 11px;")
        else:
            self.status_lbl.setText("")

    @property
    def is_checked(self) -> bool:
        return self.chk.isChecked()

    def set_checked(self, v: bool):
        self.chk.blockSignals(True)
        self.chk.setChecked(v)
        self.chk.blockSignals(False)


# ══════════════════════════════════════════════════════════════════
# SECTION 7: MAIN APPLICATION WINDOW
# ══════════════════════════════════════════════════════════════════

class AppVaultWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — {APP_TAGLINE}")
        self.setMinimumSize(1100, 720)
        self.resize(1200, 780)

        self._apps: list[AppRecord] = []
        self._item_widgets: list[AppListItem] = []
        self._scan_thread: Optional[QThread] = None
        self._match_thread: Optional[WingetMatcher] = None
        self._install_thread: Optional[InstallWorker] = None
        self._winget_ok = _winget_available()

        self._build_ui()
        self._apply_styles()
        self._update_status("Ready — click Scan to detect installed applications.")

    # ── UI Construction ───────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        # Content area (stacked pages via a dict of QWidgets)
        self._pages: dict[str, QWidget] = {}
        self._content_container = QWidget()
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._content_container, 1)

        self._pages["scan"]    = self._build_scan_page()
        self._pages["install"] = self._build_install_page()
        self._pages["results"] = self._build_results_page()
        self._pages["transfer"]= self._build_transfer_page()

        for w in self._pages.values():
            self._content_layout.addWidget(w)
            w.hide()

        self._show_page("scan")

        # Status bar
        self.setStatusBar(QStatusBar())

    def _build_sidebar(self) -> QWidget:
        sb = QWidget()
        sb.setObjectName("sidebar")
        layout = QVBoxLayout(sb)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo / branding
        brand = QWidget()
        brand.setStyleSheet(f"background: {C.BG}; border-bottom: 1px solid {C.BORDER};")
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(20, 18, 20, 18)
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {C.WHITE}; background: transparent;")
        tag = QLabel(APP_TAGLINE)
        tag.setStyleSheet(f"font-size: 10px; color: {C.ACCENT}; background: transparent; letter-spacing: 1px; text-transform: uppercase;")
        bl.addWidget(title)
        bl.addWidget(tag)
        layout.addWidget(brand)

        layout.addSpacing(12)

        nav_items = [
            ("🔍  System Scan",    "scan"),
            ("📦  Install Apps",   "install"),
            ("✅  Results",        "results"),
            ("🔄  Transfer / Export", "transfer"),
        ]

        self._nav_buttons: dict[str, QPushButton] = {}
        for label, key in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navbtn")
            btn.setCheckable(False)
            btn.clicked.connect(lambda _, k=key: self._show_page(k))
            layout.addWidget(btn)
            self._nav_buttons[key] = btn

        layout.addStretch()

        # Winget status
        wg_panel = QWidget()
        wg_panel.setStyleSheet(f"background: {C.BG}; border-top: 1px solid {C.BORDER};")
        wgl = QVBoxLayout(wg_panel)
        wgl.setContentsMargins(16, 12, 16, 12)
        if self._winget_ok:
            wl = QLabel("● Winget: Available")
            wl.setStyleSheet(f"color: {C.GREEN}; font-size: 11px; background: transparent;")
        else:
            wl = QLabel("⚠ Winget: Not Found")
            wl.setStyleSheet(f"color: {C.RED}; font-size: 11px; background: transparent;")
        wgl.addWidget(wl)
        ver_l = QLabel(f"AppVault v{APP_VERSION}")
        ver_l.setStyleSheet(f"color: {C.TEXT_MUTED}; font-size: 10px; background: transparent;")
        wgl.addWidget(ver_l)
        layout.addWidget(wg_panel)

        return sb

    # ── Scan Page ─────────────────────────────────────────────────

    def _build_scan_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        hdr.addWidget(_label("System Scan", "section"))
        hdr.addStretch()
        self._app_count_badge = _badge("0 apps", C.TEXT_MUTED)
        hdr.addWidget(self._app_count_badge)
        layout.addLayout(hdr)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.scan_btn = _btn("🔍  Scan Now", "primary")
        self.scan_btn.setFixedHeight(36)
        self.scan_btn.clicked.connect(self._do_scan)
        toolbar.addWidget(self.scan_btn)

        self.match_btn = _btn("⚡  Match Winget IDs", "")
        self.match_btn.setFixedHeight(36)
        self.match_btn.setEnabled(False)
        self.match_btn.clicked.connect(self._do_match)
        toolbar.addWidget(self.match_btn)

        toolbar.addSpacing(16)

        self.sel_all_btn = _btn("☑  Select All")
        self.sel_all_btn.setFixedHeight(36)
        self.sel_all_btn.clicked.connect(lambda: self._set_all_checked(True))
        toolbar.addWidget(self.sel_all_btn)

        self.sel_none_btn = _btn("☐  Deselect All")
        self.sel_none_btn.setFixedHeight(36)
        self.sel_none_btn.clicked.connect(lambda: self._set_all_checked(False))
        toolbar.addWidget(self.sel_none_btn)

        toolbar.addStretch()

        sort_lbl = QLabel("Sort:")
        sort_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; font-size: 12px;")
        toolbar.addWidget(sort_lbl)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name ↑", "Name ↓", "Publisher", "Source"])
        self.sort_combo.setFixedWidth(120)
        self.sort_combo.currentIndexChanged.connect(self._do_sort)
        toolbar.addWidget(self.sort_combo)

        layout.addLayout(toolbar)

        # Search
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔎  Search by name or publisher…")
        self.search_input.setFixedHeight(36)
        self.search_input.textChanged.connect(self._do_filter)
        search_row.addWidget(self.search_input)
        layout.addLayout(search_row)

        # Match progress
        self.match_progress = QProgressBar()
        self.match_progress.setFixedHeight(6)
        self.match_progress.hide()
        layout.addWidget(self.match_progress)

        # App list
        self.app_list = QListWidget()
        self.app_list.setAlternatingRowColors(False)
        self.app_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.app_list.setSpacing(2)
        layout.addWidget(self.app_list, 1)

        # Bottom actions
        bottom = QHBoxLayout()
        self.proceed_install_btn = _btn("📦  Proceed to Install →", "primary")
        self.proceed_install_btn.setFixedHeight(38)
        self.proceed_install_btn.setEnabled(False)
        self.proceed_install_btn.clicked.connect(lambda: self._show_page("install"))
        bottom.addStretch()
        bottom.addWidget(self.proceed_install_btn)
        layout.addLayout(bottom)

        return page

    # ── Install Page ──────────────────────────────────────────────

    def _build_install_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(_label("Install Applications", "section"))

        # Tab: Command | Direct Install
        self.install_tabs = QTabWidget()

        # — Command tab —
        cmd_tab = QWidget()
        cmd_layout = QVBoxLayout(cmd_tab)
        cmd_layout.setContentsMargins(16, 16, 16, 16)
        cmd_layout.setSpacing(12)

        cmd_layout.addWidget(QLabel("Generated PowerShell command to install all selected apps via Winget:"))
        self.cmd_text = QTextEdit()
        self.cmd_text.setReadOnly(True)
        self.cmd_text.setMinimumHeight(200)
        self.cmd_text.setPlaceholderText("Scan and match apps first, then return here for the generated command.")
        cmd_layout.addWidget(self.cmd_text, 1)

        copy_row = QHBoxLayout()
        copy_btn = _btn("📋  Copy Command", "primary")
        copy_btn.clicked.connect(self._copy_command)
        regen_btn = _btn("🔄  Regenerate")
        regen_btn.clicked.connect(self._regen_command)
        save_ps1_btn = _btn("💾  Save as .ps1…")
        save_ps1_btn.clicked.connect(self._do_export_ps1)
        copy_row.addWidget(copy_btn)
        copy_row.addWidget(regen_btn)
        copy_row.addWidget(save_ps1_btn)
        copy_row.addStretch()
        cmd_layout.addLayout(copy_row)

        self.install_tabs.addTab(cmd_tab, "  PowerShell Command  ")

        # — Direct Install tab —
        direct_tab = QWidget()
        direct_layout = QVBoxLayout(direct_tab)
        direct_layout.setContentsMargins(16, 16, 16, 16)
        direct_layout.setSpacing(12)

        if not self._winget_ok:
            warn = QLabel("⚠  Winget is not installed on this system.\n"
                          "   Visit: https://aka.ms/getwinget to install it.")
            warn.setStyleSheet(f"color: {C.WARNING}; background: {C.WARNING_BG}; "
                               f"padding: 12px; border-radius: 6px;")
            direct_layout.addWidget(warn)

        direct_layout.addWidget(QLabel("Selected apps will be installed one-by-one. Apps without Winget IDs will be skipped."))

        self.overall_prog = QProgressBar()
        self.overall_prog.setFixedHeight(22)
        self.overall_prog.setFormat("Ready")
        direct_layout.addWidget(self.overall_prog)

        self.install_log = QTextEdit()
        self.install_log.setReadOnly(True)
        self.install_log.setMinimumHeight(160)
        self.install_log.setPlaceholderText("Installation log will appear here…")
        direct_layout.addWidget(self.install_log, 1)

        install_row = QHBoxLayout()
        self.start_install_btn = _btn("▶  Start Installation", "primary")
        self.start_install_btn.setFixedHeight(38)
        self.start_install_btn.clicked.connect(self._start_install)
        self.stop_install_btn = _btn("⏹  Stop", "danger")
        self.stop_install_btn.setFixedHeight(38)
        self.stop_install_btn.setEnabled(False)
        self.stop_install_btn.clicked.connect(self._stop_install)
        install_row.addWidget(self.start_install_btn)
        install_row.addWidget(self.stop_install_btn)
        install_row.addStretch()
        direct_layout.addLayout(install_row)

        self.install_tabs.addTab(direct_tab, "  Direct Install  ")

        layout.addWidget(self.install_tabs, 1)

        bottom = QHBoxLayout()
        view_results = _btn("📊  View Results →", "success")
        view_results.setFixedHeight(36)
        view_results.clicked.connect(lambda: self._show_page("results"))
        bottom.addStretch()
        bottom.addWidget(view_results)
        layout.addLayout(bottom)

        return page

    # ── Results Page ──────────────────────────────────────────────

    def _build_results_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        hdr.addWidget(_label("Installation Results", "section"))
        hdr.addStretch()
        save_log_btn = _btn("💾  Save Log")
        save_log_btn.clicked.connect(self._save_log)
        hdr.addWidget(save_log_btn)
        layout.addLayout(hdr)

        # Summary row
        self.results_summary = QWidget()
        sum_layout = QHBoxLayout(self.results_summary)
        sum_layout.setContentsMargins(0, 0, 0, 0)
        sum_layout.setSpacing(12)
        self.res_success_badge = _badge("✓ 0 Installed", C.SUCCESS)
        self.res_failed_badge  = _badge("✗ 0 Failed", C.ERROR)
        self.res_manual_badge  = _badge("⚠ 0 Manual", C.WARNING)
        sum_layout.addWidget(self.res_success_badge)
        sum_layout.addWidget(self.res_failed_badge)
        sum_layout.addWidget(self.res_manual_badge)
        sum_layout.addStretch()
        layout.addWidget(self.results_summary)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Application", "Status", "Details"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.results_tree.header().resizeSection(1, 120)
        self.results_tree.setAlternatingRowColors(False)
        layout.addWidget(self.results_tree, 1)

        # Manual install section
        layout.addWidget(_separator())
        layout.addWidget(_label("⚠  Manual Install Required", "section"))
        self.manual_list = QListWidget()
        self.manual_list.setMaximumHeight(140)
        layout.addWidget(self.manual_list)

        return page

    # ── Transfer Page ─────────────────────────────────────────────

    def _build_transfer_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        layout.addWidget(_label("Export / Import App List", "section"))
        layout.addWidget(QLabel(
            "Export your selected apps as a JSON template, a ready-to-run PowerShell script, or a complete bundle — "
            "then import on another PC to restore everything."
        ))

        # ── Export section ──────────────────────────────────────────
        layout.addWidget(_label("📤  Export Options", "section"))

        export_grid = QHBoxLayout()
        export_grid.setSpacing(12)

        # Card helper
        def _exp_card(icon, title, desc, btn_label, btn_style, handler):
            card = _panel()
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 16, 18, 16)
            cl.setSpacing(8)
            ttl = QLabel(f"{icon}  {title}")
            ttl.setStyleSheet(f"color: {C.WHITE}; font-size: 13px; font-weight: 700; background: transparent;")
            cl.addWidget(ttl)
            d = QLabel(desc)
            d.setStyleSheet(f"color: {C.TEXT_DIM}; font-size: 11px; background: transparent;")
            d.setWordWrap(True)
            cl.addWidget(d)
            cl.addStretch()
            b = _btn(btn_label, btn_style)
            b.setFixedHeight(34)
            b.clicked.connect(handler)
            cl.addWidget(b)
            return card

        export_grid.addWidget(_exp_card(
            "📋", "JSON Template",
            "Portable app list. Import this on another PC to restore the same apps automatically.",
            "Export JSON…", "primary", self._do_export_json
        ))
        export_grid.addWidget(_exp_card(
            "⚡", "PowerShell Script (.ps1)",
            "Runnable install script. Double-click or run in PowerShell — no AppVault needed.",
            "Export .ps1…", "primary", self._do_export_ps1
        ))
        export_grid.addWidget(_exp_card(
            "📦", "Full Bundle (folder)",
            "Exports JSON template + .ps1 script + plain-text app list into one folder.",
            "Export Bundle…", "success", self._do_export_bundle
        ))
        layout.addLayout(export_grid)

        # Preview box
        prev_hdr = QHBoxLayout()
        prev_hdr.addWidget(_label("Preview — install.ps1", "section"))
        prev_hdr.addStretch()
        copy_prev_btn = _btn("📋  Copy")
        copy_prev_btn.setFixedHeight(30)
        copy_prev_btn.clicked.connect(self._copy_ps1_preview)
        prev_hdr.addWidget(copy_prev_btn)
        layout.addLayout(prev_hdr)

        self.ps1_preview = QTextEdit()
        self.ps1_preview.setReadOnly(True)
        self.ps1_preview.setMinimumHeight(160)
        self.ps1_preview.setPlaceholderText(
            "Scan apps and (optionally) match Winget IDs, then the generated script will appear here…"
        )
        layout.addWidget(self.ps1_preview, 1)

        # ── Import section ──────────────────────────────────────────
        layout.addWidget(_separator())
        layout.addWidget(_label("📥  Import App List", "section"))

        imp_panel = _panel()
        imp_layout = QVBoxLayout(imp_panel)
        imp_layout.setContentsMargins(20, 16, 20, 16)
        imp_layout.setSpacing(10)
        imp_layout.addWidget(QLabel(
            "Load a previously exported JSON template. The app list will be populated and "
            "Winget matching will begin automatically on this machine."
        ))
        imp_row = QHBoxLayout()
        self.import_path_lbl = QLabel("No file selected")
        self.import_path_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; font-size: 12px;")
        imp_row.addWidget(self.import_path_lbl, 1)
        import_btn = _btn("Browse…")
        import_btn.clicked.connect(self._do_import)
        imp_row.addWidget(import_btn)
        imp_layout.addLayout(imp_row)
        layout.addWidget(imp_panel)

        return page

    # ── Navigation ────────────────────────────────────────────────

    def _show_page(self, key: str):
        for k, w in self._pages.items():
            w.show() if k == key else w.hide()
        for k, btn in self._nav_buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if key == "install":
            self._regen_command()
        if key == "results":
            self._refresh_results()
        if key == "transfer":
            self._refresh_ps1_preview()

    # ── Actions: Scan ─────────────────────────────────────────────

    def _do_scan(self):
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning…")
        self._update_status("Scanning registry…")
        self.app_list.clear()
        self._apps = []
        self._item_widgets = []

        class ScanThread(QThread):
            done = Signal(list)
            def run(self_):
                self_.done.emit(scan_installed_apps())

        self._scan_thread = ScanThread()
        self._scan_thread.done.connect(self._on_scan_done)
        self._scan_thread.start()

    def _on_scan_done(self, apps: list[AppRecord]):
        self._apps = apps
        self._item_widgets = []
        self.app_list.clear()

        for app in apps:
            widget = AppListItem(app)
            widget.check_changed.connect(self._on_check_changed)
            item = QListWidgetItem(self.app_list)
            item.setSizeHint(widget.sizeHint())
            self.app_list.addItem(item)
            self.app_list.setItemWidget(item, widget)
            self._item_widgets.append(widget)

        count = len(apps)
        self._app_count_badge.setText(f"{count} apps")
        self._app_count_badge.setStyleSheet(
            f"background: {C.ACCENT}; color: white; border-radius: 8px; "
            f"padding: 1px 7px; font-size: 11px; font-weight: 600;"
        )
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍  Scan Again")
        self.match_btn.setEnabled(count > 0)
        self.proceed_install_btn.setEnabled(count > 0)
        self._update_status(f"Found {count} installed applications.")

    def _set_all_checked(self, state: bool):
        for w in self._item_widgets:
            if not w.isHidden():
                w.set_checked(state)

    def _do_filter(self, text: str):
        text = text.lower()
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            widget = self._item_widgets[i]
            if text in widget.app.name.lower() or text in widget.app.publisher.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def _do_sort(self, idx: int):
        sorts = {
            0: lambda a: a.name.lower(),
            1: lambda a: a.name.lower(),
            2: lambda a: a.publisher.lower(),
            3: lambda a: a.source.lower(),
        }
        rev = idx == 1
        self._apps.sort(key=sorts.get(idx, sorts[0]), reverse=rev)
        # Rebuild list with sorted order
        self._on_scan_done(self._apps)

    def _on_check_changed(self):
        selected = sum(1 for w in self._item_widgets if w.is_checked)
        self._update_status(f"{selected} of {len(self._apps)} apps selected.")

    # ── Actions: Winget Matching ──────────────────────────────────

    def _do_match(self):
        if not self._winget_ok:
            QMessageBox.warning(self, "Winget Not Found",
                "Winget is not installed on this system.\n\nVisit: https://aka.ms/getwinget")
            return

        indices = [i for i, w in enumerate(self._item_widgets) if w.is_checked]
        if not indices:
            QMessageBox.information(self, "No Apps Selected", "Select apps first.")
            return

        self.match_btn.setEnabled(False)
        self.match_btn.setText("Matching…")
        self.match_progress.show()
        self.match_progress.setMaximum(len(indices))
        self.match_progress.setValue(0)
        self._update_status(f"Matching {len(indices)} apps to Winget…")

        self._match_thread = WingetMatcher(self._apps, indices)
        self._match_thread.progress.connect(self._on_match_progress)
        self._match_thread.app_matched.connect(self._on_app_matched)
        self._match_thread.finished.connect(self._on_match_done)
        self._match_thread.start()

    def _on_match_progress(self, curr: int, total: int):
        self.match_progress.setValue(curr)
        self.match_progress.setFormat(f"Matching {curr}/{total}…")

    def _on_app_matched(self, idx: int, winget_id: str, status: str):
        if idx < len(self._item_widgets):
            self._item_widgets[idx].update_winget(winget_id, status)

    def _on_match_done(self):
        self.match_btn.setEnabled(True)
        self.match_btn.setText("⚡  Rematch Winget IDs")
        self.match_progress.hide()
        found = sum(1 for a in self._apps if a.winget_status == "found")
        manual = sum(1 for a in self._apps if a.winget_status == "not_found")
        self._update_status(f"Matching complete — {found} via Winget, {manual} manual install required.")

    # ── Actions: Command Generation ───────────────────────────────

    def _regen_command(self):
        selected = [self._apps[i] for i, w in enumerate(self._item_widgets) if w.is_checked]
        cmd = build_winget_command(selected)
        self.cmd_text.setPlainText(cmd)

    def _copy_command(self):
        QApplication.clipboard().setText(self.cmd_text.toPlainText())
        self._update_status("Command copied to clipboard.")

    # ── Actions: Direct Install ───────────────────────────────────

    def _start_install(self):
        if not self._winget_ok:
            QMessageBox.warning(self, "Winget Required",
                "Winget is not available.\nVisit https://aka.ms/getwinget to install it.")
            return

        indices = [i for i, w in enumerate(self._item_widgets) if w.is_checked]
        if not indices:
            QMessageBox.information(self, "Nothing Selected", "Select at least one app.")
            return

        self.start_install_btn.setEnabled(False)
        self.stop_install_btn.setEnabled(True)
        self.overall_prog.setMaximum(len(indices))
        self.overall_prog.setValue(0)
        self.overall_prog.setFormat("Starting…")
        self.install_log.clear()

        self._install_thread = InstallWorker(self._apps, indices)
        self._install_thread.app_started.connect(self._on_app_started)
        self._install_thread.app_finished.connect(self._on_app_finished)
        self._install_thread.overall_progress.connect(self._on_install_progress)
        self._install_thread.log_message.connect(self.install_log.append)
        self._install_thread.all_done.connect(self._on_install_done)
        self._install_thread.start()

    def _on_app_started(self, idx: int, name: str):
        if idx < len(self._item_widgets):
            self._item_widgets[idx].update_status("installing")
        self._update_status(f"Installing: {name}…")

    def _on_app_finished(self, idx: int, status: str, error: str):
        if idx < len(self._item_widgets):
            self._item_widgets[idx].update_status(status, error)

    def _on_install_progress(self, done: int, total: int):
        self.overall_prog.setValue(done)
        self.overall_prog.setFormat(f"{done} / {total} apps")

    def _on_install_done(self):
        self.start_install_btn.setEnabled(True)
        self.stop_install_btn.setEnabled(False)
        self._update_status("Installation complete. View Results for details.")
        self._refresh_results()
        QMessageBox.information(self, "Installation Complete",
            "Installation finished!\n\nSwitch to the Results page for a full breakdown.")

    def _stop_install(self):
        if self._install_thread:
            self._install_thread.stop()
        self.stop_install_btn.setEnabled(False)

    # ── Actions: Results ──────────────────────────────────────────

    def _refresh_results(self):
        self.results_tree.clear()
        self.manual_list.clear()

        success_grp = QTreeWidgetItem(self.results_tree, ["✅  Successfully Installed", "", ""])
        success_grp.setForeground(0, QColor(C.GREEN))
        success_grp.setFont(0, QFont("Segoe UI", 12, QFont.Weight.Bold))

        failed_grp = QTreeWidgetItem(self.results_tree, ["❌  Failed", "", ""])
        failed_grp.setForeground(0, QColor(C.RED))
        failed_grp.setFont(0, QFont("Segoe UI", 12, QFont.Weight.Bold))

        n_success = n_failed = n_manual = 0
        for app in self._apps:
            if app.install_status == "success":
                child = QTreeWidgetItem(success_grp, [app.name, "✓ Installed", app.winget_id])
                child.setForeground(0, QColor(C.GREEN))
                child.setForeground(1, QColor(C.GREEN))
                n_success += 1
            elif app.install_status == "failed":
                child = QTreeWidgetItem(failed_grp, [app.name, "✗ Failed", app.install_error])
                child.setForeground(0, QColor(C.RED))
                child.setForeground(1, QColor(C.RED))
                child.setForeground(2, QColor(C.RED))
                child.setToolTip(2, app.install_error)
                n_failed += 1
            elif app.install_status == "manual":
                self.manual_list.addItem(f"⚠  {app.name}   —   {app.publisher}")
                n_manual += 1

        self.results_tree.expandAll()
        self.res_success_badge.setText(f"✓ {n_success} Installed")
        self.res_failed_badge.setText(f"✗ {n_failed} Failed")
        self.res_manual_badge.setText(f"⚠ {n_manual} Manual")

        if n_success == 0 and n_failed == 0 and n_manual == 0:
            placeholder = QTreeWidgetItem(self.results_tree, ["No installation data yet. Run an installation first.", "", ""])
            placeholder.setForeground(0, QColor(C.TEXT_DIM))

    def _save_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Log",
            str(Path.home() / "AppVault_results.log"), "Log Files (*.log);;All Files (*)")
        if path:
            lines = [
                f"AppVault Results Log — {datetime.datetime.now().isoformat()}",
                "=" * 60,
            ]
            for app in self._apps:
                if app.install_status:
                    lines.append(f"[{app.install_status.upper():10}]  {app.name}  ({app.winget_id})")
                    if app.install_error:
                        lines.append(f"              Error: {app.install_error}")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self._update_status(f"Log saved to {path}")

    # ── Actions: Export / Import ──────────────────────────────────

    def _selected_apps(self) -> list[AppRecord]:
        return [self._apps[i] for i, w in enumerate(self._item_widgets) if w.is_checked]

    def _check_has_selection(self) -> bool:
        if not self._selected_apps():
            QMessageBox.information(self, "Nothing Selected",
                "Scan apps and check the ones you want to export first.")
            return False
        return True

    def _refresh_ps1_preview(self):
        """Render the PS1 script into the preview box without saving."""
        selected = self._selected_apps()
        if not selected:
            self.ps1_preview.setPlaceholderText(
                "No apps selected. Scan apps and check the ones you want to export.")
            self.ps1_preview.clear()
            return
        import tempfile, os as _os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8")
        tmp.close()
        try:
            export_ps1(selected, tmp.name)
            with open(tmp.name, "r", encoding="utf-8") as f:
                self.ps1_preview.setPlainText(f.read())
        finally:
            try:
                _os.unlink(tmp.name)
            except Exception:
                pass

    def _copy_ps1_preview(self):
        QApplication.clipboard().setText(self.ps1_preview.toPlainText())
        self._update_status("PowerShell script copied to clipboard.")

    def _do_export_json(self):
        if not self._check_has_selection():
            return
        selected = self._selected_apps()
        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON Template",
            str(Path.home() / "appvault_template.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        export_template(selected, path)
        self._update_status(f"JSON template saved — {len(selected)} apps → {path}")
        QMessageBox.information(self, "Exported",
            f"✅  JSON template saved with {len(selected)} apps:\n\n{path}")

    def _do_export_ps1(self):
        if not self._check_has_selection():
            return
        selected = self._selected_apps()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Install Script",
            str(Path.home() / "appvault_install.ps1"),
            "PowerShell Script (*.ps1);;All Files (*)"
        )
        if not path:
            return
        wg, manual = export_ps1(selected, path)
        self._update_status(f"PowerShell script saved — {wg} winget, {manual} manual → {path}")
        QMessageBox.information(self, "Saved",
            f"✅  install.ps1 saved:\n\n{path}\n\n"
            f"  • {wg} apps via Winget\n"
            f"  • {manual} apps listed as manual install\n\n"
            "Run it in PowerShell to install everything.")

    def _do_export_bundle(self):
        if not self._check_has_selection():
            return
        selected = self._selected_apps()
        folder = QFileDialog.getExistingDirectory(
            self, "Choose Export Folder", str(Path.home())
        )
        if not folder:
            return
        bundle_dir = os.path.join(folder, f"AppVault_Bundle_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}")
        out = export_bundle(selected, bundle_dir)
        self._update_status(f"Bundle exported to {bundle_dir}")
        file_list = "\n".join(f"  • {k}" for k in out)
        QMessageBox.information(self, "Bundle Exported",
            f"✅  {len(selected)} apps exported to:\n\n{bundle_dir}\n\n"
            f"Files created:\n{file_list}\n\n"
            "Copy the folder to your new PC and run install.ps1, "
            "or import appvault_template.json into AppVault.")

    def _do_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import App Template",
            str(Path.home()), "JSON (*.json);;All Files (*)")
        if not path:
            return
        apps, err = import_template(path)
        if err:
            QMessageBox.critical(self, "Import Failed", f"Could not parse template:\n{err}")
            return
        self.import_path_lbl.setText(os.path.basename(path))
        self._apps = apps
        self._on_scan_done(apps)
        self._show_page("scan")
        self._update_status(f"Imported {len(apps)} apps from template. Running Winget matching…")
        if self._winget_ok:
            QTimer.singleShot(500, self._do_match)
        else:
            QMessageBox.information(self, "Import Complete",
                f"Imported {len(apps)} apps.\n\nWinget is not available on this machine — "
                "install it to enable automatic installation.")

    # ── Helpers ───────────────────────────────────────────────────

    def _update_status(self, msg: str):
        self.statusBar().showMessage(f"  {msg}")

    def _apply_styles(self):
        self.setStyleSheet(QSS)

    def closeEvent(self, event):
        for t in [self._scan_thread, self._match_thread, self._install_thread]:
            if t and t.isRunning():
                try:
                    t.stop()
                except Exception:
                    pass
                t.wait(2000)
        event.accept()


# ══════════════════════════════════════════════════════════════════
# SECTION 8: ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def _request_admin():
    """Re-launch with admin rights if needed (Windows only)."""
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            # Re-launch elevated
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
    except Exception:
        pass  # Fail silently — registry access degrades gracefully


def main():
    # Only request elevation on Windows
    if sys.platform == "win32":
        _request_admin()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Global font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = AppVaultWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()