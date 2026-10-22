"""FR-6 endpoints: change impact, quality gate, and Markdown package export."""
import hashlib

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_role
from app.models.tables import AuditLog, ScopeVersion
from app.schemas.package import ChangeImpactRequest
from app.services.change_impact import analyze_change_impact
from app.services.package_assembler import assemble_package
from app.services.quality_gate import run_quality_gate

router = APIRouter(prefix="/sessions", tags=["final-package"])


def _latest(sid: str, db: Session):
    return db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc()).first()


@router.post("/{sid}/change-impact")
def change_impact(sid: str, body: ChangeImpactRequest, db: Session = Depends(get_db), user=Depends(require_role("architect", "delivery", "reviewer"))):
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    impact = analyze_change_impact(sid, sv.payload, body)
    return {"change_impact": impact.model_dump()}


@router.post("/{sid}/quality-gate")
def quality_gate(sid: str, db: Session = Depends(get_db), user=Depends(require_role("architect", "delivery", "reviewer"))):
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    gate = run_quality_gate(sid, sv.payload)
    merged = dict(sv.payload)
    merged["quality_gate"] = gate.model_dump()
    h = hashlib.sha256(str(gate.model_dump()).encode()).hexdigest()[:12]
    next_v = ScopeVersion(session_id=sid, version_no=sv.version_no + 1, payload=merged, hash=h, status=sv.status, created_by=user.id, created_role=user.role)
    db.add(next_v)
    db.add(AuditLog(org_id=user.org_id, actor_id=user.id, actor_role=user.role, action="quality_gate.run", entity="session", entity_id=sid, detail={"status": gate.status, "issues": len(gate.issues)}))
    db.commit()
    return {"version_no": next_v.version_no, "quality_gate": gate.model_dump()}


@router.get("/{sid}/quality-gate")
def get_quality_gate(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    if "quality_gate" in (sv.payload or {}):
        return {"version_no": sv.version_no, "quality_gate": sv.payload["quality_gate"]}
    gate = run_quality_gate(sid, sv.payload)
    return {"version_no": sv.version_no, "quality_gate": gate.model_dump()}


@router.post("/{sid}/package")
def create_package(sid: str, body: ChangeImpactRequest | None = None, db: Session = Depends(get_db), user=Depends(require_role("architect", "delivery", "reviewer"))):
    sv = _latest(sid, db)
    if not sv:
        return {"error": "no scope yet", "code": 409}
    impact = analyze_change_impact(sid, sv.payload, body) if body else None
    gate = run_quality_gate(sid, sv.payload)
    package = assemble_package(sid, sv.payload, gate, impact)
    merged = dict(sv.payload)
    merged["quality_gate"] = gate.model_dump()
    merged["package"] = package.model_dump()
    h = hashlib.sha256(package.markdown.encode()).hexdigest()[:12]
    next_v = ScopeVersion(session_id=sid, version_no=sv.version_no + 1, payload=merged, hash=h, status=sv.status, created_by=user.id, created_role=user.role)
    db.add(next_v)
    db.add(AuditLog(org_id=user.org_id, actor_id=user.id, actor_role=user.role, action="package.export", entity="session", entity_id=sid, detail={"status": gate.status, "export_path": package.export_path}))
    db.commit()
    return {"version_no": next_v.version_no, "package": package.model_dump()}


@router.get("/{sid}/package")
def get_package(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sv = _latest(sid, db)
    if not sv or "package" not in (sv.payload or {}):
        return {"status": "pending"}
    return {"version_no": sv.version_no, "package": sv.payload["package"]}
