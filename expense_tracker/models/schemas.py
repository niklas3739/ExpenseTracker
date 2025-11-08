from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class SplitType(str, Enum):
    equal = "equal"
    shares = "shares"
    percent = "percent"

# ---- Expense Schemas ----
class ExpenseBase(BaseModel):
    # Make group_id optional so POST /groups/{gid}/expenses works when the body doesn't include it.
    group_id: Optional[int] = None
    payer_id: str
    amount: float
    description: Optional[str] = None
    date: str
    split_type: SplitType

class ExpenseCreate(ExpenseBase):
    """Used when creating an expense (no ID yet). Body won't include group_id."""
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
    """Used when creating a group: now includes member names (string IDs)."""
    members: List[str] = Field(..., min_items=1)

class GroupRead(GroupBase):
    """Returned from the API: include members so the frontend can render pickers."""
    id: int
    members: List[str]

# ---- Group Member ----
class GroupMemberBase(BaseModel):
    group_id: int
    user_id: str

class GroupMemberRead(GroupMemberBase):
    # If your table doesn't have a numeric ID column, you can remove this model or leave it unused.
    # Keeping as-is for compatibility if you reference it elsewhere.
    pass

# ---- Aggregated Responses ----
class GroupSummary(BaseModel):
    group_id: int
    total_expenses: float
    members: List[str]
    balances: Dict[str, float]
