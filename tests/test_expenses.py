from fastapi.testclient import TestClient
from expense_tracker.app import app

def _new_group(client, members):
    r = client.post("/groups/", json={"name": "G-Expenses", "members": members})
    assert r.status_code == 200
    return r.json()["id"]

def test_add_expense_equal_and_list():
    with TestClient(app) as client:
        gid = _new_group(client, ["alice", "bob"])

        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "alice",
            "amount": 30.0,
            "description": "Snacks",
            "date": "2025-10-19",
            "split_type": "equal",
            "splits": [{"user_id": "alice"}, {"user_id": "bob"}]
        })
        assert r.status_code == 200

        r = client.get(f"/groups/{gid}/expenses")
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 1
        assert items[0]["payer_id"] == "alice"
        assert items[0]["amount"] == 30.0
        assert items[0]["split_type"] == "equal"

def test_add_expense_shares_and_percent():
    with TestClient(app) as client:
        gid = _new_group(client, ["alice", "bob", "carol"])

        # shares: 1:2 (alice:bob) on 60 -> owed 20 and 40
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "bob",
            "amount": 60.0,
            "description": "Museum",
            "date": "2025-10-19",
            "split_type": "shares",
            "splits": [
                {"user_id": "alice", "share_value": 1},
                {"user_id": "bob",   "share_value": 2},
            ]
        })
        assert r.status_code == 200

        # percent: 25/75 on 100 -> 25 and 75
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "alice",
            "amount": 100.0,
            "description": "Tickets",
            "date": "2025-10-19",
            "split_type": "percent",
            "splits": [
                {"user_id": "alice", "share_value": 25},
                {"user_id": "bob",   "share_value": 75},
            ]
        })
        assert r.status_code == 200

        r = client.get(f"/groups/{gid}/expenses")
        assert r.status_code == 200
        assert len(r.json()) == 2
