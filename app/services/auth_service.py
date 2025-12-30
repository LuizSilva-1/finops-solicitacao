import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app import models
from app.core.config import get_settings

ALGO = "HS256"
ACCESS_EXPIRE_MINUTES = 30
REFRESH_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_tokens(user: models.user.User) -> Tuple[str, str]:
    settings = get_settings()
    now = datetime.utcnow()
    access_payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "display_name": user.display_name,
        "exp": now + timedelta(minutes=ACCESS_EXPIRE_MINUTES),
        "type": "access",
    }
    refresh_payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "exp": now + timedelta(days=REFRESH_EXPIRE_DAYS),
        "type": "refresh",
    }
    access = jwt.encode(access_payload, settings.secret_key, algorithm=ALGO)
    refresh = jwt.encode(refresh_payload, settings.secret_key, algorithm=ALGO)
    return access, refresh


def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[ALGO])


def get_user_by_username(db: Session, username: str) -> Optional[models.user.User]:
    return db.query(models.user.User).filter(models.user.User.username == username).first()


def create_user(db: Session, username: str, password: str, role: str, display: Optional[str] = None) -> models.user.User:
    if get_user_by_username(db, username):
        raise ValueError("User already exists")
    user = models.user.User(username=username, password_hash=hash_password(password), role=role, display_name=display)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
