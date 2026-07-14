# -*- coding: utf-8 -*-
"""Start both backend and frontend services"""
import subprocess, sys, os, time, signal, json, atexit

SERVICES = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def start_backend():
    print("Starting backend...")
    p = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    SERVICES["backend"] = p
    print(f"  Backend PID: {p.pid}")

def start_frontend():
    print("Starting frontend...")
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    p = subprocess.Popen(
        ["npx", "vite", "--host", "0.0.0.0", "--port", "5173", "--strictPort"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    SERVICES["frontend"] = p
    print(f"  Frontend PID: {p.pid}")

def cleanup():
    for name, p in list(SERVICES.items()):
        if p.poll() is None:
            print(f"Stopping {name}...")
            p.terminate()
            try:
                p.wait(timeout=5)
            except:
                p.kill()

if __name__ == "__main__":
    atexit.register(cleanup)
    start_backend()
    start_frontend()
    
    time.sleep(3)
    
    # Check services
    for name, p in SERVICES.items():
        if p.poll() is None:
            print(f"  {name}: RUNNING (PID {p.pid})")
        else:
            print(f"  {name}: FAILED (exit code {p.returncode})")
    
    print("\nServices:")
    print("  Backend:  http://localhost:8000")
    print("  Frontend: http://localhost:5173")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
