"""Architecture router — platform select or auto-recommend. 409 unless scope approved."""
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user, require_role
from app.models.tables import AuditLog, ScopeVersion
from app.services.arch_generator import generate_architecture
from app.services.cloud_catalog import REQUIRED_LAYERS, recommend_platform, validate_platform_services

router = APIRouter(prefix="/sessions", tags=["architecture"])


class ArchRequest(BaseModel):
    platform: str = "auto"  # aws | azure | gcp | auto


def _latest(sid: str, db: Session):
    return db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc()).first()


def _job(sid: str, platform: str, actor_id: str, actor_role: str, org_id: str):
    from app.core.db import SessionLocal
    import hashlib
    db = SessionLocal()
    try:
        sv = _latest(sid, db)
        if not sv or sv.status != "approved":
            return
        scope = sv.payload
        arch = generate_architecture(sid, scope, platform, sv.version_no)
        payload = arch.model_dump()
        off_catalog = validate_platform_services(platform, payload.get("components", []))
        layers = {c["layer"] for c in payload.get("components", [])}
        missing_layers = [l for l in REQUIRED_LAYERS if l not in layers]
        payload["validation"] = {"off_catalog": off_catalog, "missing_layers": missing_layers}
        h = hashlib.sha256(str(payload).encode()).hexdigest()[:12]
        merged = dict(scope)
        merged["architecture"] = payload
        db.add(ScopeVersion(session_id=sid, version_no=sv.version_no + 1, payload=merged, hash=h, status="approved", created_by=actor_id, created_role=actor_role))
        db.add(AuditLog(org_id=org_id, actor_id=actor_id, actor_role=actor_role, action="arch.generate", entity="session", entity_id=sid, detail={"platform": platform, "off_catalog": off_catalog}))
        db.commit()
    finally:
        db.close()


@router.post("/{sid}/architecture")
def request_arch(sid: str, body: ArchRequest, bg: BackgroundTasks, db: Session = Depends(get_db), user=Depends(require_role("architect", "reviewer"))):
    if body.platform not in ("aws", "azure", "gcp", "auto"):
        return {"error": "platform must be aws|azure|gcp|auto", "code": 400}
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    if sv.status != "approved":
        return {"error": "scope must be approved before architecture", "code": 409}
    platform = body.platform
    if platform == "auto":
        types = [r.get("type", "") for r in (sv.payload.get("requirements", []))]
        platform = recommend_platform(types)
    bg.add_task(_job, sid, platform, user.id, user.role, user.org_id)
    return {"ok": True, "status": "queued", "platform": platform}


@router.get("/{sid}/architecture")
def get_arch(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sv = _latest(sid, db)
    if not sv or "architecture" not in (sv.payload or {}):
        return {"status": "pending"}
    return {"version_no": sv.version_no, "architecture": sv.payload["architecture"]}
