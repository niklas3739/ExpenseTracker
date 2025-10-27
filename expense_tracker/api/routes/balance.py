from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from expense_tracker.api.deps import get_db
from expense_tracker.models.group import Group
from expense_tracker.schemas.balance import BalanceRead
from expense_tracker.services.balance import compute_balances, payout_suggestions

router = APIRouter(prefix="/groups/{gid}", tags=["balance"])


@router.get("/balance", response_model=BalanceRead)
def group_balance(gid: int, s: Session = Depends(get_db)):
    if not s.get(Group, gid):
        raise HTTPException(404, detail="group not found")
    balances = compute_balances(s, gid)
    suggestions = payout_suggestions(balances)
    return BalanceRead(balances=balances, suggestions=suggestions)