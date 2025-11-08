from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Enum as SAEnum
import enum


class SplitType(str, enum.Enum):
    equal = "equal"
    shares = "shares"
    percent = "percent"
    # exact = "exact"  # uncomment when support exact-amount splits


class Expense(SQLModel, table=True):
    __tablename__ = "expenses"
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="groups.id")
    payer_id: str = Field(..., max_length=64)
    amount: float
    description: Optional[str] = None
    date: str  # keep as str to match your current API
    split_type: SplitType = Field(sa_column=Column(SAEnum(SplitType)))


class ExpenseSplit(SQLModel, table=True):
    __tablename__ = "expense_splits"
    id: Optional[int] = Field(default=None, primary_key=True)
    expense_id: int = Field(foreign_key="expenses.id")
    user_id: str = Field(..., max_length=64)
    share_value: float
    owed_amount: float


class Settlement(SQLModel, table=True):
    __tablename__ = "settlements"
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="groups.id")
    from_user_id: str = Field(..., max_length=64)
    to_user_id: str = Field(..., max_length=64)
    amount: float
    date: str
    note: Optional[str] = None
