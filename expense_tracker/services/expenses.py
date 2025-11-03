from typing import Iterable, List, Optional, Sequence, Tuple
from sqlmodel import Session, select
from expense_tracker.models.group import Group, GroupMember
from expense_tracker.models.expense import Expense, ExpenseSplit, Settlement, SplitType
from expense_tracker.services.errors import GroupNotFound, ExpenseNotFound, SplitValidationError
from expense_tracker.services.balance import compute_balances, payout_suggestions
from expense_tracker.services.splits import normalize_splits


# ---------- Helpers ----------

def _ensure_group_exists(session: Session, gid: int) -> None:
    if session.get(Group, gid) is None:
        raise GroupNotFound(f"group id {gid} not found")


def _get_group_member_ids(session: Session, gid: int) -> List[str]:
    stmt = select(GroupMember.user_id).where(GroupMember.group_id == gid)
    return [row[0] for row in session.exec(stmt).all()]


def _attach_expense_splits(session: Session, expense_id: int, splits: Sequence[ExpenseSplit]) -> None:
    # Ensure splits reference the new expense id
    for sp in splits:
        sp.expense_id = expense_id
        session.add(sp)


# ---------- Services ----------

def create_expense(
    session: Session,
    *,
    group_id: int,
    payer_id: str,
    amount: float,
    split_type: SplitType | str,
    description: Optional[str] = None,
    date: str,
    splits: Optional[Iterable[ExpenseSplit | dict]] = None,
) -> Tuple[Expense, List[ExpenseSplit]]:
    """
    Create an expense and its normalized splits.
    - Validates group existence
    - Normalizes splits based on split_type
    - Persists Expense and ExpenseSplit rows
    Returns (expense, splits_list)
    Raises GroupNotFound, SplitValidationError on invalid inputs.
    """
    _ensure_group_exists(session, group_id)

    # Build a canonical list of "input split" objects for normalization
    input_splits: List[ExpenseSplit] = []
    if splits:
        for item in splits:
            if isinstance(item, ExpenseSplit):
                input_splits.append(item)
            else:
                user_id = item.get("user_id")
                share_value = item.get("share_value")
                input_splits.append(ExpenseSplit(expense_id=0, user_id=user_id, share_value=share_value, owed_amount=0.0))

    members = _get_group_member_ids(session, group_id)
    normalized: List[ExpenseSplit] = normalize_splits(
        amount=amount,
        split_type=str(split_type),
        members=members,
        splits=input_splits,
    )

    expense = Expense(
        group_id=group_id,
        payer_id=payer_id,
        amount=amount,
        description=description,
        date=date,
        split_type=SplitType(split_type) if not isinstance(split_type, SplitType) else split_type,
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)

    _attach_expense_splits(session, expense.id, normalized)
    session.commit()

    # Refresh splits (ensure db-generated ids are present)
    saved_splits = list(
        session.exec(select(ExpenseSplit).where(ExpenseSplit.expense_id == expense.id)).all()
    )
    return expense, saved_splits


def record_settlement(
    session: Session,
    *,
    group_id: int,
    from_user_id: str,
    to_user_id: str,
    amount: float,
    date: str,
    note: Optional[str] = None,
) -> Settlement:
    """
    Record a settlement (manual payment) between two users in a group.
    """
    _ensure_group_exists(session, group_id)
    settlement = Settlement(
        group_id=group_id,
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        amount=amount,
        date=date,
        note=note,
    )
    session.add(settlement)
    session.commit()
    session.refresh(settlement)
    return settlement


def get_group_summary(session: Session, group_id: int) -> dict:
    """
    Compute and return a summary dict for the group:
      - total_expenses
      - balances {user_id: balance}
      - payout_suggestions [{from, to, amount}]
      - members [user_id]
    Raises GroupNotFound if group_id doesn't exist.
    """
    _ensure_group_exists(session, group_id)

    # total expenses
    total = 0.0
    for ex in session.exec(select(Expense).where(Expense.group_id == group_id)).all():
        total += ex.amount
    total = round(total, 2)

    members = _get_group_member_ids(session, group_id)
    balances = compute_balances(session, group_id)
    suggestions = payout_suggestions(balances)

    return {
        "group_id": group_id,
        "members": members,
        "total_expenses": total,
        "balances": balances,
        "payout_suggestions": suggestions,
    }


def get_expense_with_splits(session: Session, expense_id: int) -> tuple[Expense, List[ExpenseSplit]]:
    """
    Return an expense and all its splits. Raises ExpenseNotFound if not exists.
    """
    exp = session.get(Expense, expense_id)
    if exp is None:
        raise ExpenseNotFound(f"expense id {expense_id} not found")
    splits = list(session.exec(select(ExpenseSplit).where(ExpenseSplit.expense_id == expense_id)).all())
    return exp, splits
