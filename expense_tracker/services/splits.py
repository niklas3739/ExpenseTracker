from typing import List
from expense_tracker.services.errors import SplitValidationError
from expense_tracker.models.expense import ExpenseSplit


def normalize_splits(amount: float, split_type: str, members: List[str], splits: List) -> List[ExpenseSplit]:
    """
    Normalize and validate splits for a given expense.
    Returns a list of ExpenseSplit (with expense_id=0 placeholder; caller sets actual id).
      - split_type == "equal": divide equally among provided splits' users or all members.
      - split_type == "shares": proportional by integer/float 'share_value' per user.
      - split_type == "percent": exact percent per user; must sum to 100.
    Raises SplitValidationError for invalid inputs.
    """
    if split_type == "equal":
        users = [sp.user_id for sp in splits] or members
        n = len(users)
        if n == 0:
            raise SplitValidationError("No users provided for equal split", code="equal_missing_users")
        each = round(amount / n, 2)
        owed = [each] * n
        # Fix rounding drift on first user
        delta = round(amount - sum(owed), 2)
        if delta != 0:
            owed[0] = round(owed[0] + delta, 2)
        return [ExpenseSplit(expense_id=0, user_id=u, share_value=1.0, owed_amount=o) for u, o in zip(users, owed)]

    if split_type == "shares":
        if not splits:
            raise SplitValidationError("shares requires splits with share_value", code="shares_missing")
        total = sum((sp.share_value or 0) for sp in splits)
        if total <= 0:
            raise SplitValidationError("sum of shares must be > 0", code="shares_sum_le_zero")
        result = []
        acc = 0.0
        for sp in splits:
            share = sp.share_value or 0
            owed = round(amount * (share / total), 2)
            acc += owed
            result.append((sp.user_id, share, owed))
        delta = round(amount - acc, 2)
        if delta != 0 and result:
            user, sv, owed = result[0]
            result[0] = (user, sv, round(owed + delta, 2))
        return [ExpenseSplit(expense_id=0, user_id=u, share_value=sv, owed_amount=o) for u, sv, o in result]

    if split_type == "percent":
        if not splits:
            raise SplitValidationError("percent requires splits with share_value=percent", code="percent_missing")
        total = round(sum((sp.share_value or 0) for sp in splits), 2)
        if abs(total - 100.0) > 0.01:
            raise SplitValidationError("sum of percents must be 100", code="percent_sum_not_100")
        result = []
        acc = 0.0
        for sp in splits:
            pct = sp.share_value or 0
            owed = round(amount * (pct / 100.0), 2)
            acc += owed
            result.append((sp.user_id, pct, owed))
        delta = round(amount - acc, 2)
        if delta != 0 and result:
            user, sv, owed = result[0]
            result[0] = (user, sv, round(owed + delta, 2))
        return [ExpenseSplit(expense_id=0, user_id=u, share_value=sv, owed_amount=o) for u, sv, o in result]

    raise SplitValidationError("invalid split_type", code="invalid_type")
