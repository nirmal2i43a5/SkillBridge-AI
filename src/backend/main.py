from datetime import datetime, timezone
import time

import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .db import init_db
from mangum import Mangum#for vercel deployment 

app = FastAPI(title="Resume Skill Matcher", version=_API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
init_db()
        
app.include_router(router)



@app.get("/health")
async def health() -> dict:
    """Basic health check endpoint"""
    return {"status": "ok"}

handler = Mangum(app)