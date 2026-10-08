"""Scope review: edit one item -> new version; approve locks."""
import hashlib
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import require_role
from app.models.tables import AuditLog, ScopeVersion

router = APIRouter(prefix="/sessions", tags=["scope"])


class EditIn(BaseModel):
    req_id: str
    description: str | None = None
    priority: str | None = None


@router.patch("/{sid}/scope/items")
def edit_item(sid: str, body: EditIn, db: Session = Depends(get_db), user=Depends(require_role("architect", "ba", "reviewer"))):
    last = db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc()).first()
    if not last:
        return {"error": "no scope yet"}
    payload = dict(last.payload)
    updated = False
    for r in payload.get("requirements", []):
        if r.get("req_id") == body.req_id:
            if body.description:
                r["description"] = body.description
            if body.priority:
                r["priority"] = body.priority
            updated = True
    if not updated:
        return {"error": "req not found"}
    h = hashlib.sha256(str(payload).encode()).hexdigest()[:12]
    sv = ScopeVersion(session_id=sid, version_no=last.version_no + 1, payload=payload, hash=h, status="draft", created_by=user.id, created_role=user.role)
    db.add(sv)
    db.add(AuditLog(org_id=user.org_id, actor_id=user.id, actor_role=user.role, action="scope.edit", entity="session", entity_id=sid, detail={"req_id": body.req_id}))
    db.commit()
    return {"ok": True, "version_no": sv.version_no}


@router.post("/{sid}/approve")
def approve(sid: str, db: Session = Depends(get_db), user=Depends(require_role("architect", "reviewer"))):
    last = db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc()).first()
    if not last:
        return {"error": "no scope yet"}
    last.status = "approved"
    db.add(AuditLog(org_id=user.org_id, actor_id=user.id, actor_role=user.role, action="scope.approve", entity="session", entity_id=sid, detail={"version": last.version_no}))
    db.commit()
    return {"ok": True, "version_no": last.version_no, "status": "approved"}
