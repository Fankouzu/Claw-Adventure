"""
Lightweight views for the game web layer (SPA shell, etc.).
"""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


def serve_react_app(request, _path=None):
    """
    Serve the built React index.html for client-side routing under /app/.

    Build output should live at web/static/app/index.html (see
    web/static/app/README.md).
    """
    game_dir = Path(getattr(settings, "GAME_DIR", settings.BASE_DIR))
    index = game_dir / "web" / "static" / "app" / "index.html"
    if not index.is_file():
        raise Http404(
            "React app not built. Run the frontend build and place "
            "index.html under web/static/app/ (see web/static/app/README.md)."
        )
    return FileResponse(
        open(index, "rb"),
        content_type="text/html; charset=utf-8",
    )
