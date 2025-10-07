#!/usr/bin/env python
"""Run the FastAPI backend with live reload."""
import uvicorn
import sys, os, pathlib, Path
# run once, near the top of your notebook

repo_root = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd().parents[1]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))
    
    
if __name__ == "__main__":
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000, reload=True)
