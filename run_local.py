"""FreightIQ Enterprise - Local Process Runner
Launches FastAPI backend on :8000 and Streamlit frontend on :8501 concurrently.
"""

import os
import sys
import subprocess
import time
import signal
import threading

env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"
env["PYTHONUTF8"] = "1"

def ensure_synthetic_data():
    """Ensure that data directory and synthetic CSVs exist before starting services."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    required_files = [
        "freight_rates_history.csv",
        "port_infrastructure.csv",
        "vessel_classes.csv",
        "port_tariffs_sor.csv",
        "port_congestion_synthetic.csv",
        "bunker_prices_synthetic.csv",
        "landside_evacuation.csv"
    ]
    missing = [f for f in required_files if not os.path.exists(os.path.join(data_dir, f))]
    if missing:
        print("[FreightIQ Init] Missing synthetic data files. Generating now...")
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "generate_synthetic_data.py")
        subprocess.run([sys.executable, script_path], check=True)
        print("[FreightIQ Init] Synthetic seed data successfully generated.")


def stream_logs(process, prefix):
    """Stream stdout/stderr from subprocess with colorized prefix."""
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"[{prefix}] {line.strip()}", flush=True)


def main():
    ensure_synthetic_data()

    print("=" * 70)
    print("🚀 STARTING FREIGHTIQ ENTERPRISE PLATFORM")
    print("=" * 70)
    print(" Backend REST API  : http://localhost:8000 (Docs: http://localhost:8000/docs)")
    print(" Frontend Dashboard: http://localhost:8501")
    print("=" * 70)

    # Launch FastAPI backend
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info"
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Launch Streamlit frontend
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", "frontend/Home.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    t1 = threading.Thread(target=stream_logs, args=(backend_proc, "BACKEND"), daemon=True)
    t2 = threading.Thread(target=stream_logs, args=(frontend_proc, "FRONTEND"), daemon=True)
    t1.start()
    t2.start()

    def shutdown(signum, frame):
        print("\n[FreightIQ Runner] Shutting down services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print(f"[FreightIQ Runner] Backend exited unexpectedly with code {backend_proc.returncode}")
                break
            if frontend_proc.poll() is not None:
                print(f"[FreightIQ Runner] Frontend exited unexpectedly with code {frontend_proc.returncode}")
                break
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
