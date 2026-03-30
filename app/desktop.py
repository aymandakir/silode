from __future__ import annotations

import threading
import time
from urllib.request import urlopen

import uvicorn

from app.config import get_settings


def _start_server() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="warning",
    )


def _wait_for_server(url: str, timeout: float = 20.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=1.5):
                return
        except Exception:
            time.sleep(0.25)

    raise RuntimeError("Silode server did not start in time.")


def launch_desktop_app() -> None:
    try:
        import webview
    except ImportError as exc:  # pragma: no cover - desktop dependency check
        raise RuntimeError(
            "pywebview is required for desktop mode. Install the project requirements first."
        ) from exc

    settings = get_settings()
    app_url = f"http://{settings.host}:{settings.port}"

    server_thread = threading.Thread(target=_start_server, daemon=True)
    server_thread.start()
    _wait_for_server(f"{app_url}/api/health")

    window = webview.create_window(
        settings.display_name,
        app_url,
        width=settings.desktop_width,
        height=settings.desktop_height,
        min_size=(1100, 720),
    )
    webview.start()

    if window is not None:
        return
