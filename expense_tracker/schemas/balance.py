from typing import Dict, List
from pydantic import BaseModel, Field


class BalanceRead(BaseModel):
    balances: Dict[str, float]
    suggestions: List[dict] = Field(default_factory=list)