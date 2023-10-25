## this models.py file is used to create the database tables
## user class is used to create the user table
## counter class is used to create the counter table

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from db import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<User %r>' % (self.name)

class CounterGroup(Base):
    __tablename__ = 'counter_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    max_count = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<CounterGroup %r>' % (self.name)

class Counter(Base):
    __tablename__ = 'counter'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    counter_group_id = Column(Integer, ForeignKey('counter_group.id'))
    count = Column(Integer)
    # attempt is used to keep track of the number of attempts to increment the counter
    attempt = Column(Integer)
    # status is used to keep track of whether the counter was successfully incremented or not
    status = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
