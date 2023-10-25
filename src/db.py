# this file contains the database connection and base of the database models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as BaseSession
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator

# create the database connection
engine = create_engine('sqlite:///counter.db', echo=False)
# create the session
Session = sessionmaker(bind=engine)
# create the base of the models
Base = declarative_base()

@contextmanager
def session_scope() -> Generator[BaseSession, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
