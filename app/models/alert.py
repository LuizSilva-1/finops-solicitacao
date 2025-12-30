import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Alert(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("request.id"), nullable=False)
    type = Column(String, nullable=False)  # reminder | expiration
    scheduled_for = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="pendente")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("Request", backref="alerts")
