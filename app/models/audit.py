import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Audit(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("request.id"), nullable=False)
    action = Column(String, nullable=False)
    by = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    at = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("Request", backref="audits")
