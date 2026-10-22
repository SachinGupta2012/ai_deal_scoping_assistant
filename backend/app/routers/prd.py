"""PRD router — 409 unless scope is approved. Stores PRD + coverage in scope payload chain."""
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user, require_role
from app.models.tables import AuditLog, ScopeVersion
from app.services.coverage import compute_coverage
from app.services.prd_generator import generate_prd

router = APIRouter(prefix="/sessions", tags=["prd"])


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
        scope = sv.payload
        prd = generate_prd(sid, scope, sv.version_no)
        payload = prd.model_dump()
        req_ids = [r["req_id"] for r in scope.get("requirements", [])]
        cov = compute_coverage(sid, req_ids, payload.get("capabilities", []))
        payload["coverage"] = cov.model_dump()
        h = hashlib.sha256(str(payload).encode()).hexdigest()[:12]
        db.add(ScopeVersion(session_id=sid, version_no=sv.version_no + 1, payload={**scope, "prd": payload}, hash=h, status="approved", created_by=actor_id, created_role=actor_role))
        db.add(AuditLog(org_id=org_id, actor_id=actor_id, actor_role=actor_role, action="prd.generate", entity="session", entity_id=sid, detail={"scope_version": sv.version_no, "coverage_pct": cov.coverage_pct}))
        db.commit()
    finally:
        db.close()


@router.post("/{sid}/prd")
def request_prd(sid: str, bg: BackgroundTasks, db: Session = Depends(get_db), user=Depends(require_role("architect", "ba", "reviewer"))):
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    if sv.status != "approved":
        return {"error": "scope must be approved before PRD generation", "code": 409}
    bg.add_task(_job, sid, user.id, user.role, user.org_id)
    return {"ok": True, "status": "queued", "scope_version": sv.version_no}


@router.get("/{sid}/prd")
def get_prd(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sv = _latest(sid, db)
    if not sv or "prd" not in (sv.payload or {}):
        return {"status": "pending"}
    return {"version_no": sv.version_no, "prd": sv.payload["prd"]}
