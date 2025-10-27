from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from expense_tracker.api.deps import get_db
from expense_tracker.models.group import Group, GroupMember
from expense_tracker.models.expense import Expense, ExpenseSplit
from expense_tracker.schemas.expense import ExpenseCreate, ExpenseRead
from expense_tracker.services.splits import normalize_splits

router = APIRouter(prefix="/groups/{gid}/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead)
def add_expense(gid: int, payload: ExpenseCreate, s: Session = Depends(get_db)):
    if payload.amount <= 0:
        raise HTTPException(400, detail="amount must be > 0")

    g = s.get(Group, gid)
    if not g:
        raise HTTPException(404, detail="group not found")

    members = [m.user_id for m in s.exec(select(GroupMember).where(GroupMember.group_id == gid))]

    users_to_check = [payload.payer_id] + [sp.user_id for sp in payload.splits]
    missing = [u for u in users_to_check if u not in set(members)]
    if missing:
        raise HTTPException(400, detail=f"Users not in group: {missing}")

    norm = normalize_splits(payload.amount, payload.split_type, members, payload.splits)

    ex = Expense(
        group_id=gid,
        payer_id=payload.payer_id,
        amount=payload.amount,
        description=payload.description,
        date=payload.date,
        split_type=payload.split_type,  # stored as enum by SA column
    )
    s.add(ex)
    s.commit()
    s.refresh(ex)

    for sp in norm:
        sp.expense_id = ex.id
        s.add(sp)
    s.commit()

    return ExpenseRead(
        id=ex.id,
        payer_id=ex.payer_id,
        amount=ex.amount,
        description=ex.description,
        date=ex.date,
        split_type=str(ex.split_type),
    )


@router.get("", response_model=List[ExpenseRead])
def list_expenses(gid: int, s: Session = Depends(get_db)):
    if not s.get(Group, gid):
        raise HTTPException(404, detail="group not found")
    rows = s.exec(select(Expense).where(Expense.group_id == gid)).all()
    return [
        ExpenseRead(
            id=r.id,
            payer_id=r.payer_id,
            amount=r.amount,
            description=r.description,
            date=r.date,
            split_type=str(r.split_type),
        )
        for r in rows
    ]