# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path


def _find_project_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "src").is_dir() and (candidate / "bin").is_dir():
            return candidate
    return start


spec_dir = Path(SPECPATH).resolve()
project_root = _find_project_root(spec_dir)
icon_file = project_root / "assets" / "app.ico"
icon_path = icon_file if icon_file.exists() else None

a = Analysis(
    [str(project_root / "bin" / "run.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[(str(icon_file), "assets")] if icon_path else [],
    hiddenimports=[
        "pygame",
        "requests",
        "openai",
        "audioplayer",
        "pyautogui",
        "pyscreeze",
        "pymsgbox",
        "pytweening",
        "mouseinfo",
        "pygetwindow",
        "pyperclip",
        "keyboard",
        "PIL",
        "PIL.Image",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="run_debug",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(icon_path)] if icon_path else None,
)
