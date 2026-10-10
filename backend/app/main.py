"""FastAPI entry — health + routers."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import Base, engine
from app.routers import architecture, auth, data_ai, estimation, final_package, prd, scope, sessions

logging.basicConfig(level=settings.LOG_LEVEL)
app = FastAPI(title="AI Deal Scoping Assistant", version="0.1.0-phase6")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(scope.router)
app.include_router(prd.router)
app.include_router(architecture.router)
app.include_router(data_ai.router)
app.include_router(estimation.router)
app.include_router(final_package.router)


@app.get("/health")
def health():
    return {
        "ok": True,
        "env": settings.ENV,
        "ai_provider": settings.AI_PROVIDER,
        "ai_provider_chain": settings.AI_PROVIDER_CHAIN,
        "ai_model": settings.AI_MODEL,
        "mock_mode": settings.USE_MOCK_AI or settings.AI_PROVIDER == "mock",
        "ai_cache_enabled": settings.AI_CACHE_ENABLED,
    }


@app.on_event("startup")
def startup():
    if settings.ENV != "development" and settings.JWT_SECRET_KEY in ("", "change-me", "CHANGE-ME-min-32-chars"):
        raise RuntimeError("JWT_SECRET_KEY must be configured for non-development environments")
    Base.metadata.create_all(bind=engine)
