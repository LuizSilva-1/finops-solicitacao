import time
from datetime import datetime, date, timedelta
import logging

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

CHECK_INTERVAL_SECONDS = 60
STARTUP_GRACE_SECONDS = 5


def expire_overdue(db: Session):
    today = date.today()
    overdue = (
        db.query(models.request.Request)
        .filter(models.request.Request.status.in_(["pendente", "aprovado", "em_uso"]))
        .filter(models.request.Request.expires_at <= today)
        .all()
    )
    for req in overdue:
        req.status = "expirado"
        req.last_alert_at = datetime.utcnow()
        db.add(req)
        audit = models.audit.Audit(request_id=req.id, action="expired_auto", by="worker")
        db.add(audit)
        logger.info("Marked request %s as expirado", req.id)
    db.commit()


def main():
    logger.info("Worker started")
    time.sleep(STARTUP_GRACE_SECONDS)  # give DB time to come up
    while True:
        db = SessionLocal()
        try:
            expire_overdue(db)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Worker error: %s", exc)
            db.rollback()
        finally:
            db.close()
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
