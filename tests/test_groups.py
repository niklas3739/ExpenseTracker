from fastapi.testclient import TestClient
from expense_tracker.app import app

def test_create_and_get_group():
    with TestClient(app) as client:
        r = client.post("/groups/", json={"name": "Trip", "members": ["alice", "bob"]})
        assert r.status_code == 200
        gid = r.json()["id"]

        r = client.get(f"/groups/{gid}")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Trip"
        assert sorted(data["members"]) == ["alice", "bob"]

def test_create_group_rejects_empty_name():
    with TestClient(app) as client:
        r = client.post("/groups/", json={"name": "   ", "members": []})
        assert r.status_code == 400
