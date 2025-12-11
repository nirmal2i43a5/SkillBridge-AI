import sys
from pathlib import Path

# Add project root to Python path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.main import app

# Vercel serverless handler
handler = app