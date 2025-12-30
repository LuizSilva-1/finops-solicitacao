from pydantic import BaseModel, ConfigDict
from typing import List
from app.schemas.request import Request


class PaginatedRequests(BaseModel):
    items: List[Request]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)
