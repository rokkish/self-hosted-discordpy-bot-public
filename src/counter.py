import datetime
import logging
from typing import Any, Dict, Union

from db import session_scope
from models import Counter, CounterGroup

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_counter_group(name: str, max_count: int) -> None:
    """Create a new counter group."""
    with session_scope() as session:
        now = datetime.datetime.now()
        counter_group = CounterGroup(
            name=name,
            max_count=max_count,
            created_at=now,
            updated_at=now,
        )
        session.add(counter_group)
        session.commit()
        logger.info(f"Added counter group {counter_group}")


def is_counter_group_name_created(name: str) -> bool:
    with session_scope() as session:
        counter_group = (
            session.query(CounterGroup).filter(CounterGroup.name == name).first()
        )
        return counter_group is not None


def get_counter_group_id(name: str) -> int:
    with session_scope() as session:
        counter_group = (
            session.query(CounterGroup).filter(CounterGroup.name == name).first()
        )
        return counter_group.id


def get_counter_group_max_count(name: str) -> int:
    with session_scope() as session:
        counter_group = (
            session.query(CounterGroup).filter(CounterGroup.name == name).first()
        )
        return counter_group.max_count


def update_counter_group_max_count(name: str, max_count: int) -> None:
    with session_scope() as session:
        counter_group = (
            session.query(CounterGroup).filter(CounterGroup.name == name).first()
        )
        before = counter_group.max_count
        counter_group.max_count = max_count
        session.add(counter_group)
        session.commit()
        logger.info(
            f"Updated counter group {counter_group} from {before} to {max_count}"
        )


def get_latest_counter(counter_group_id: int) -> Union[None, Dict[str, Any]]:
    with session_scope() as session:
        counters = (
            session.query(Counter)
            .filter(Counter.counter_group_id == counter_group_id)
            .all()
        )
        if len(counters) == 0:
            return None

        latest_counter = counters[-1]
        return {
            "count": latest_counter.count,
            "attempt": latest_counter.attempt,
            "status": latest_counter.status,
        }


def record_counter(
    user_id: int, counter_group_id: int, count: int, attempt: int, status: bool
) -> None:
    """Increment the counter for a user."""
    with session_scope() as session:
        now = datetime.datetime.now()
        counter = Counter(
            user_id=user_id,
            counter_group_id=counter_group_id,
            count=count,
            attempt=attempt,
            status=status,
            created_at=now,
            updated_at=now,
        )
        session.add(counter)
        session.commit()
        logger.info(f"Added counter {counter}")


def check_increment(
    user_id: int, counter_group_id: int, count: int, attempt: int
) -> bool:
    """Check if the counter should be incremented."""
    with session_scope() as session:
        counters = (
            session.query(Counter)
            .filter(
                Counter.counter_group_id == counter_group_id, Counter.attempt == attempt
            )
            .all()
        )
        if len(counters) == 0:
            return count == 1
        else:
            # get unique user_id list from Counter, and check if the user is already in the list
            unique_user_ids = list(set([c.user_id for c in counters]))
            if user_id in unique_user_ids:
                return False

            counter_group = (
                session.query(CounterGroup)
                .filter(CounterGroup.id == counter_group_id)
                .first()
            )
            if counter_group is None:
                raise Exception(f"Counter group {counter_group_id} not found")
            max_count = get_counter_group_max_count(counter_group.name)

            latest_counter = counters[-1]
            return latest_counter.count + 1 == count and count <= max_count


def get_latest_attempt(counter_group_id: int) -> int:
    c = get_latest_counter(counter_group_id)
    if c is None:
        return 1
    else:
        with session_scope() as session:
            counter_group = (
                session.query(CounterGroup)
                .filter(CounterGroup.id == counter_group_id)
                .first()
            )
            if counter_group is None:
                raise Exception(f"Counter group {counter_group_id} not found")
            max_count = get_counter_group_max_count(counter_group.name)

        # prev count is unsuccessful
        if c["status"] == False:
            return c["attempt"] + 1
        # prev attempt is successful
        elif c["status"] and c["count"] == max_count:
            return c["attempt"] + 1
        # prev attempt is successful but not max count
        return c["attempt"]


def try_increment_counter(
    user_id: int, counter_group_id: int, count: int
) -> Dict[str, Any]:
    """Increment the counter for a user."""
    attempt = get_latest_attempt(counter_group_id)
    status = check_increment(user_id, counter_group_id, count, attempt)
    try:
        record_counter(user_id, counter_group_id, count, attempt, status)
    except Exception as e:
        logger.error(e)
    finally:
        return {
            "status": status,
            "attempt": attempt,
        }
