import subprocess
import sys
from pathlib import Path

APP_PATH = Path(__file__).resolve().parent.parent / "frontend" / "app.py"

if __name__ == "main__":
    raise SystemExit("Please run as a module")

if __name__ == "__main__":
    cmd = [sys.executable, "-m", "streamlit", "run", str(APP_PATH)]
    raise SystemExit(subprocess.call(cmd))
