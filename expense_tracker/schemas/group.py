from typing import List
from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: str
    members: List[str] = Field(default_factory=list)


class GroupRead(BaseModel):
    id: int
    name: str
    members: List[str]

    model_config = {
        "from_attributes": True,
    }