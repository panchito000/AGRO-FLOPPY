"""Conexión a PostgreSQL."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa para modelos SQLAlchemy."""


def get_db():
    """Dependencia FastAPI: sesión de base de datos por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
