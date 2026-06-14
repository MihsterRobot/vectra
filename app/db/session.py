from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

from app.core.config import settings


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    '''Yields a database session and ensures it is closed after use.

    Yields:
        A SQLAlchemy database session.
    '''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
