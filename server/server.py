"""
Flask REST API backend for the app store.
Production-style implementation with CORS, structured logging, and error handling.
"""

import json
import logging
import os
import sys
import time
import webbrowser
from pathlib import Path
from threading import Timer, Thread

from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS

# --- Path resolution for PyInstaller and development ---
def get_base_path() -> Path:
    """Resolve base path for bundled (PyInstaller) or script execution."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def locate_static_dir() -> Path:
    """Locate the built Angular static files (client). Prefer client/ paths first."""
    base = get_base_path()
    # Project root: when frozen, exe is in server/dist/ so go up twice; else base.parent (server/)
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        project_root = exe_dir.parent.parent  # server/dist -> server -> project
    else:
        project_root = base.parent  # server/ -> project
    # Try client/ first so we never accidentally use server/dist or wrong folder
    candidates = [
        project_root / "client" / "dist" / "my-first-angular-app" / "browser",
        project_root / "client" / "dist" / "my-first-angular-app",
        project_root / "client" / "dist" / "browser",
        project_root / "client" / "dist",
        # PyInstaller bundle (client baked into exe at ui/dist)
        base / "ui" / "dist" / "my-first-angular-app" / "browser",
        base / "ui" / "dist" / "browser",
        base / "ui" / "dist",
        base / "dist" / "my-first-angular-app" / "browser",
        base / "dist" / "browser",
        base / "dist",
    ]
    for p in candidates:
        index = p / "index.html"
        if index.exists():
            return p
    return base / "ui" / "dist" / "browser"  # fallback for PyInstaller datas


def locate_manifest_path() -> Path:
    """Locate manifest.json path."""
    base = get_base_path()
    candidates = [
        base / "manifest.json",
        base / ".." / "manifest.json",
    ]
    for p in candidates:
        if p.resolve().exists():
            return p.resolve()
    return base / "manifest.json"


def locate_downloads_dir() -> Path:
    """Directory containing downloadable exe files."""
    base = get_base_path()
    return base / "downloads"


# --- Logging configuration ---
def setup_logging():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
CORS(app, origins=["*"], allow_headers=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# In-memory download counter: { app_id: count }
_download_counts: dict[str, int] = {}

# For "close browser = shut down": last time we got a ping from the client
_last_activity: float = 0.0
_shutdown_idle_seconds = 15.0


def _watchdog():
    """If no client activity for _shutdown_idle_seconds, exit the process."""
    while True:
        time.sleep(5)
        if _last_activity == 0:
            continue
        if time.time() - _last_activity > _shutdown_idle_seconds:
            logger.info("No client activity for %.0fs; shutting down.", _shutdown_idle_seconds)
            os._exit(0)


def load_manifest() -> list[dict]:
    """Load and parse manifest.json dynamically."""
    path = locate_manifest_path()
    if not path.exists():
        logger.warning("manifest.json not found at %s, returning empty list", path)
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        apps = data if isinstance(data, list) else data.get("apps", [])
        return apps
    except json.JSONDecodeError as e:
        logger.error("Invalid manifest.json: %s", e)
        return []
    except OSError as e:
        logger.error("Cannot read manifest.json: %s", e)
        return []


def get_app_by_id(app_id: str) -> dict | None:
    """Get a single app by id."""
    for app in load_manifest():
        if str(app.get("id", "")) == str(app_id):
            return app
    return None


# --- API Endpoints ---

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "app-store-api"})


@app.route("/apps", methods=["GET"])
def list_apps():
    """List all apps from manifest."""
    apps = load_manifest()
    for a in apps:
        aid = str(a.get("id", ""))
        a["downloadCount"] = _download_counts.get(aid, 0)
    return jsonify({"apps": apps})


@app.route("/apps/<app_id>", methods=["GET"])
def get_app(app_id: str):
    """Get single app by id."""
    app_obj = get_app_by_id(app_id)
    if not app_obj:
        return jsonify({"error": "App not found"}), 404
    aid = str(app_obj.get("id", ""))
    app_obj = dict(app_obj)
    app_obj["downloadCount"] = _download_counts.get(aid, 0)
    return jsonify(app_obj)


@app.route("/apps/<app_id>/updates", methods=["GET"])
def get_app_updates(app_id: str):
    """Get update information for an app."""
    app_obj = get_app_by_id(app_id)
    if not app_obj:
        return jsonify({"error": "App not found"}), 404
    return jsonify({
        "appId": app_obj.get("id"),
        "version": app_obj.get("version"),
    })


@app.route("/apps/<app_id>/download", methods=["GET"])
def download_app(app_id: str):
    """Serve the exe file and increment download counter."""
    app_obj = get_app_by_id(app_id)
    if not app_obj:
        return jsonify({"error": "App not found"}), 404

    exe_url = app_obj.get("exeUrl") or app_obj.get("exePath")
    if not exe_url:
        return jsonify({"error": "No download available for this app"}), 404

    downloads_dir = locate_downloads_dir()
    filename = Path(exe_url).name
    filepath = downloads_dir / filename

    if not filepath.exists():
        logger.warning("File not found: %s", filepath)
        return jsonify({"error": "Download file not found"}), 404

    _download_counts[str(app_obj.get("id", ""))] = _download_counts.get(str(app_obj.get("id", "")), 0) + 1

    return send_from_directory(
        downloads_dir,
        filename,
        as_attachment=True,
        download_name=filename,
    )


@app.route("/download-events", methods=["POST"])
def record_download_event():
    """Record a download event (e.g. analytics)."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        app_id = data.get("appId")
        event_type = data.get("eventType", "download")
        logger.info("Download event: appId=%s, eventType=%s", app_id, event_type)
        return jsonify({"recorded": True})
    except Exception as e:
        logger.exception("Failed to record download event: %s", e)
        return jsonify({"error": str(e)}), 400


@app.route("/tools", methods=["GET"])
def list_tools():
    """List available tools (from manifest or derived)."""
    apps = load_manifest()
    tools = [
        {"id": a.get("id"), "name": a.get("name"), "description": a.get("description"), "version": a.get("version")}
        for a in apps
    ]
    return jsonify({"tools": tools})


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze request (e.g. app usage analytics)."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        apps = load_manifest()
        summary = {
            "totalApps": len(apps),
            "totalDownloads": sum(_download_counts.values()),
            "byApp": {str(a.get("id", "")): _download_counts.get(str(a.get("id", "")), 0) for a in apps},
        }
        return jsonify({"analysis": summary, "input": data})
    except Exception as e:
        logger.exception("Analyze failed: %s", e)
        return jsonify({"error": str(e)}), 500


# --- Static file serving (Angular SPA) ---

static_dir = locate_static_dir().resolve()
_index_html = static_dir / "index.html"


def _safe_path(base: Path, subpath: str) -> Path | None:
    """Resolve subpath under base; return None if it escapes base (security)."""
    base = base.resolve()
    try:
        full = (base / subpath).resolve()
        full.relative_to(base)
        return full
    except (ValueError, OSError):
        return None


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path: str):
    """Serve Angular SPA: static files or index.html for client-side routes."""
    if not path or path == "index.html":
        if _index_html.exists():
            return send_file(str(_index_html), mimetype="text/html")
        return jsonify({"error": "Not found"}), 404
    resolved = _safe_path(static_dir, path)
    if resolved and resolved.is_file():
        return send_file(str(resolved), mimetype=None, as_attachment=False)
    if _index_html.exists():
        return send_file(str(_index_html), mimetype="text/html")
    return jsonify({"error": "Not found"}), 404


@app.route("/ping", methods=["GET"])
def ping():
    """Client pings this so server knows the app is still open. If pings stop (browser closed), server shuts down."""
    global _last_activity
    _last_activity = time.time()
    return jsonify({"ok": True})


@app.route("/shutdown", methods=["POST"])
def shutdown():
    """Shut down the server (and exe). Call from Quit app button."""
    def do_exit():
        import time
        time.sleep(0.3)  # allow response to be sent
        os._exit(0)

    Thread(target=do_exit, daemon=True).start()
    return jsonify({"ok": True, "message": "Shutting down"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    logger.exception("Internal server error")
    return jsonify({"error": "Internal server error"}), 500


def open_browser():
    """Open default browser to the app (after short delay)."""
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    logger.info("Starting server on %s:%d", host, port)
    logger.info("Static dir exists: %s", static_dir.exists())
    Thread(target=_watchdog, daemon=True).start()
    Timer(1.0, open_browser).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)
