import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, JSON

from app.db.base_class import Base


class ImportJob(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False)  # csv | json
    status = Column(String, nullable=False, default="pendente")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    details = Column(JSON, nullable=True)
