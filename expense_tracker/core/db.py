from sqlmodel import SQLModel, create_engine, Session

BASE_DIR = Path(__file__).resolve().parent  # -> expense_tracker/
DB_PATH = BASE_DIR / "dev.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency generator for DB sessions."""
    with Session(engine) as session:
        yield session