from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

class SplitType(str, Enum):
    equal = "equal"
    shares = "shares"
    percent = "percent"


# ---- Expense Schemas ----
class ExpenseBase(BaseModel):
    group_id: int
    payer_id: str
    amount: float
    description: Optional[str] = None
    date: str
    split_type: SplitType


class ExpenseCreate(ExpenseBase):
    """Used when creating an expense (no ID yet)."""
    pass


class ExpenseRead(ExpenseBase):
    """Used when reading expense data (includes ID)."""
    id: int


# ---- Expense Split ----
class ExpenseSplitBase(BaseModel):
    user_id: str
    share_value: float
    owed_amount: float


class ExpenseSplitRead(ExpenseSplitBase):
    id: int
    expense_id: int


# ---- Settlement ----
class SettlementBase(BaseModel):
    group_id: int
    from_user_id: str
    to_user_id: str
    amount: float
    date: str
    note: Optional[str] = None


class SettlementRead(SettlementBase):
    id: int


# ---- Group ----
class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    """Used when creating a group."""
    pass


class GroupRead(GroupBase):
    """Used when returning a group from the API."""
    id: int


# ---- Group Member ----
class GroupMemberBase(BaseModel):
    group_id: int
    user_id: str


class GroupMemberRead(GroupMemberBase):
    id: int


# ---- Aggregated Responses ----
class GroupSummary(BaseModel):
    group_id: int
    total_expenses: float
    members: List[str]
    balances: dict[str, float]
