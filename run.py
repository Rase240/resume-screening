#!/usr/bin/env python3
"""
Folio Unified Runner
A single cross-platform runner for the Folio Resume Screening application.
Works across Windows, macOS, and Linux.
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
VENDOR_DIR = BACKEND_DIR / "vendor"
NODE_MODULES = FRONTEND_DIR / "node_modules"

# On Windows, if launched with an incompatible Python (e.g. MSYS 3.14 without pip),
# auto-switch to Python 3.12 via py launcher if available.
    py_launcher = shutil.which("py")
    if py_launcher:
        check = subprocess.run(
            ["py", "-3.12", "-c", "import sys; sys.exit(0)"],
            capture_output=True
        )
        if check.returncode == 0:
            result = subprocess.run(["py", "-3.12", str(__file__)] + sys.argv[1:])
            sys.exit(result.returncode)


def get_env():
    """Build the required environment variables for the backend."""
    env = os.environ.copy()
    vendor_str = str(VENDOR_DIR)
    backend_str = str(BACKEND_DIR)
    existing_pythonpath = env.get("PYTHONPATH", "")
    new_pythonpath = os.pathsep.join(
        [vendor_str, backend_str] + ([existing_pythonpath] if existing_pythonpath else [])
    )
    env["PYTHONPATH"] = new_pythonpath
    env["OPENBLAS_NUM_THREADS"] = "1"
    return env


def check_dependencies():
    """Verify that vendor and node_modules exist."""
    missing = []
    if not VENDOR_DIR.exists():
        missing.append(f"Backend vendor packages missing: {VENDOR_DIR}")
    if not NODE_MODULES.exists():
        missing.append(f"Frontend packages missing: {NODE_MODULES}")

    if missing:
        print("\n[Folio Error] Dependencies are missing:")
        for m in missing:
            print(f"  - {m}")
        print("\nPlease run: python run.py install\n")
        sys.exit(1)


def check_port(port, service_name, host="127.0.0.1"):
    """Check if a port is already occupied."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        if s.connect_ex((host, port)) == 0:
            print(f"\n[Folio Error] Port {port} is already in use (required by {service_name}).")
            print(f"Please stop the existing process using port {port} and try again.\n")
            sys.exit(1)


def kill_proc(proc):
    """Cleanly terminate a process and its process tree."""
    if proc is None or proc.poll() is not None:
        return
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    else:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


def run_install():
    """Install backend and frontend dependencies."""
    print("[Folio] Installing backend Python packages to backend/vendor...")
    req_file = BACKEND_DIR / "requirements.txt"
    pip_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--target",
        str(VENDOR_DIR),
        "-r",
        str(req_file),
    ]
    subprocess.run(pip_cmd, check=True)

    print("\n[Folio] Installing frontend npm packages...")
    npm_bin = shutil.which("npm") or ("npm.cmd" if sys.platform == "win32" else "npm")
    subprocess.run([npm_bin, "install"], cwd=str(FRONTEND_DIR), check=True)

    print("\n[Folio] All dependencies installed successfully.")


def run_test():
    """Run backend test suite."""
    check_dependencies()
    print("[Folio] Running backend test suite with pytest...")
    env = get_env()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    cmd = [sys.executable, "-m", "pytest", "backend/tests", "-q"]
    res = subprocess.run(cmd, cwd=str(ROOT), env=env)
    sys.exit(res.returncode)


def run_backend():
    """Run the FastAPI backend service."""
    check_dependencies()
    check_port(8000, "Backend (FastAPI)")
    print("[Folio] Starting FastAPI backend on http://127.0.0.1:8000 ...")
    env = get_env()
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--app-dir",
        "backend",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--ws",
        "none",
    ]
    try:
        subprocess.run(cmd, cwd=str(ROOT), env=env)
    except KeyboardInterrupt:
        print("\n[Folio] Backend stopped.")


def run_frontend():
    """Run the Next.js frontend dev server."""
    check_dependencies()
    check_port(3000, "Frontend (Next.js)")
    print("[Folio] Starting Next.js frontend on http://127.0.0.1:3000 ...")
    npm_bin = shutil.which("npm") or ("npm.cmd" if sys.platform == "win32" else "npm")
    cmd = [npm_bin, "run", "dev", "--", "--hostname", "127.0.0.1", "--port", "3000"]
    try:
        subprocess.run(cmd, cwd=str(FRONTEND_DIR))
    except KeyboardInterrupt:
        print("\n[Folio] Frontend stopped.")


def run_both():
    """Run both backend and frontend concurrently with graceful shutdown."""
    check_dependencies()
    check_port(8000, "Backend (FastAPI)")
    check_port(3000, "Frontend (Next.js)")
    env = get_env()
    npm_bin = shutil.which("npm") or ("npm.cmd" if sys.platform == "win32" else "npm")

    print("[Folio] Starting Backend on http://127.0.0.1:8000 ...")
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--app-dir",
        "backend",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--ws",
        "none",
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(ROOT), env=env)

    print("[Folio] Starting Frontend on http://127.0.0.1:3000 ...")
    frontend_cmd = [npm_bin, "run", "dev", "--", "--hostname", "127.0.0.1", "--port", "3000"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(FRONTEND_DIR))

    print("\n[Folio] Services running at http://127.0.0.1:3000 (Press Ctrl+C to stop both)\n")

    def handle_signal(sig, frame):
        print("\n[Folio] Shutting down services...")
        kill_proc(backend_proc)
        kill_proc(frontend_proc)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_signal)

    try:
        while True:
            b_poll = backend_proc.poll()
            f_poll = frontend_proc.poll()
            if b_poll is not None or f_poll is not None:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        kill_proc(backend_proc)
        kill_proc(frontend_proc)
        print("[Folio] All services stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Folio Resume Screening - Unified Multi-Platform Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""commands:
  (default)  Start both backend and frontend together
  backend    Start FastAPI backend only (http://127.0.0.1:8000)
  frontend   Start Next.js frontend only (http://127.0.0.1:3000)
  install    Install both backend and frontend dependencies
  test       Run backend test suite (pytest)
""",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="both",
        choices=["both", "backend", "frontend", "install", "test"],
        help="Command to run (default: both)",
    )

    args = parser.parse_args()

    if args.command == "both":
        run_both()
    elif args.command == "backend":
        run_backend()
    elif args.command == "frontend":
        run_frontend()
    elif args.command == "install":
        run_install()
    elif args.command == "test":
        run_test()


if __name__ == "__main__":
    main()