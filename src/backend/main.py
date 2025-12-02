from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .db import init_db

app = FastAPI(title="Resume Skill Matcher", version="0.1.0")

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
    return {"status": "ok"}
