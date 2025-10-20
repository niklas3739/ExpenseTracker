import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine
from sqlalchemy.pool import StaticPool
import expense_tracker.app as app_module

@pytest.fixture(scope="function")
def client():
    """Fresh TestClient + in-memory DB for each test."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Replace the app’s engine
    app_module.engine = test_engine

    # Recreate schema
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

    with TestClient(app_module.app) as c:
        yield c
