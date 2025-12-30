from typing import Dict, Optional
from fastapi import Depends, HTTPException, Header
from starlette import status
from sqlalchemy.orm import Session

from app.services import auth_service
from app.db.session import get_db
from app import models


def get_current_user(token: Optional[str] = Header(default=None, alias="X-Auth-Token"), db: Session = Depends(get_db)) -> models.user.User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = auth_service.decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.user.User).filter(models.user.User.id == payload.get("sub")).first()
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    return user


def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user
