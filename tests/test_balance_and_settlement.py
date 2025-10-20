from fastapi.testclient import TestClient
from expense_tracker.app import app

def test_balance_then_settlement():
    with TestClient(app) as client:
        # group
        r = client.post("/groups/", json={"name": "Trip-B", "members": ["alice", "bob", "carol"]})
        gid = r.json()["id"]

        # expense 1: alice pays 60, equal among 3 → each owes 20
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "alice",
            "amount": 60.0,
            "description": "Dinner",
            "date": "2025-10-06",
            "split_type": "equal",
            "splits": [{"user_id":"alice"},{"user_id":"bob"},{"user_id":"carol"}]
        })
        assert r.status_code == 200

        # expense 2: bob pays 60, shares 1:2 (alice:bob) → alice owes 20, bob owes 40
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "bob",
            "amount": 60.0,
            "description": "Museum",
            "date": "2025-10-06",
            "split_type": "shares",
            "splits": [{"user_id":"alice","share_value":1},{"user_id":"bob","share_value":2}]
        })
        assert r.status_code == 200

        # balances
        r = client.get(f"/groups/{gid}/balance")
        assert r.status_code == 200
        balances = r.json()["balances"]
        assert balances["alice"] == 20.0   # gets 20
        assert balances["bob"] == 00.0   # gets 20
        assert balances["carol"] == -20.0  # owes 40

        # settlement: carol pays 20 to alice
        r = client.post(f"/groups/{gid}/settlements", json={
            "from_user_id": "carol",
            "to_user_id": "alice",
            "amount": 20.0,
            "date": "2025-10-07"
        })
        assert r.status_code == 200

        # balances again
        r = client.get(f"/groups/{gid}/balance")
        b2 = r.json()["balances"]
        assert b2["alice"] == 40.0
        assert b2["bob"] == 0.0
        assert b2["carol"] == -40.0
