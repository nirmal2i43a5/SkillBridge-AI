#!/usr/bin/env python
"""Run the FastAPI backend with live reload."""
import sys
from pathlib import Path

import uvicorn

# Add project root to Python path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

if __name__ == "__main__":
    uvicorn.run("src.backend.main:app", host="localhost", port=8000, reload=True)
