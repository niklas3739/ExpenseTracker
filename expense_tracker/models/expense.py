from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Enum as SAEnum
import enum


class SplitType(str, enum.Enum):
    equal = "equal"
    shares = "shares"
    percent = "percent"


class Expense(SQLModel, table=True):
    __tablename__ = "expenses"
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int
    payer_id: str
    amount: float
    description: Optional[str] = None
    date: str  # consider date/datetime type later
    split_type: SplitType = Field(sa_column=Column(SAEnum(SplitType)))


class ExpenseSplit(SQLModel, table=True):
    __tablename__ = "expense_splits"
    id: Optional[int] = Field(default=None, primary_key=True)
    expense_id: int
    user_id: str
    share_value: float
    owed_amount: float


class Settlement(SQLModel, table=True):
    __tablename__ = "settlements"
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int
    from_user_id: str
    to_user_id: str
    amount: float
    date: str
    note: Optional[str] = None