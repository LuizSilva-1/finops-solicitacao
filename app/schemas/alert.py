from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    request_id: str
    type: str
    scheduled_for: datetime


class AlertCreate(AlertBase):
    pass


class AlertInDBBase(AlertBase):
    id: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Alert(AlertInDBBase):
    pass
