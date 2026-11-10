"""
Robust FastAPI server launcher with automatic instance reuse,
health checking, and port conflict resolution.
"""
import os
import sys
import socket
import urllib.request
import json
import logging
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("server_launcher")

def is_backend_healthy(host: str, port: int, timeout: float = 3.5) -> bool:
    """Check if our FastAPI backend is already responding on host:port."""
    endpoints = ["/api/ingest/batch-status", "/health", "/docs", "/"]
    for ep in endpoints:
        url = f"http://{host}:{port}{ep}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FastAPI-Launcher"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("content-type", "")
                    if "json" in content_type:
                        data = json.loads(resp.read().decode("utf-8"))
                        if (
                            data.get("service") == "Multilingual News Digest API"
                            or "active_count" in data
                            or data.get("status") in ["ok", "healthy"]
                        ):
                            return True
                    else:
                        body = resp.read().decode("utf-8", errors="ignore")
                        if "swagger" in body.lower() or "fastapi" in body.lower():
                            return True
        except Exception:
            continue
    return False

def is_port_available(host: str, port: int) -> bool:
    """Test if a socket can bind to host:port without permission or occupation errors."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        s.bind((host, port))
        s.close()
        return True
    except OSError:
        return False

def find_available_port(host: str, start_port: int, max_attempts: int = 20) -> int:
    """Find the next open port starting from start_port."""
    for p in range(start_port, start_port + max_attempts):
        if is_port_available(host, p):
            return p
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts}")

def sync_port_configuration(port: int):
    """Sync the chosen port to backend/.env and frontend/.env.local so services stay aligned."""
    env_file = backend_dir / ".env"
    frontend_dir = backend_dir.parent / "frontend"
    frontend_env = frontend_dir / ".env.local"

    # Update or add PORT in backend/.env
    if env_file.exists():
        lines = env_file.read_text(encoding="utf-8").splitlines()
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith("PORT="):
                new_lines.append(f"PORT={port}")
                updated = True
            else:
                new_lines.append(line)
        if not updated:
            new_lines.append(f"PORT={port}")
        env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    else:
        env_file.write_text(f"PORT={port}\n", encoding="utf-8")

    # Update frontend/.env.local
    if frontend_dir.exists():
        api_url = f"http://127.0.0.1:{port}"
        frontend_env.write_text(f"NEXT_PUBLIC_API_URL={api_url}\n", encoding="utf-8")
        logger.info(f"Synchronized frontend NEXT_PUBLIC_API_URL to {api_url}")

def main():
    host = settings.HOST
    desired_port = int(os.getenv("PORT") or settings.PORT)

    logger.info(f"Checking backend status on http://{host}:{desired_port}...")

    # 1. Check if healthy backend is ALREADY running
    if is_backend_healthy(host, desired_port):
        logger.info(f"[OK] Healthy FastAPI backend is already running on http://{host}:{desired_port} [reusing existing instance].")
        print("\n======================================================================")
        print(f" [OK] FastAPI backend is already active on http://{host}:{desired_port}")
        print(f"      Reusing running instance. Interactive API docs: http://{host}:{desired_port}/docs")
        print("======================================================================\n")
        return 0

    # 2. Check if the port can be bound or if it is blocked/forbidden (WinError 10013 / 10048)
    chosen_port = desired_port
    if not is_port_available(host, desired_port):
        logger.warning(
            f"Port {desired_port} is occupied or blocked by Windows permissions ([WinError 10013/10048]). "
            "Searching for available development port..."
        )
        chosen_port = find_available_port(host, desired_port + 1)
        logger.info(f"Selected available development port: {chosen_port}")
        sync_port_configuration(chosen_port)
    else:
        # Also ensure frontend .env.local is in sync with current port
        sync_port_configuration(chosen_port)

    # 3. Start Uvicorn on the chosen port
    import uvicorn
    logger.info(f"Starting FastAPI backend on http://{host}:{chosen_port}...")
    uvicorn.run("app.main:app", host=host, port=chosen_port, reload=True)

if __name__ == "__main__":
    sys.exit(main() or 0)
