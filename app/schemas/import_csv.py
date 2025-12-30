from pydantic import BaseModel, ConfigDict
from typing import List


class ImportResult(BaseModel):
    created: List[str]
    count: int

    model_config = ConfigDict(from_attributes=True)
