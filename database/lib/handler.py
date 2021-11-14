import logging
import functools
from datetime import datetime

from sqlalchemy.orm import sessionmaker, scoped_session
from database.__main__ import engine, Base

import database.models.chat_id_to_command_and_state as chat_id_to_command_and_state_model
import database.models.users as users_model
import database.models.corona_infos as corona_infos_model
import database.exceptions.exceptions as database_exceptions
from libs.constants.states import StatesEnum
from libs.constants.commands import CommandsEnum
from libs.constants.corona import CoronaInfoType


logger = logging.getLogger(__name__)


def with_session_commit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        args[0].db_session.commit()
        return result
    return wrapper


class DBHandler:
    def __init__(self):
        logger.info('Init DBHandler')

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

    def get_user(self, chat_id, user_id):
        filter_condition = (users_model.User.chat_id == chat_id and users_model.User.user_id == user_id)
        return users_model.User.query.filter(filter_condition).first()

    @with_session_commit
    def update_user_info(self, chat_id, user_from_message):
        if not user_from_message:
            logger.info('There is no user from chat with id={}'.format(chat_id))
            return

        user = self.get_user(chat_id, user_from_message['id'])
        if user:
            user.is_bot = user_from_message['is_bot']
            user.first_name = user_from_message['first_name']
            user.last_name = user_from_message['last_name']
            user.last_appeal_datetime = datetime.now()
        else:
            user = users_model.User(
                chat_id=chat_id,
                user_id=user_from_message['id'],
                first_name=user_from_message['first_name'],
                last_name=user_from_message['last_name'],
            )
            self.db_session.add(user)

    def get_corona_info(self, region, country):
        filter_condition = (corona_infos_model.CoronaInfos.region == region and corona_infos_model.CoronaInfos.country == country)
        return corona_infos_model.CoronaInfos.query.filter(filter_condition).first()

    @with_session_commit
    def update_corona_info_row(self, region, country, border_info, requirement_info):
        corona_info_row = self.get_corona_info(region, country)
        if corona_info_row:
            corona_info_row.border_info = border_info
            corona_info_row.requirement_info = requirement_info
        else:
            corona_info_row = corona_infos_model.CoronaInfos(
                region=region,
                country=country,
                border_info=border_info,
                requirement_info=requirement_info,
            )
            self.db_session.add(corona_info_row)

    def upload_corona_infos(self, corona_infos):
        for region, corona_infos_for_countries in corona_infos.items():
            for country, corona_infos in corona_infos_for_countries.items():
                self.update_corona_info_row(region, country, corona_infos[CoronaInfoType.BORDERS], corona_infos[CoronaInfoType.REQUIREMENTS])
