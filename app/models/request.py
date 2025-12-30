import uuid
from datetime import datetime, date
from sqlalchemy import Boolean, Column, DateTime, String, JSON, Date, Integer, Text

from app.db.base_class import Base


class Request(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    requester = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
    params = Column(Text, nullable=True)
    cost_center = Column(String, nullable=True)
    tags = Column(Text, nullable=True)
    region = Column(String, nullable=True)
    aws_account = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pendente")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(Date, nullable=False)
    retention_days = Column(Integer, nullable=True)
    resource_id = Column(String, nullable=True)
    estimated_cost = Column(String, nullable=True)
    auto_delete = Column(Boolean, default=False)
    approver = Column(String, nullable=True)
    last_alert_at = Column(DateTime, nullable=True)
