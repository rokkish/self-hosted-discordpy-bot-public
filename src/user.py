import logging
import datetime

from models import User
from db import session_scope

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def register_user(id: int, name: str) -> None:
    """Register a new user."""
    with session_scope() as session:
        now = datetime.datetime.now()
        user = User(
            id=id,
            name=name,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        session.commit()
        logger.info(f"Added user {user}")


def is_user_registered(name: str) -> bool:
    with session_scope() as session:
        user = session.query(User).filter(User.name == name).first()
        return user is not None
