from sqlmodel import Session
from fastapi import Depends
from expense_tracker.core.db import get_session


def get_db(session: Session = Depends(get_session)) -> Session:
    return session