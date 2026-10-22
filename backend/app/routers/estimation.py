"""Estimation router — deterministic FR-5, no LLM numbers."""
import hashlib

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_role
from app.models.tables import AuditLog, ScopeVersion
from app.schemas.estimation import EstimateConfig
from app.services.estimation import calculate_estimate

router = APIRouter(prefix="/sessions", tags=["estimation"])


class EstimateRequest(BaseModel):
    config: EstimateConfig = Field(default_factory=EstimateConfig)


def _latest(sid: str, db: Session):
    return db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc()).first()


@router.post("/{sid}/estimate")
def request_estimate(
    sid: str,
    body: EstimateRequest,
    db: Session = Depends(get_db),
    user=Depends(require_role("architect", "delivery", "reviewer")),
):
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    if sv.status != "approved":
        return {"error": "scope must be approved before estimation", "code": 409}
    estimate = calculate_estimate(sid, sv.payload, sv.version_no, body.config)
    payload = estimate.model_dump()
    merged = dict(sv.payload)
    merged["estimate"] = payload
    h = hashlib.sha256(str(payload).encode()).hexdigest()[:12]
    next_v = ScopeVersion(
        session_id=sid,
        version_no=sv.version_no + 1,
        payload=merged,
        hash=h,
        status="approved",
        created_by=user.id,
        created_role=user.role,
    )
    db.add(next_v)
    db.add(AuditLog(
        org_id=user.org_id,
        actor_id=user.id,
        actor_role=user.role,
        action="estimate.generate",
        entity="session",
        entity_id=sid,
        detail={"scope_version": sv.version_no, "confidence": estimate.confidence, "rom_low": estimate.rom_low, "rom_high": estimate.rom_high},
    ))
    db.commit()
    return {"ok": True, "version_no": next_v.version_no, "estimate": payload}


@router.get("/{sid}/estimate")
def get_estimate(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sv = _latest(sid, db)
    if not sv or "estimate" not in (sv.payload or {}):
        return {"status": "pending"}
    return {"version_no": sv.version_no, "estimate": sv.payload["estimate"]}
