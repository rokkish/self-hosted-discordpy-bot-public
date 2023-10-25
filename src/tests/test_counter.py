import pytest
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as BaseSession
from typing import Generator
import datetime

from db import Base
from models import User, CounterGroup, Counter
from counter import *
from user import *


class TestData:
    user_ids: list[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    user_names: list[str] = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    db_url: str = "sqlite:///:memory:"
    counter_group_id: int = 1
    counter_group_name: str = "test_counter_group"
    counter_group_max_count: int = 10


test_data = TestData()


def register_users(mocker: MockerFixture, test_session: BaseSession) -> None:
    mocker.patch("user.session_scope", return_value=test_session)

    for user_id, user_name in zip(test_data.user_ids, test_data.user_names):
        user = test_session.query(User).filter(User.id == user_id).first()
        if user is None:
            register_user(user_id, user_name)
        else:
            raise Exception("user already exists. maybe test_db is not empty?")

    for user_name in test_data.user_names:
        assert is_user_registered(user_name)


def setup_counter_group(mocker: MockerFixture, test_session: BaseSession) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    create_counter_group(
        test_data.counter_group_name, test_data.counter_group_max_count
    )
    assert is_counter_group_name_created(test_data.counter_group_name)


@pytest.fixture(scope="function")
def test_session(mocker: MockerFixture) -> Generator[BaseSession, None, None]:
    engine = create_engine(
        test_data.db_url, echo=True, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    test_session = sessionmaker(bind=engine)
    session = test_session()
    session.query(User).delete()
    session.query(CounterGroup).delete()
    session.query(Counter).delete()
    session.commit()

    register_users(mocker, session)
    setup_counter_group(mocker, session)

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def test_update_counter_group_max_count(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    update_counter_group_max_count(test_data.counter_group_name, 20)
    assert get_counter_group_max_count(test_data.counter_group_name) == 20


# test_length = 1
def test_get_latest_counter(mocker: MockerFixture, test_session: BaseSession) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)

    c = get_latest_counter(test_data.counter_group_id)
    assert c["count"] == 1
    assert c["attempt"] == 1
    assert c["status"]


# test_length = 3
def test_get_latest_counter_3(mocker: MockerFixture, test_session: BaseSession) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    record_counter(test_data.user_ids[1], test_data.counter_group_id, 2, 1, True)
    record_counter(test_data.user_ids[2], test_data.counter_group_id, 3, 1, True)

    c = get_latest_counter(test_data.counter_group_id)
    assert c["count"] == 3
    assert c["attempt"] == 1
    assert c["status"]


# fail case
def test_get_latest_counter_failed(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    record_counter(test_data.user_ids[1], test_data.counter_group_id, 3, 1, False)
    record_counter(test_data.user_ids[2], test_data.counter_group_id, 1, 2, True)

    c = get_latest_counter(test_data.counter_group_id)
    assert c["count"] == 1
    assert c["attempt"] == 2
    assert c["status"]


# unit test for check_increment
def test_check_increment(mocker: MockerFixture, test_session: BaseSession) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)
    is_incremented = check_increment(
        test_data.user_ids[0], test_data.counter_group_id, 1, 1
    )
    assert is_incremented


# unit test for get_latest_attempt
def test_get_latest_attempt(mocker: MockerFixture, test_session: BaseSession) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)
    attempt = get_latest_attempt(test_data.counter_group_id)
    assert attempt == 1


# use wrapper
def test_try_increment_counter(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    ret = try_increment_counter(test_data.user_ids[1], test_data.counter_group_id, 2)
    assert ret["attempt"] == 1
    assert ret["status"]


## long case
def test_try_increment_counter_long(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    _ = try_increment_counter(test_data.user_ids[1], test_data.counter_group_id, 2)
    _ = try_increment_counter(test_data.user_ids[2], test_data.counter_group_id, 3)
    _ = try_increment_counter(test_data.user_ids[3], test_data.counter_group_id, 4)
    _ = try_increment_counter(test_data.user_ids[4], test_data.counter_group_id, 5)
    _ = try_increment_counter(test_data.user_ids[5], test_data.counter_group_id, 6)
    _ = try_increment_counter(test_data.user_ids[6], test_data.counter_group_id, 7)
    _ = try_increment_counter(test_data.user_ids[7], test_data.counter_group_id, 8)
    _ = try_increment_counter(test_data.user_ids[8], test_data.counter_group_id, 9)
    ret = try_increment_counter(test_data.user_ids[9], test_data.counter_group_id, 10)
    assert ret["attempt"] == 1
    assert ret["status"]


## 2 attempt
def test_try_increment_counter_long_twice(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    _ = try_increment_counter(test_data.user_ids[1], test_data.counter_group_id, 2)
    _ = try_increment_counter(
        test_data.user_ids[2], test_data.counter_group_id, 4
    )  # fail
    _ = try_increment_counter(test_data.user_ids[1], test_data.counter_group_id, 1)
    ret = try_increment_counter(test_data.user_ids[2], test_data.counter_group_id, 2)
    assert ret["attempt"] == 2
    assert ret["status"]


## 2 attempt: start fail
def test_try_increment_counter_long_twice_fail(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    _ = try_increment_counter(test_data.user_ids[1], test_data.counter_group_id, 2)
    _ = try_increment_counter(
        test_data.user_ids[2], test_data.counter_group_id, 4
    )  # fail
    ret = try_increment_counter(
        test_data.user_ids[1], test_data.counter_group_id, 2
    )  # fail
    assert ret["attempt"] == 2
    assert ret["status"] == False


## long fail case over limit
def test_try_increment_counter_over(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    assert test_data.counter_group_max_count == 10
    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    _ = try_increment_counter(test_data.user_ids[1], test_data.counter_group_id, 2)
    _ = try_increment_counter(test_data.user_ids[2], test_data.counter_group_id, 3)
    _ = try_increment_counter(test_data.user_ids[3], test_data.counter_group_id, 4)
    _ = try_increment_counter(test_data.user_ids[4], test_data.counter_group_id, 5)
    _ = try_increment_counter(test_data.user_ids[5], test_data.counter_group_id, 6)
    _ = try_increment_counter(test_data.user_ids[6], test_data.counter_group_id, 7)
    _ = try_increment_counter(test_data.user_ids[7], test_data.counter_group_id, 8)
    _ = try_increment_counter(test_data.user_ids[8], test_data.counter_group_id, 9)
    _ = try_increment_counter(test_data.user_ids[9], test_data.counter_group_id, 10)
    ret = try_increment_counter(test_data.user_ids[0], test_data.counter_group_id, 11)
    assert ret["attempt"] == 1
    assert ret["status"] == False


## bug case (id start from 1 not 0)
def test_try_increment_counter_bug(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], 0, 1, 1, True)
    with pytest.raises(Exception):
        _ = try_increment_counter(test_data.user_ids[1], 0, 3)


## fail case: skip
def test_try_increment_counter_fail_skip_count(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    ret = try_increment_counter(test_data.user_ids[1], test_data.counter_group_id, 3)
    assert ret["attempt"] == 1
    assert ret["status"] == False


## fail case: duplicate user
def test_try_increment_counter_fail_duplicate_user(
    mocker: MockerFixture, test_session: BaseSession
) -> None:
    mocker.patch("counter.session_scope", return_value=test_session)

    record_counter(test_data.user_ids[0], test_data.counter_group_id, 1, 1, True)
    ret = try_increment_counter(test_data.user_ids[0], test_data.counter_group_id, 2)
    assert ret["attempt"] == 1
    assert ret["status"] == False
