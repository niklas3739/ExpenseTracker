from typing import Optional
from sqlmodel import SQLModel, Field


class Group(SQLModel, table=True):
    __tablename__ = "groups"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., max_length=128)


class GroupMember(SQLModel, table=True):
    __tablename__ = "group_members"

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="groups.id")
    user_id: str = Field(..., max_length=64)
