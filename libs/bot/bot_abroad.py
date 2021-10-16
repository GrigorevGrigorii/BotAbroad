import os
import telegram
import logging
from telegram.utils.helpers import DEFAULT_NONE

from libs.corona import corona_restrictions
from libs.corona import exceptions as corona_exceptions
from libs.secondary_functions.string import chunk_string
from libs.constants import (
    states as states_constants,
    commands as commands_constants,
    telegram as telegram_constants,
)
from database.models.chat_id_to_command_and_state import COMMAND_TO_CORONA_INFO_TYPE


logger = logging.getLogger(__name__)


class BotAbroad:
    bot_client = telegram.Bot(token=os.environ.get('TOKEN'))

    def __init__(self, db_handler, chat_id, user=None):
        logger.info('Init BotAbroad')

        self.db_handler = db_handler
        self.chat_id = chat_id

        self.db_handler.create_chat_id_to_command_and_state_if_not_exists(self.chat_id)
        self.db_handler.update_user_info(chat_id, user)

    def message_processing(self, text):
        """Определение типа сообщения и перенаправление на дальнейшую обработку"""

        logger.info("Process message '{}' for chat_id={}".format(text, self.chat_id))

        self._send_typing_action()
        if text is None:
            # если ввели не текстовое сообщение
            self._process_non_text_message()

        elif text.startswith('/'):
            # обработка команд
            self._process_command(text)

        else:
            # обработка текста
            self._process_text(text)

    def _send_message(self, message_text, reply_markup=None, parse_mode=DEFAULT_NONE):
        self.__class__.bot_client.send_message(self.chat_id, message_text, reply_markup=reply_markup, parse_mode=parse_mode)

    def _send_typing_action(self):
        self.__class__.bot_client.send_chat_action(self.chat_id, telegram.ChatAction.TYPING)

    def _get_command_and_state(self):
        return self.db_handler.get_command_and_state(self.chat_id)

    def _process_non_text_message(self):
        """Обработка не текстового сообщения"""

        _, state = self._get_command_and_state()
        if state == states_constants.StatesEnum.REGION_SELECTION:
            # если ожидался ввод региона
            self._send_message('\n'.join(('Бот принимает только текстовые сообщения.',
                                          'Вы должны ввести регион. Выберите его из списка.')))

        elif state == states_constants.StatesEnum.COUNTRY_SELECTION:
            # если ожидался ввод страны
            self._send_message('\n'.join(('Бот принимает только текстовые сообщения.',
                                          'Вы должны ввести страну. Выберите её из списка.')))

        else:
            markup = telegram.ReplyKeyboardRemove()
            self._send_message('Бот принимает только текстовые сообщения. Введите /help, чтобы посмотреть доступные команды.',
                               reply_markup=markup)

    def _process_command(self, command):
        """Обработка введённой команды"""
        assert command.startswith('/')

        if command in (commands_constants.CommandsEnum.START, commands_constants.CommandsEnum.HELP):
            # обработка команд commands_constants.CommandsEnum.START и commands_constants.CommandsEnum.HELP
            markup = telegram.ReplyKeyboardRemove()
            self._send_message('\n'.join(('Для того, чтобы получить ответ бота используйте следующие команды:',
                                          '/borders - получить информацию о границе между определенной страной и Россией.',
                                          '/requirements - получить информацию о требованиях страны.')),
                               reply_markup=markup)

            self.db_handler.reset_command_and_state(self.chat_id)

        elif command in (commands_constants.CommandsEnum.BORDERS, commands_constants.CommandsEnum.REQUIREMENTS):
            # обработка команд commands_constants.CommandsEnum.BORDERS и commands_constants.CommandsEnum.REQUIREMENTS
            items = []
            for region in corona_restrictions.get_regions():
                items.append([telegram.KeyboardButton(region)])
            markup = telegram.ReplyKeyboardMarkup(items)
            self._send_message('Выберите регион:', reply_markup=markup)

            self.db_handler.set_command_and_state(self.chat_id, command, states_constants.StatesEnum.REGION_SELECTION)

        else:
            # если ввели недопустимую команду
            markup = telegram.ReplyKeyboardRemove()
            self._send_message('\n'.join(('Вы используете какую-то странную команду...',
                                          'Для того, чтобы получить ответ бота используйте следующие команды:',
                                          f'{commands_constants.CommandsEnum.BORDERS} - получить информацию о границе между определенной страной и Россией.',
                                          f'{commands_constants.CommandsEnum.REQUIREMENTS} - получить информацию о требованиях страны.')),
                               reply_markup=markup)

            self.db_handler.reset_command_and_state(self.chat_id)

    def _process_text(self, text):
        """Обработка введённого текста"""

        command, state = self._get_command_and_state()
        if state == states_constants.StatesEnum.REGION_SELECTION:
            # если ожидался ввод региона
            try:
                items = []
                for country in corona_restrictions.get_countries_by_region(text):
                    items.append([telegram.KeyboardButton(country)])
                markup = telegram.ReplyKeyboardMarkup(items)
                self._send_message('Выберите страну:', reply_markup=markup)

                self.db_handler.set_state(self.chat_id, states_constants.StatesEnum.COUNTRY_SELECTION)
            except corona_exceptions.RegionNotFoundError:
                # если сработало данное исключение, то значит введенного региона нет в базе
                self._send_message('Вы ввели какой-то странный регион. Выберите из списка.')

        elif state == states_constants.StatesEnum.COUNTRY_SELECTION:
            # если ожидался ввод страны
            self._send_message('Минуточку, бот ищет данные...')
            self._send_typing_action()
            try:
                markup = telegram.ReplyKeyboardRemove()
                corona_info_type = COMMAND_TO_CORONA_INFO_TYPE[command]
                for chunk in chunk_string(corona_restrictions.get_full_info(text, info_type=corona_info_type), telegram_constants.MAX_MESSAGE_LENGTH):
                    self._send_message(chunk, reply_markup=markup, parse_mode=telegram.ParseMode.HTML)
                    markup = None
                self.db_handler.reset_command_and_state(self.chat_id)
            except corona_exceptions.CountryNotFoundError:
                # если сработало данное исключение, то значит введенной страны нет в базе
                self._send_message('\n'.join(('Похоже, что такой страны нет в базе или вы ввели её неправильно(',
                                              'Выберите страну из списка.')))

        else:
            # если ввели что-то неожиданное
            markup = telegram.ReplyKeyboardRemove()
            self._send_message('Бот вас не понимает. Введите /help, чтобы посмотреть доступные команды.',
                               reply_markup=markup)

            self.db_handler.reset_command_and_state(self.chat_id)


def get_bot_abroad(handler, update):
    chat_id = update['message']['chat']['id']
    user = update['message'].get('from')

    return BotAbroad(handler, chat_id, user)
