import logging
from typing import Generator
from contextlib import contextmanager

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


@contextmanager
def db_session_ctx():
    """Database Session Dependency.

    This function provides a database session for each request.
    It ensures that the session is committed after successful operations.
    """
    session: Session = SessionLocal()
    try:
        session.expire_on_commit = False  # TODO: check this is safe
        yield session
        session.commit()
    except Exception as ex:
        session.rollback()
        logging.error(ex)
        raise ex
    finally:
        session.close()
