from fastapi.testclient import TestClient
from expense_tracker.app import app
from expense_tracker.api.deps import get_db
from expense_tracker.core.db import make_memory_engine, create_all_on_engine, session_from_engine

def test_create_and_get_group(client):
    r = client.post("/groups/", json={"name": "Trip", "members": ["alice", "bob"]})
    assert r.status_code == 200
    gid = r.json()["id"]

    r = client.get(f"/groups/{gid}")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Trip"
    assert sorted(data["members"]) == ["alice", "bob"]

def test_create_group_rejects_empty_name(client):
    r = client.post("/groups/", json={"name": "   ", "members": []})
    assert r.status_code == 400
