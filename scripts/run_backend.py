import uvicorn

# Add project root to Python path
repo_root = Path(__file__).resolve().parent.parent

# Add project root to sys.path if not already there
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

    sys.path.append(str(repo_root))

if __name__ == "__main__":
    uvicorn.run("src.backend.main:app", host="127.0.0.1", port=8000, reload=True)
