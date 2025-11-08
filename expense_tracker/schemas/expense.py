from typing import Optional, List
from pydantic import BaseModel, Field


class SplitInput(BaseModel):
    user_id: str
    share_value: Optional[float] = None


class ExpenseCreate(BaseModel):
    payer_id: str
    amount: float = Field(gt=0)
    description: Optional[str] = None
    date: str
    split_type: str = Field(pattern="^(equal|shares|percent)$")
    splits: List[SplitInput]


class ExpenseRead(BaseModel):
    id: int
    payer_id: str
    amount: float
    description: Optional[str]
    date: str
    split_type: str

    model_config = {
        "from_attributes": True,
    }


class SettlementCreate(BaseModel):
    from_user_id: str
    to_user_id: str
    amount: float = Field(gt=0)
    date: str
    note: Optional[str] = None