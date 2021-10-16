from datetime import datetime

from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from database.__main__ import Base


class User(Base):
    """
    Пользователи бота
    """

    __tablename__ = "users"

    chat_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    is_bot = Column(Boolean)
    first_name = Column(Text)
    last_name = Column(Text, default=None)
    first_appeal_datetime = Column(DateTime, default=datetime.now())
    last_appeal_datetime = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return "{}: {}".format(self.__name__, ', '.join(['{}={}'.format(key, value) for key, value in self.__dict__ if not key.startswith('__')]))
