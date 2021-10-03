from sqlalchemy import Column, Integer, Text
from database.__main__ import Base

from libs.constants.states import StatesEnum
from libs.constants.commands import CommandsEnum


class ChatIDToCommandAndState(Base):
    """
    Сопоставление ID чата -> текущая команда, состояние бота
    """

    __tablename__ = "chat_id_to_command_and_state"

    chat_id = Column(Integer, primary_key=True)
    command = Column(Text, default=CommandsEnum.NOTHING)
    state = Column(Text, default=StatesEnum.NOTHING)

    def __repr__(self):
        return f"<ChatIDToCommandAndState: chat_id={self.chat_id}, command={self.command}, state={self.state}>"
