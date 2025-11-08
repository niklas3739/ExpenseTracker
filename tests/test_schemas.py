# tests/test_schemas.py
import json
import pytest
from pydantic import ValidationError

from expense_tracker.models.schemas import (
    SplitType,
    ExpenseCreate,
    ExpenseRead,
    ExpenseSplitRead,
    SettlementRead,
    GroupCreate,
    GroupRead,
    GroupMemberRead,
    GroupSummary,
)

# ---------------- SplitType ----------------

def test_split_type_values():
    assert SplitType.equal.value == "equal"
    assert SplitType.shares.value == "shares"
    assert SplitType.percent.value == "percent"
    # enum should be json-serializable to its value
    payload = {"split_type": SplitType.equal}
    dumped = json.dumps(payload, default=lambda o: o.value if hasattr(o, "value") else str(o))
    assert '"equal"' in dumped

# ---------------- Expense ----------------

def test_expense_create_minimal_valid():
    m = ExpenseCreate(
        payer_id="alice",
        amount=12.5,
        description=None,
        date="2025-11-08",
        split_type=SplitType.equal,
    )
    # group_id is optional and should default to None
    assert m.group_id is None
    # enum preserved
    assert m.split_type == SplitType.equal
    # json should contain the enum value string
    data = json.loads(m.model_dump_json())
    assert data["split_type"] == "equal"

def test_expense_create_missing_fields_raises():
    with pytest.raises(ValidationError):
        ExpenseCreate(
            payer_id="alice",
            # amount missing
            date="2025-11-08",
            split_type=SplitType.equal,
        )
    with pytest.raises(ValidationError):
        ExpenseCreate(
            payer_id="alice",
            amount=10,
            # date missing
            split_type=SplitType.equal,
        )
    with pytest.raises(ValidationError):
        ExpenseCreate(
            payer_id="alice",
            amount=10,
            date="2025-11-08",
            # split_type missing
        )

def test_expense_read_allows_group_id_none_and_has_id():
    m = ExpenseRead(
        id=7,
        payer_id="bob",
        amount=33.33,
        description="pizza",
        date="2025-11-08",
        split_type="shares",  # str should coerce to Enum
        group_id=None,
    )
    assert m.id == 7
    assert m.group_id is None
    assert m.split_type == SplitType.shares

# ---------------- ExpenseSplit ----------------

def test_expense_split_read_roundtrip():
    sp = ExpenseSplitRead(
        id=1,
        expense_id=10,
        user_id="carol",
        share_value=2.0,
        owed_amount=15.55,
    )
    dumped = sp.model_dump()
    assert dumped["user_id"] == "carol"
    assert dumped["share_value"] == 2.0
    assert dumped["owed_amount"] == 15.55
    # reconstruct
    sp2 = ExpenseSplitRead(**dumped)
    assert sp2 == sp

# ---------------- Settlement ----------------

def test_settlement_read_valid():
    st = SettlementRead(
        id=5,
        group_id=2,
        from_user_id="alice",
        to_user_id="bob",
        amount=25.0,
        date="2025-11-08",
        note="cash",
    )
    assert st.id == 5
    assert st.group_id == 2
    assert st.from_user_id == "alice"
    assert st.to_user_id == "bob"
    assert st.amount == 25.0

# ---------------- Group ----------------

def test_group_create_with_members_valid():
    g = GroupCreate(name="Trip", members=["alice", "bob"])
    assert g.name == "Trip"
    assert g.members == ["alice", "bob"]

def test_group_create_requires_members():
    with pytest.raises(ValidationError):
        GroupCreate(name="No Members", members=[])

def test_group_read_serialization():
    g = GroupRead(id=1, name="Trip", members=["a", "b", "c"])
    payload = g.model_dump()
    assert payload["id"] == 1
    assert payload["name"] == "Trip"
    assert payload["members"] == ["a", "b", "c"]

# ---------------- GroupMember ----------------

def test_group_member_read_simple():
    gm = GroupMemberRead(group_id=1, user_id="alice")
    assert gm.group_id == 1
    assert gm.user_id == "alice"

# ---------------- GroupSummary ----------------

def test_group_summary_shape_and_types():
    gs = GroupSummary(
        group_id=9,
        total_expenses=123.45,
        members=["alice", "bob"],
        balances={"alice": 61.73, "bob": -61.73},
    )
    assert gs.group_id == 9
    assert gs.total_expenses == 123.45
    assert set(gs.members) == {"alice", "bob"}
    assert isinstance(gs.balances, dict)
    # json encoding/decoding should preserve
    decoded = GroupSummary(**json.loads(gs.model_dump_json()))
    assert decoded == gs
