"""Data/AI router — 409 unless scope approved. Architect/BA own it."""
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user, require_role
from app.models.tables import AuditLog, ScopeVersion
from app.services.coverage import compute_coverage
from app.services.data_ai_generator import generate_data_ai

router = APIRouter(prefix="/sessions", tags=["data-ai"])


def _latest(sid: str, db: Session):
    return db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc()).first()


def _job(sid: str, actor_id: str, actor_role: str, org_id: str):
    from app.core.db import SessionLocal
    import hashlib
    db = SessionLocal()
    try:
        sv = _latest(sid, db)
        if not sv or sv.status != "approved":
            return
        strat = generate_data_ai(sid, sv.payload, sv.version_no)
        payload = strat.model_dump()
        # Extended coverage: capabilities (from PRD if present) + integrations + AI use cases
        req_ids = [r["req_id"] for r in sv.payload.get("requirements", [])]
        caps = ((sv.payload.get("prd") or {}).get("capabilities", [])) or []
        cov = compute_coverage(sid, req_ids, caps, payload.get("integrations", []), payload.get("ai_use_cases", []))
        payload["coverage"] = cov.model_dump()
        h = hashlib.sha256(str(payload).encode()).hexdigest()[:12]
        merged = dict(sv.payload)
        merged["data_ai"] = payload
        db.add(ScopeVersion(session_id=sid, version_no=sv.version_no + 1, payload=merged, hash=h, status="approved", created_by=actor_id, created_role=actor_role))
        db.add(AuditLog(org_id=org_id, actor_id=actor_id, actor_role=actor_role, action="data_ai.generate", entity="session", entity_id=sid, detail={"scope_version": sv.version_no, "coverage_pct": cov.coverage_pct}))
        db.commit()
    finally:
        db.close()


@router.post("/{sid}/data-ai")
def request_data_ai(sid: str, bg: BackgroundTasks, db: Session = Depends(get_db), user=Depends(require_role("architect", "ba", "reviewer"))):
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    if sv.status != "approved":
        return {"error": "scope must be approved before data/AI strategy", "code": 409}
    bg.add_task(_job, sid, user.id, user.role, user.org_id)
    return {"ok": True, "status": "queued", "scope_version": sv.version_no}


@router.get("/{sid}/data-ai")
def get_data_ai(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sv = _latest(sid, db)
    if not sv or "data_ai" not in (sv.payload or {}):
        return {"status": "pending"}
    return {"version_no": sv.version_no, "data_ai": sv.payload["data_ai"]}
