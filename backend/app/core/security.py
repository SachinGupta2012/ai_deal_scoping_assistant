"""JWT + RBAC. Backend is source of truth — frontend gates are UX only."""
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db

bearer = HTTPBearer(auto_error=False)

# Enterprise roles for Phase 1
ROLES = ["admin", "sales", "architect", "ba", "delivery", "reviewer", "viewer"]


def create_token(sub: str, org_id: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": sub, "org_id": org_id, "role": role, "exp": exp},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = jwt.decode(creds.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # Lazy import to avoid circular import at startup
    from app.models.tables import User

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*allowed: str):
    allowed_set = set(allowed)

    def checker(user=Depends(get_current_user)):
        if user.role not in allowed_set and user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires role {allowed}")
        return user

    return checker
