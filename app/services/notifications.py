import json
import urllib.request
import logging
from app.core.config import get_settings

logger = logging.getLogger("notifications")


def send_webhook(text: str) -> None:
    settings = get_settings()
    if not settings.webhook_url:
        logger.info("Webhook skipped: WEBHOOK_URL not set")
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
        logger.info("Webhook sent")
    except Exception as exc:
        logger.warning("Webhook failed: %s", exc)
