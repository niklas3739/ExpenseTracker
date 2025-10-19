from fastapi.testclient import TestClient
from expense_tracker.app import app

client = TestClient(app)

def test_create_group_minimal():
    """Check that a group can be created and fetched."""
    # create group
    r = client.post("/groups/", json={"name": "TestGroup", "members": ["alice", "bob"]})
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    gid = data["id"]

    # fetch same group
    r = client.get(f"/groups/{gid}")
    assert r.status_code == 200
    g = r.json()
    assert g["name"] == "TestGroup"
    assert sorted(g["members"]) == ["alice", "bob"]

def test_add_simple_expense():
    """Add an expense to a new group."""
    # create group
    r = client.post("/groups/", json={"name": "Dinner", "members": ["alice", "bob"]})
    gid = r.json()["id"]

    # add expense (equal split)
    r = client.post(f"/groups/{gid}/expenses", json={
        "payer_id": "alice",
        "amount": 20.0,
        "description": "Pizza",
        "date": "2025-10-19",
        "split_type": "equal",
        "splits": [{"user_id": "alice"}, {"user_id": "bob"}]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["payer_id"] == "alice"
    assert data["amount"] == 20.0