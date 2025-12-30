import json
import os
from typing import Dict, Optional
from threading import Lock

DEFAULT_PATH = os.getenv("USERS_FILE", "data/users.json")
_lock = Lock()


def _load_users(path: str = DEFAULT_PATH) -> Dict[str, Dict[str, str]]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users(users: Dict[str, Dict[str, str]], path: str = DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def authenticate(username: str, password: str) -> Optional[Dict[str, str]]:
    with _lock:
        users = _load_users()
        user = users.get(username)
        if user and user.get("password") == password:
            return {"username": username, "role": user.get("role", "user"), "display_name": user.get("display", username)}
    return None


def list_users() -> Dict[str, Dict[str, str]]:
    with _lock:
        return _load_users()


def create_user(username: str, password: str, role: str = "user", display: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    with _lock:
        users = _load_users()
        if username in users:
            raise ValueError("User already exists")
        users[username] = {"password": password, "role": role, "display": display or username}
        _save_users(users)
        return users[username]
