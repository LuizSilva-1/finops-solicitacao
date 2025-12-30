import time
from typing import Dict

# simple in-memory rate limit per key
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60
_attempts: Dict[str, list] = {}


def allow(key: str) -> bool:
    now = time.time()
    window_start = now - WINDOW_SECONDS
    attempts = [t for t in _attempts.get(key, []) if t > window_start]
    if len(attempts) >= MAX_ATTEMPTS:
        _attempts[key] = attempts
        return False
    attempts.append(now)
    _attempts[key] = attempts
    return True
