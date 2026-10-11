"""Sessions: create + ingest + analyze."""
import hashlib
import os
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.core.security import get_current_user, require_role
from app.models.tables import AuditLog, Chunk, Document, RequirementRow, ScopeVersion, Session as S
from app.services.ai.orchestrator import run_analysis
from app.services.ingestion import chunk_text, normalize_text, read_upload

router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateIn(BaseModel):
    title: str = "New scoping session"
    opportunity_context: dict = {}


@router.post("")
def create_session(body: CreateIn, db: Session = Depends(get_db), user=Depends(require_role("sales", "architect", "ba", "delivery", "reviewer"))):
    s = S(org_id=user.org_id, title=body.title, opportunity_context=body.opportunity_context, created_by=user.id)
    db.add(s)
    db.commit()
    db.refresh(s)
    db.add(AuditLog(org_id=user.org_id, actor_id=user.id, actor_role=user.role, action="session.create", entity="session", entity_id=s.id))
    db.commit()
    return {"id": s.id, "title": s.title, "status": s.status}


@router.get("")
def list_sessions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(S).filter(S.org_id == user.org_id).order_by(S.created_at.desc()).limit(50).all()
    return {
        "sessions": [
            {
                "id": row.id,
                "title": row.title,
                "status": row.status,
                "opportunity_context": row.opportunity_context or {},
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
    }


@router.post("/{sid}/ingest")
def ingest(sid: str, text: str = Form(default=""), file: UploadFile | None = File(default=None), db: Session = Depends(get_db), user=Depends(require_role("sales", "architect", "ba"))):
    s = db.query(S).filter(S.id == sid).first()
    if not s:
        return {"error": "not found"}
    raw = text
    fname = "pasted.txt"
    if file:
        raw = read_upload(file.filename, file.file.read())
        fname = file.filename
    norm = normalize_text(raw)
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    path = os.path.join(settings.STORAGE_DIR, f"{sid}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(norm)
    doc = Document(session_id=sid, filename=fname, raw_path=path, normalized_md=norm)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    chunks = chunk_text(norm)
    for c in chunks:
        db.add(Chunk(document_id=doc.id, idx=c["idx"], text=c["text"], char_start=c["char_start"], char_end=c["char_end"]))
    db.commit()
    return {"document_id": doc.id, "chars": len(norm), "chunks": len(chunks), "preview": norm[:2000]}


def _analyze_job(sid: str, actor_id: str, actor_role: str, org_id: str):
    from app.core.db import SessionLocal
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.session_id == sid).order_by(Document.id.desc()).first()
        if not doc:
            return
        chs = db.query(Chunk).filter(Chunk.document_id == doc.id).order_by(Chunk.idx).all()
        chunk_dicts = [{"idx": str(c.idx), "text": c.text} for c in chs]
        scope, meta = run_analysis(sid, doc.normalized_md, chunk_dicts)
        payload = scope.model_dump()
        h = hashlib.sha256(str(payload).encode()).hexdigest()[:12]
        last = db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc()).first()
        vno = (last.version_no + 1) if last else 1
        db.add(ScopeVersion(session_id=sid, version_no=vno, payload=payload, hash=h, status="draft", created_by=actor_id, created_role=actor_role))
        db.query(RequirementRow).filter(RequirementRow.session_id == sid).delete()
        for r in scope.requirements:
            db.add(RequirementRow(session_id=sid, req_id=r.req_id, type=r.type, description=r.description, priority=r.priority, chunk_id=r.chunk_id, quote=r.quote, origin=r.origin))
        db.add(AuditLog(org_id=org_id, actor_id=actor_id, actor_role=actor_role, action="scope.analyze", entity="session", entity_id=sid, detail=meta))
        db.commit()
    finally:
        db.close()


@router.post("/{sid}/analyze")
def analyze(sid: str, bg: BackgroundTasks, db: Session = Depends(get_db), user=Depends(require_role("sales", "architect", "ba"))):
    bg.add_task(_analyze_job, sid, user.id, user.role, user.org_id)
    return {"ok": True, "status": "queued"}


@router.get("/{sid}/scope")
def get_scope(sid: str, v: str = "latest", db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(ScopeVersion).filter(ScopeVersion.session_id == sid).order_by(ScopeVersion.version_no.desc())
    sv = q.first()
    if not sv:
        return {"status": "pending"}
    return {"version_no": sv.version_no, "status": sv.status, "hash": sv.hash, "scope": sv.payload}
