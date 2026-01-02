from datetime import date, datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class RequestBase(BaseModel):
    requester: Optional[str] = None
    service_type: str
    params: Optional[str] = None
    cost_center: Optional[str] = None
    tags: Optional[str] = None
    region: Optional[str] = None
    aws_account: Optional[str] = None
    expires_at: date
    retention_days: Optional[int] = None
    resource_id: Optional[str] = None
    estimated_cost: Optional[str] = None
    auto_delete: bool = False
    approver: Optional[str] = None


class RequestCreate(RequestBase):
    pass


class RequestUpdate(BaseModel):
    status: Optional[str] = None
    expires_at: Optional[date] = None
    retention_days: Optional[int] = None
    approver: Optional[str] = None


class RequestInDBBase(RequestBase):
    id: str = Field(..., alias="id")
    status: str
    created_at: datetime
    last_alert_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Request(RequestInDBBase):
    pass
