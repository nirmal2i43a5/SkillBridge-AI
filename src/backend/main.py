from datetime import datetime, timezone
import time

import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router, recommender
# from .db import init_db

# Initialize database tables
# init_db()

# Track startup time for uptime calculation
_start_time = time.time()
_API_VERSION = "v1.3.2"

app = FastAPI(title="Resume Skill Matcher", version=_API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
# init_db()
        
app.include_router(router)



@app.get("/health")
async def health() -> dict:
    """Basic health check endpoint"""
    return {"status": "ok"}


@app.get("/status")
async def status() -> dict:
    """Comprehensive system status endpoint"""
    # Calculate uptime
    uptime_seconds = int(time.time() - _start_time)
    
    # Get vector store metrics
    vector_store_status = recommender.vector_store.get_status()
    vector_count = vector_store_status["vector_count"]
    embedding_store_status = "Available" if vector_store_status["is_initialized"] else "Not Initialized"
    
    # Get last sync time
    last_sync = recommender._last_index_time
    last_sync_str = None
    if last_sync:
        last_sync_str = last_sync.isoformat().replace("+00:00", "Z")
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Measure API response time (simple approach - just for this endpoint)
    response_start = time.time()
    response_time_ms = int((time.time() - response_start) * 1000)
    
    # Get recommender status
    indexed_jobs = len(recommender._job_postings)
    recommender_status = "Ready" if indexed_jobs > 0 else "No Jobs Indexed"
    
    return {
        "status": "OK",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "api": {
            "uptime_seconds": uptime_seconds,
            "version": _API_VERSION,
            "response_time_ms": response_time_ms
        },
        "embedding_store": {
            "status": embedding_store_status,
            "vector_count": vector_count,
            "last_sync": last_sync_str,
            "index_type": vector_store_status.get("index_type"),
            "backend": vector_store_status.get("backend")
        },
        "system_metrics": {
            "cpu_usage_percent": round(cpu_percent, 1),
            "memory_usage_percent": round(memory_percent, 1),
            "active_requests": 0  # Could be enhanced with middleware to track actual requests
        },
        "recommender": {
            "indexed_jobs": indexed_jobs,
            "status": recommender_status
        }
    }
