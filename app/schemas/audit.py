from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class AuditBase(BaseModel):
    request_id: str
    action: str
    by: str
    details: Optional[Any] = None


class AuditCreate(AuditBase):
    pass


class AuditInDBBase(AuditBase):
    id: str
    at: datetime

    model_config = ConfigDict(from_attributes=True)


class Audit(AuditInDBBase):
    pass
