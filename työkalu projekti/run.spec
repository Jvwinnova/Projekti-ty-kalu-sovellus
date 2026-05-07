# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path


def _find_project_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "src").is_dir() and (candidate / "bin").is_dir():
            return candidate
    return start


spec_dir = Path(SPECPATH).resolve()
project_root = _find_project_root(spec_dir)
repo_root = project_root.parent
project_assets_dir = project_root / "assets"
shared_assets_dir = repo_root / "assets"

icon_file = project_assets_dir / "app.ico"
if not icon_file.exists():
    icon_file = shared_assets_dir / "app.ico"

copy_icon_file = project_assets_dir / "copy.png"
icon_path = icon_file if icon_file.exists() else None
data_files = []

if icon_path:
    data_files.append((str(icon_file), "assets"))

if copy_icon_file.exists():
    data_files.append((str(copy_icon_file), "assets"))

a = Analysis(
    [str(project_root / "bin" / "run.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=data_files,
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
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(icon_path)] if icon_path else None,
)
