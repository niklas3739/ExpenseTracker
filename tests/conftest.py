import pytest
from fastapi.testclient import TestClient
from expense_tracker.app import app
from expense_tracker.api.deps import get_db
from expense_tracker.core.db import make_memory_engine, create_all_on_engine, session_from_engine

@pytest.fixture
def client():
    engine = make_memory_engine()
    create_all_on_engine(engine)

    def _override_get_db():
        with session_from_engine(engine) as s:
            yield s

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
