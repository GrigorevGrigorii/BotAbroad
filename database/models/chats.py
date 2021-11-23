from sqlalchemy import Column, Integer, Text
from database.__main__ import Base

from libs.constants.states import StatesEnum
from libs.constants.commands import CommandsEnum
from libs.constants.corona import CoronaInfoType


COMMAND_TO_CORONA_INFO_TYPE = {
    CommandsEnum.BORDERS: CoronaInfoType.BORDERS,
    CommandsEnum.REQUIREMENTS: CoronaInfoType.REQUIREMENTS,
}


class Chat(Base):
    """
    Чаты (бот привзяан к чату, а не к юзеру, так как бот может быть добавлен к групповой чат)
    """

    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True)
    command = Column(Text, default=CommandsEnum.NOTHING)
    state = Column(Text, default=StatesEnum.NOTHING)
    subsciptions = Column(, default=[])  # TODO: make list

    def __repr__(self):
        return f"<Chat: chat_id={self.chat_id}, command={self.command}, state={self.state}>"
