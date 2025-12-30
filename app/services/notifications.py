import json
import urllib.request
from app.core.config import get_settings


def send_webhook(text: str) -> None:
    settings = get_settings()
    if not settings.webhook_url:
        return
    payload = {"text": text}
    if settings.webhook_channel:
        payload["channel"] = settings.webhook_channel
    if settings.webhook_username:
        payload["username"] = settings.webhook_username
    req = urllib.request.Request(
        settings.webhook_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
            resp.read()
    except Exception:
        # Fail silently to not break the flow
        return
