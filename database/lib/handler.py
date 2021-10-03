import logging
import functools

from sqlalchemy.orm import sessionmaker, scoped_session
from database.__main__ import engine, Base

import database.models.chat_id_to_command_and_state as chat_id_to_command_and_state_model
import database.exceptions.exceptions as database_exceptions
from libs.constants.states import StatesEnum
from libs.constants.commands import CommandsEnum


logger = logging.getLogger(__name__)


def with_session_commit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        args[0].db_session.commit()
        return result
    return wrapper


class Handler:
    def __init__(self):
        logger.info('Init Handler')

        self.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        Base.query = self.db_session.query_property()

    def __enter__(self):
        self.__init__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_session.remove()

    def remove_session(self):
        self.db_session.remove()

    def get_chat_id_to_command_and_state_row(self, chat_id):
        filter_condition = (chat_id_to_command_and_state_model.ChatIDToCommandAndState.chat_id == chat_id)
        return chat_id_to_command_and_state_model.ChatIDToCommandAndState.query.filter(filter_condition).first()

    def get_command_and_state(self, chat_id):
        command_and_state_row = self.get_chat_id_to_command_and_state_row(chat_id)
        return command_and_state_row.command, command_and_state_row.state

    def create_chat_id_to_command_and_state_if_not_exists(self, chat_id):
        command_and_state_row = self.get_chat_id_to_command_and_state_row(chat_id)
        if not command_and_state_row:
            self.create_chat_id_to_command_and_state(chat_id)

    @with_session_commit
    def create_chat_id_to_command_and_state(self, chat_id):
        chat_id_to_state = chat_id_to_command_and_state_model.ChatIDToCommandAndState(chat_id=chat_id)
        self.db_session.add(chat_id_to_state)

    def reset_command_and_state(self, char_id):
        self.set_command_and_state(char_id, CommandsEnum.NOTHING, StatesEnum.NOTHING)

    @with_session_commit
    def set_state(self, chat_id, state):
        command_and_state_row = self.get_chat_id_to_command_and_state_row(chat_id)
        if not command_and_state_row:
            raise database_exceptions.ItemNotFountError('There is no command_and_state_row with chat_id={}'.format(chat_id))

        command_and_state_row.state = state

    @with_session_commit
    def set_command_and_state(self, chat_id, command, state):
        command_and_state_row = self.get_chat_id_to_command_and_state_row(chat_id)
        if not command_and_state_row:
            raise database_exceptions.ItemNotFountError('There is no command_and_state_row with chat_id={}'.format(chat_id))

        command_and_state_row.command = command
        command_and_state_row.state = state
