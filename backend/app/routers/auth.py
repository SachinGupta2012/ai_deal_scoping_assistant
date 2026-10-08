"""Auth: seed owner + login -> JWT."""
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import create_token
from app.models.tables import Organization, User

router = APIRouter(prefix="/auth", tags=["auth"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginIn(BaseModel):
    email: str
    password: str


@router.post("/seed-owner")
def seed_owner(db: Session = Depends(get_db)):
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
    return {"access_token": create_token(u.id, u.org_id, u.role), "role": u.role}
