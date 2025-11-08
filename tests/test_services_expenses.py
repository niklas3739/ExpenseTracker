# tests/test_services_expenses.py
import pytest
from sqlmodel import SQLModel, create_engine, Session, select

from expense_tracker.models.group import Group, GroupMember
from expense_tracker.models.expense import Expense, ExpenseSplit, Settlement, SplitType
from expense_tracker.services.expenses import (
    create_expense,
    get_expense_with_splits,
    get_group_summary,
    record_settlement,
)
from expense_tracker.services.errors import GroupNotFound, ExpenseNotFound

# ---------- Test fixtures ----------

@pytest.fixture()
def engine():
    # In-memory SQLite for isolated, fast tests
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture()
def session(engine):
    with Session(engine) as s:
        yield s

@pytest.fixture()
def sample_group(session: Session):
    """
    Create a group with member user_ids. We seed with full names,
    but tests will read back what the DB actually stored.
    """
    g = Group(name="Trip to Rome")
    session.add(g)
    session.commit()
    session.refresh(g)

    for uid in ["alice", "bob", "carol"]:
        session.add(GroupMember(group_id=g.id, user_id=uid))
    session.commit()
    return g

# ---------- Helpers ----------

def get_members(session: Session, gid: int) -> set[str]:
    rows = session.exec(select(GroupMember.user_id).where(GroupMember.group_id == gid)).all()
    return set(r[0] for r in rows)

def total_split_amount(session: Session, expense_id: int) -> float:
    rows = session.exec(select(ExpenseSplit).where(ExpenseSplit.expense_id == expense_id)).all()
    return round(sum(r.owed_amount for r in rows), 2)

# ---------- Tests: create_expense ----------

def test_create_expense_equal_split(session: Session, sample_group: Group):
    """
    Creates an expense with equal split among members (no custom splits provided).
    Expects: one Expense persisted + one ExpenseSplit per member summing to the total.
    """
    amount = 90.0
    expense, splits = create_expense(
        session,
        group_id=sample_group.id,
        payer_id="alice",
        amount=amount,
        split_type=SplitType.equal,  # with your service fix (enum.value passed into normalize_splits)
        description="Dinner",
        date="2025-11-08",
        splits=None,
    )

    # DB checks
    assert expense.id is not None
    assert expense.group_id == sample_group.id
    assert expense.payer_id == "alice"
    assert float(expense.amount) == amount
    assert expense.split_type == SplitType.equal

    # There should be one split per member
    expected_members = get_members(session, sample_group.id)
    assert len(splits) == len(expected_members)

    # Splits sum to the expense amount
    assert total_split_amount(session, expense.id) == round(amount, 2)

    # Each split references this expense and uses a valid member id
    for sp in splits:
        assert sp.expense_id == expense.id
        assert sp.user_id in expected_members

# ---------- Tests: error case ----------

def test_create_expense_group_not_found(session: Session):
    with pytest.raises(GroupNotFound):
        create_expense(
            session,
            group_id=999,
            payer_id="someone",
            amount=10.0,
            split_type="equal",
            description=None,
            date="2025-11-08",
            splits=None,
        )

# ---------- Tests: get_expense_with_splits ----------

def test_get_expense_with_splits_ok(session: Session, sample_group: Group):
    exp, splits = create_expense(
        session,
        group_id=sample_group.id,
        payer_id="bob",
        amount=60.0,
        split_type="equal",
        description="Museum tickets",
        date="2025-11-08",
        splits=None,
    )

    got_exp, got_splits = get_expense_with_splits(session, exp.id)
    assert got_exp.id == exp.id
    assert len(got_splits) == len(splits)
    assert {s.user_id for s in got_splits} == get_members(session, sample_group.id)

def test_get_expense_with_splits_not_found(session: Session):
    with pytest.raises(ExpenseNotFound):
        get_expense_with_splits(session, 42)

# ---------- Tests: record_settlement ----------

def test_record_settlement(session: Session, sample_group: Group):
    st = record_settlement(
        session,
        group_id=sample_group.id,
        from_user_id="carol",
        to_user_id="alice",
        amount=25.50,
        date="2025-11-08",
        note="Cash payback",
    )

    assert st.id is not None
    assert st.group_id == sample_group.id
    assert st.from_user_id == "carol"
    assert st.to_user_id == "alice"
    assert float(st.amount) == 25.50

# ---------- Tests: get_group_summary ----------

def test_get_group_summary(session: Session, sample_group: Group):
    # Two expenses: 90 + 60
    create_expense(
        session,
        group_id=sample_group.id,
        payer_id="alice",
        amount=90.0,
        split_type="equal",
        description="Dinner",
        date="2025-11-08",
        splits=None,
    )
    create_expense(
        session,
        group_id=sample_group.id,
        payer_id="bob",
        amount=60.0,
        split_type="equal",
        description="Tickets",
        date="2025-11-08",
        splits=None,
    )

    summary = get_group_summary(session, sample_group.id)

    # basic structure
    assert summary["group_id"] == sample_group.id
    assert set(summary["members"]) == get_members(session, sample_group.id)
    assert isinstance(summary["balances"], dict)
    assert isinstance(summary["payout_suggestions"], list)

    # total_expenses should be 150.00
    assert float(summary["total_expenses"]) == 150.0

    # Balances should sum to 0 (someone is owed; others owe)
    total_balance = round(sum(float(v) for v in summary["balances"].values()), 6)
    assert total_balance == 0.0
