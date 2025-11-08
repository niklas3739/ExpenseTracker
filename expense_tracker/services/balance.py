from typing import Dict, List, Tuple
from sqlmodel import Session, select
from expense_tracker.models.group import GroupMember
from expense_tracker.models.expense import Expense, ExpenseSplit, Settlement


def compute_balances(s: Session, gid: int) -> Dict[str, float]:
    """
    Compute per-user balances for a group:
      +amount for what a user paid,
      -amount for what a user owes via splits,
      settlements adjust balances accordingly.
    Returns rounded balances per user_id.
    """
    stmt_members = select(GroupMember).where(GroupMember.group_id == gid)
    members = [m.user_id for m in s.exec(stmt_members).all()]
    balances: Dict[str, float] = {u: 0.0 for u in members}

    for ex in s.exec(select(Expense).where(Expense.group_id == gid)).all():
        balances[ex.payer_id] = balances.get(ex.payer_id, 0.0) + ex.amount
        for sp in s.exec(select(ExpenseSplit).where(ExpenseSplit.expense_id == ex.id)).all():
            balances[sp.user_id] = balances.get(sp.user_id, 0.0) - sp.owed_amount

    for st in s.exec(select(Settlement).where(Settlement.group_id == gid)).all():
        balances[st.from_user_id] = balances.get(st.from_user_id, 0.0) - st.amount
        balances[st.to_user_id] = balances.get(st.to_user_id, 0.0) + st.amount

    return {u: round(v, 2) for u, v in balances.items()}


def payout_suggestions(balances: Dict[str, float]) -> List[dict]:
    """
    Produce a minimal set of peer-to-peer payouts to settle balances.
    Returns a list of dicts: {"from": debtor, "to": creditor, "amount": value}
    """
    creditors: List[Tuple[str, float]] = sorted(
        [(u, v) for u, v in balances.items() if v > 0], key=lambda x: -x[1]
    )
    debtors: List[Tuple[str, float]] = sorted(
        [(u, -v) for u, v in balances.items() if v < 0], key=lambda x: -x[1]
    )
    i = j = 0
    suggestions: List[dict] = []
    while i < len(creditors) and j < len(debtors):
        cu, ca = creditors[i]
        du, da = debtors[j]
        pay = round(min(ca, da), 2)
        if pay > 0:
            suggestions.append({"from": du, "to": cu, "amount": pay})
            ca = round(ca - pay, 2)
            da = round(da - pay, 2)
        if ca == 0:
            i += 1
        else:
            creditors[i] = (cu, ca)
        if da == 0:
            j += 1
        else:
            debtors[j] = (du, da)
    return suggestions
