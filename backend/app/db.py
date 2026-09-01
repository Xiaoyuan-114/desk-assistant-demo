from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import data_dir, get_settings


class Base(DeclarativeBase):
    pass


def _url() -> str:
    settings = get_settings()
    if settings.database_url.strip():
        return settings.database_url.strip()
    return f"sqlite:///{(data_dir() / 'demo.sqlite').as_posix()}"


engine = create_engine(
    _url(),
    future=True,
    connect_args={"check_same_thread": False} if _url().startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
