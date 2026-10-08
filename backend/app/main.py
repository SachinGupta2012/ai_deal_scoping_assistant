"""FastAPI entry — health + routers."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import Base, engine
from app.routers import architecture, auth, data_ai, prd, scope, sessions

logging.basicConfig(level=settings.LOG_LEVEL)
app = FastAPI(title="AI Deal Scoping Assistant", version="0.1.0-phase1")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(scope.router)
app.include_router(prd.router)
app.include_router(architecture.router)
app.include_router(data_ai.router)


@app.get("/health")
def health():
    return {"ok": True, "env": settings.ENV, "ai_provider": settings.AI_PROVIDER, "ai_model": settings.AI_MODEL, "live_only": True}


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
