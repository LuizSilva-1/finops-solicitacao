from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    username: str
    role: str
    display_name: Optional[str] = None
    active: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    display_name: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime
