from pathlib import Path


def apply_app_icon(window):
    """Apply app icon if an .ico file exists."""
    app_dir = Path(__file__).resolve().parent
    project_root = app_dir.parent.parent
    repo_root = project_root.parent
    candidates = (
        repo_root / "assets" / "app.ico",
        project_root / "assets" / "app.ico",
        app_dir / "assets" / "app.ico",
    )

    for icon_path in candidates:
        if icon_path.exists():
            try:
                window.iconbitmap(str(icon_path))
                return
            except Exception:
                return
