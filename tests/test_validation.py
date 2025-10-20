from fastapi.testclient import TestClient
from expense_tracker.app import app

def _new_group(client, name="Val-G", members=("alice", "bob")):
    r = client.post("/groups/", json={"name": name, "members": list(members)})
    return r.json()["id"]

def test_reject_non_member_in_expense():
    with TestClient(app) as client:
        gid = _new_group(client)
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "alice",
            "amount": 10.0,
            "description": "Soda",
            "date": "2025-10-19",
            "split_type": "equal",
            "splits": [{"user_id": "alice"}, {"user_id": "mallory"}]  # mallory not in group
        })
        assert r.status_code == 400

def test_reject_non_positive_amount():
    with TestClient(app) as client:
        gid = _new_group(client)
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "alice",
            "amount": 0.0,
            "description": "Free?",
            "date": "2025-10-19",
            "split_type": "equal",
            "splits": [{"user_id": "alice"}, {"user_id": "bob"}]
        })
        # Your pydantic Field(gt=0) may trigger 422; handler might return 400 — accept either.
        assert r.status_code in (400, 422)

def test_percent_must_sum_to_100():
    with TestClient(app) as client:
        gid = _new_group(client)
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "alice",
            "amount": 50.0,
            "description": "Gift",
            "date": "2025-10-19",
            "split_type": "percent",
            "splits": [
                {"user_id": "alice", "share_value": 10},
                {"user_id": "bob",   "share_value": 10},
            ]
        })
        assert r.status_code == 400

def test_invalid_split_type_is_rejected():
    with TestClient(app) as client:
        gid = _new_group(client)
        r = client.post(f"/groups/{gid}/expenses", json={
            "payer_id": "alice",
            "amount": 15.0,
            "description": "Snack",
            "date": "2025-10-19",
            "split_type": "weird",  # invalid
            "splits": [{"user_id": "alice"}, {"user_id": "bob"}]
        })
        # Could be 422 (pydantic pattern) or 400 (manual validation), accept either.
        assert r.status_code in (400, 422)
