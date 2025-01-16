import logging
from typing import Generator

from database.session import SessionLocal
from sqlalchemy.orm import Session


def db_session() -> Generator:
    """Database Session Dependency.

    This function provides a database session for each request.
    It ensures that the session is committed after successful operations.
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as ex:
        session.rollback()
        logging.error(ex)
        raise ex
    finally:
        session.close()
