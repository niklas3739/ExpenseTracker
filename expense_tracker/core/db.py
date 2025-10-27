from sqlmodel import SQLModel, create_engine, Session

ENGINE_URL = "sqlite:///./dev.db"
engine = create_engine(ENGINE_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency generator for DB sessions."""
    with Session(engine) as session:
        yield session