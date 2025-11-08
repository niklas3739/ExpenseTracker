from __future__ import annotations
import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.pool import StaticPool

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
_engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def get_engine():
    """Return the global SQLModel engine (do not create engines elsewhere)."""
    return _engine

def create_db_and_tables() -> None:
    """Create all tables if they don't exist yet."""
    from expense_tracker.models.expense import Expense, ExpenseSplit, Settlement
    from expense_tracker.models.group import Group, GroupMember
    SQLModel.metadata.create_all(_engine)

# Backward-compatible alias so your lifespan still calls init_db()
def init_db() -> None:
    create_db_and_tables()

def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency generator for DB sessions."""
    with Session(_engine) as session:
        yield session

# ---------- Test helpers ----------
def make_memory_engine():
    """Create an in-memory SQLite engine that persists across sessions."""
    return create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@contextmanager
def session_from_engine(engine) -> Generator[Session, None, None]:
    """Open/close a Session bound to a specific engine (useful in tests)."""
    with Session(engine) as s:
        yield s

def create_all_on_engine(engine) -> None:
    """Create the schema on a given engine (useful for tests)."""
    from expense_tracker.models.expense import Expense, ExpenseSplit, Settlement
    from expense_tracker.models.group import Group, GroupMember
    SQLModel.metadata.create_all(engine)
