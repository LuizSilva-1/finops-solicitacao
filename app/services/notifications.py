import json
import urllib.request
import logging
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger("notifications")


def send_webhook(text: str, channel: Optional[str] = None) -> None:
    settings = get_settings()
    if not settings.webhook_url:
        logger.info("Webhook skipped: WEBHOOK_URL not set")
        return
    payload = {"text": text}
    target_channel = channel or settings.webhook_channel
    if target_channel:
        payload["channel"] = target_channel
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
        logger.info("Webhook sent")
    except Exception as exc:
        logger.warning("Webhook failed: %s", exc)
