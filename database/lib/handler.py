import logging
import functools
from datetime import datetime

from sqlalchemy.orm import sessionmaker, scoped_session
from database.__main__ import engine, Base

import database.models.chats as chats_model
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

    def get_chat(self, chat_id):
        filter_condition = (chats_model.Chat.chat_id == chat_id)
        return chats_model.Chat.query.filter(filter_condition).first()

    def get_command_and_state(self, chat_id):
        chat = self.get_chat(chat_id)
        return chat.command, chat.state

    def create_chat_if_not_exists(self, chat_id):
        chat = self.get_chat(chat_id)
        if not chat:
            self.create_chat(chat_id)

    @with_session_commit
    def create_chat(self, chat_id):
        chat = chats_model.Chat(chat_id=chat_id)
        self.db_session.add(chat)

    def reset_command_and_state(self, char_id):
        self.set_command_and_state(char_id, CommandsEnum.NOTHING, StatesEnum.NOTHING)

    @with_session_commit
    def set_state(self, chat_id, state):
        chat = self.get_chat(chat_id)
        if not chat:
            raise database_exceptions.ItemNotFountError('There is no chat with chat_id={}'.format(chat_id))

        chat.state = state

    @with_session_commit
    def set_command(self, chat_id, command):
        chat = self.get_chat(chat_id)
        if not chat:
            raise database_exceptions.ItemNotFountError('There is no chat with chat_id={}'.format(chat_id))

        chat.command = command

    @with_session_commit
    def set_command_and_state(self, chat_id, command, state):
        chat = self.get_chat(chat_id)
        if not chat:
            raise database_exceptions.ItemNotFountError('There is no chat with chat_id={}'.format(chat_id))

        chat.command = command
        chat.state = state

    def get_all_chats(self):
        return chats_model.Chat.query.all()

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
        model = corona_infos_model.REGION_TO_MODEL['region']
        return model.query.filter(model.country == country).first()

    @with_session_commit
    def compare_and_update_corona_info_row(self, region, country, border_info, requirement_info):
        corona_info_row = self.get_corona_info(region, country)
        if corona_info_row:
            changed = corona_info_row.border_info != border_info or corona_info_row.requirement_info != requirement_info
            corona_info_row.border_info = border_info
            corona_info_row.requirement_info = requirement_info
            return changed
        else:
            model = corona_infos_model.REGION_TO_MODEL['region']
            corona_info_row = model(
                country=country,
                border_info=border_info,
                requirement_info=requirement_info,
            )
            self.db_session.add(corona_info_row)
            return False

    def get_changed_and_upload_corona_infos(self, corona_infos):
        changed_contries = []
        for region, corona_infos_for_countries in corona_infos.items():
            for country, corona_infos in corona_infos_for_countries.items():
                changed = self.compare_and_update_corona_info_row(region, country, corona_infos[CoronaInfoType.BORDERS], corona_infos[CoronaInfoType.REQUIREMENTS])
                if changed:
                    changed_contries.append(country)
        return changed_contries
