from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ImportJobBase(BaseModel):
    source: str
    details: Optional[Any] = None


class ImportJobCreate(ImportJobBase):
    pass


class ImportJobInDBBase(ImportJobBase):
    id: str
    status: str
    created_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ImportJob(ImportJobInDBBase):
    pass
