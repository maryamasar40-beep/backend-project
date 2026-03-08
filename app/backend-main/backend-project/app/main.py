import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.db import engine
from app.routes import auth, brand, feedback, result, scan, whitelist

app = FastAPI(title="Phishing Hunter Backend")

cors_origins = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Backend is running successfully"}


@app.get("/health")
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        return {"status": "degraded"}


app.include_router(scan.router)
app.include_router(result.router)
app.include_router(feedback.router)
app.include_router(whitelist.router)
app.include_router(auth.router)
app.include_router(brand.router)
