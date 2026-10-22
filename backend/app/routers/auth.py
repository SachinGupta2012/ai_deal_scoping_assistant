"""Auth: seed owner + login -> JWT."""
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.core.security import ROLES, create_token, get_current_user, require_role
from app.models.tables import Organization, User

router = APIRouter(prefix="/auth", tags=["auth"])
pwd = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


class LoginIn(BaseModel):
    email: str
    password: str


class CreateUserIn(BaseModel):
    email: str
    password: str
    role: str


def _public_user(user: User) -> dict:
    return {"id": user.id, "email": user.email, "role": user.role, "org_id": user.org_id}


@router.post("/seed-owner")
def seed_owner(db: Session = Depends(get_db)):
    if settings.ENV != "development" or not settings.ALLOW_DEV_SEED_OWNER:
        raise HTTPException(status_code=403, detail="Seed owner is development-only")
    org = db.query(Organization).first() or Organization(name="default")
    if not db.query(Organization).first():
        db.add(org)
        db.commit()
        db.refresh(org)
    if db.query(User).filter(User.email == "owner@local.dev").first():
        return {"ok": True, "exists": True}
    u = User(org_id=org.id, email="owner@local.dev", password_hash=pwd.hash("Owner123!"), role="admin")
    db.add(u)
    db.commit()
    return {"ok": True, "email": "owner@local.dev", "password": "Owner123!"}


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == body.email).first()
    if not u or not pwd.verify(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(u.id, u.org_id, u.role), "user": _public_user(u)}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"user": _public_user(user)}


@router.get("/users")
def list_users(db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    users = db.query(User).filter(User.org_id == user.org_id).order_by(User.created_at.desc()).all()
    return {"users": [_public_user(row) for row in users]}


@router.post("/users")
def create_user(body: CreateUserIn, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    email = body.email.strip().lower()
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Invalid email")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Allowed roles: {ROLES}")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="User already exists")
    created = User(org_id=user.org_id, email=email, password_hash=pwd.hash(body.password), role=body.role)
    db.add(created)
    db.commit()
    db.refresh(created)
    return {"user": _public_user(created)}
