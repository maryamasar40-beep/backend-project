from fastapi import FastAPI
from app.routes.scan import router as scan_router
from app.db import engine, Base
from app import models


app = FastAPI(title="Backend Project API")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/hello")
def hello():
    return {"message": "hello backend"}


app.include_router(scan_router)