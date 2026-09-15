from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import (
    auth_router,
    challenges_router,
    cve_router,
    downloads_router,
    hints_router,
    leaderboard_router,
)
from .seed import seed

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AVST Lite API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(challenges_router.router)
app.include_router(downloads_router.router)
app.include_router(hints_router.router)
app.include_router(cve_router.router)
app.include_router(leaderboard_router.router)


@app.on_event("startup")
def on_startup():
    seed()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AVST Lite API"}
