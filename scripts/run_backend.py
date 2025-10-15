
import sys
import os
from pathlib import Path   
import uvicorn

# Determine project root directory
repo_root = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd().parents[1]

# Add project root to sys.path if not already there
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

if __name__ == "__main__":
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000, reload=True)
