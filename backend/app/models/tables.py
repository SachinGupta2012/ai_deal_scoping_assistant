"""SQLAlchemy tables — Phase 1 only. Edits create new scope_versions, never overwrite."""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.db import Base


def uid() -> str:
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, default=uid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin|sales|architect|ba|delivery|reviewer|viewer
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=uid)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    title = Column(String, nullable=False, default="New scoping session")
    opportunity_context = Column(JSONB, default=dict)
    status = Column(String, default="draft")
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=uid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    filename = Column(String, nullable=False)
    raw_path = Column(String, nullable=False)
    normalized_md = Column(Text, nullable=False)
    pii_flags = Column(JSONB, default=list)


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(String, primary_key=True, default=uid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    idx = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=False)
    char_end = Column(Integer, nullable=False)


class RequirementRow(Base):
    __tablename__ = "requirements"
    id = Column(String, primary_key=True, default=uid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    req_id = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, nullable=False)
    chunk_id = Column(String, nullable=False)
    quote = Column(Text, nullable=False)
    origin = Column(String, nullable=False)
    status = Column(String, default="draft")
    version = Column(Integer, default=1)


class ScopeVersion(Base):
    __tablename__ = "scope_versions"
    id = Column(String, primary_key=True, default=uid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    version_no = Column(Integer, nullable=False)
    payload = Column(JSONB, nullable=False)
    hash = Column(String, nullable=False)
    status = Column(String, default="draft")
    created_by = Column(String, nullable=False)
    created_role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=uid)
    org_id = Column(String, nullable=False)
    actor_id = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    detail = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
