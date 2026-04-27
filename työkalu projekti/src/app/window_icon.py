from pathlib import Path
import sys

# This module handles applying the application icon to windows.
def find_app_icon_path():
    app_dir = Path(__file__).resolve().parent
    project_root = app_dir.parent.parent
    repo_root = project_root.parent
    frozen_base = Path(getattr(sys, "_MEIPASS", "")) if getattr(sys, "frozen", False) else None

    candidates = []
    if frozen_base:
        candidates.append(frozen_base / "assets" / "app.ico")

    candidates.extend((
        repo_root / "assets" / "app.ico",
        project_root / "assets" / "app.ico",
        app_dir / "assets" / "app.ico",
    ))

    for icon_path in candidates:
        if icon_path.exists():
            return icon_path
    return None


def apply_app_icon(window):
    icon_path = find_app_icon_path()
    if not icon_path:
        return
    try:
        window.iconbitmap(str(icon_path))
        return
    except Exception:
        return
