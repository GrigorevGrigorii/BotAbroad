import os
import telegram
import logging

from libs.corona import corona_restrictions
from libs.corona import exceptions as corona_exceptions
from libs.secondary_functions.string import chunk_string
from libs.constants import (
    states as states_constants,
    commands as commands_constants,
    telegram as telegram_constants,
    subscription as subscription_constants,
)
from database.models.chats import COMMAND_TO_CORONA_INFO_TYPE


logger = logging.getLogger(__name__)


class BotAbroad:
    bot_client = telegram.Bot(token=os.environ.get('TOKEN'))

    def __init__(self, db_handler, chat_id, user=None):
        logger.info('Init BotAbroad')

        self.db_handler = db_handler

        db_handler.create_chat_if_not_exists(chat_id)
        self.chat = db_handler.get_chat(chat_id)

        db_handler.update_user_info(chat_id, user)

    def message_processing(self, text):
        """Определение типа сообщения и перенаправление на дальнейшую обработку"""

        logger.info("Process message '{}' for chat_id={}".format(text, self.chat.chat_id))

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

    def send_info_about_subscriptions(self, contries):
        """Отправка стран из подписок, по которым изменились требования"""

        self._send_message('\n'.join(('Привет!',
                                      'Изменилась информация по следующим странам:',
                                      ', '.join(contries))))

    def _send_message(self, message_text, reply_markup=None):
        self.__class__.bot_client.send_message(self.chat.chat_id, message_text, reply_markup=reply_markup)

    def _send_typing_action(self):
        self.__class__.bot_client.send_chat_action(self.chat.chat_id, telegram.ChatAction.TYPING)

    def _get_chat(self):
        return self.db_handler.get_chat(self.chat.chat_id)

    def _send_regions(self):
        items = []
        for region in corona_restrictions.get_regions():
            items.append([telegram.KeyboardButton(region)])
        markup = telegram.ReplyKeyboardMarkup(items)
        self._send_message('Выберите регион:', reply_markup=markup)

    def _process_non_text_message(self):
        """Обработка не текстового сообщения"""

        chat = self._get_chat()
        if chat.state == states_constants.StatesEnum.REGION_SELECTION:
            # если ожидался ввод региона
            self._send_message('\n'.join(('Бот принимает только текстовые сообщения.',
                                          'Вы должны ввести регион. Выберите его из списка.')))

        elif chat.state == states_constants.StatesEnum.COUNTRY_SELECTION:
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

        self.db_handler.reset_chat_settings(self.chat)
        if command in (commands_constants.CommandsEnum.START, commands_constants.CommandsEnum.HELP):
            # обработка команд commands_constants.CommandsEnum.START и commands_constants.CommandsEnum.HELP
            markup = telegram.ReplyKeyboardRemove()
            self._send_message('\n'.join(('Для того, чтобы получить ответ бота используйте следующие команды:',
                                          '/borders - получить информацию о границе между определенной страной и Россией.',
                                          '/requirements - получить информацию о требованиях страны.')),
                               reply_markup=markup)

        elif command in (commands_constants.CommandsEnum.BORDERS, commands_constants.CommandsEnum.REQUIREMENTS):
            # обработка команд commands_constants.CommandsEnum.BORDERS и commands_constants.CommandsEnum.REQUIREMENTS
            self._send_regions()
            self.db_handler.set_command_and_state(self.chat, command, states_constants.StatesEnum.REGION_SELECTION)

        elif command == commands_constants.CommandsEnum.SUBSCRIPTIONS:
            markup = telegram.ReplyKeyboardMarkup([[action] for action in subscription_constants.ACTION_TO_DISPLAY_NAME.values()])
            self._send_message('Выберите подходящее действие:', reply_markup=markup)
            self.db_handler.set_command(self.chat, commands_constants.CommandsEnum.SUBSCRIPTIONS)

        else:
            # если ввели недопустимую команду
            markup = telegram.ReplyKeyboardRemove()
            self._send_message('\n'.join(('Вы используете какую-то странную команду...',
                                          'Для того, чтобы получить ответ бота используйте следующие команды:',
                                          f'{commands_constants.CommandsEnum.BORDERS} - получить информацию о границе между определенной страной и Россией.',
                                          f'{commands_constants.CommandsEnum.REQUIREMENTS} - получить информацию о требованиях страны.',
                                          f'{commands_constants.CommandsEnum.SUBSCRIPTIONS} - управление подписками.')),
                               reply_markup=markup)

    def _process_text(self, text):
        """Обработка введённого текста"""

        chat = self._get_chat()
        if chat.command == commands_constants.CommandsEnum.SUBSCRIPTIONS and not chat.state:
            if text in subscription_constants.ACTION_TO_DISPLAY_NAME.values():
                if text == subscription_constants.ACTION_TO_DISPLAY_NAME[subscription_constants.ActionsEnum.SHOW]:
                    if chat.subscriptions:
                        self._send_message('\n'.join(('Ваши подписки:',
                                                      '\n'.join(chat.subscriptions))), reply_markup=telegram.ReplyKeyboardRemove())
                    else:
                        self._send_message('Вы пока не подписаны ни на одну страну(', reply_markup=telegram.ReplyKeyboardRemove())
                    self.db_handler.reset_chat_settings(self.chat)
                else:
                    self._send_regions()
                    self.db_handler.set_subcommand(self.chat, subscription_constants.DISPLAY_NAME_TO_ACTION[text])
                    self.db_handler.set_state(self.chat, states_constants.StatesEnum.REGION_SELECTION)

            else:
                self._send_message('\n'.join(('Вы ввели какое-то странное действие...',
                                              'Выберите подходящее из списка:')))

        elif chat.state == states_constants.StatesEnum.REGION_SELECTION:
            # если ожидался ввод региона
            try:
                items = []
                for country in corona_restrictions.get_countries_by_region(text):
                    items.append([telegram.KeyboardButton(country)])
                markup = telegram.ReplyKeyboardMarkup(items)
                self._send_message('Выберите страну:', reply_markup=markup)
                self.db_handler.set_state(self.chat, states_constants.StatesEnum.COUNTRY_SELECTION)
            except corona_exceptions.RegionNotFoundError:
                # если сработало данное исключение, то значит введенного региона нет в базе
                self._send_message('Вы ввели какой-то странный регион. Выберите из списка.')

        elif chat.state == states_constants.StatesEnum.COUNTRY_SELECTION:
            # если ожидался ввод страны
            if chat.command == commands_constants.CommandsEnum.SUBSCRIPTIONS:
                if chat.subcommand == commands_constants.SubcommandsEnum.ADD:
                    try:
                        self.db_handler.add_subscription(chat, text)
                        self._send_message('В ваши подписки была добавлена страна {}'.format(text), reply_markup=telegram.ReplyKeyboardRemove())
                    except corona_exceptions.CountryNotFoundError:
                        # если сработало данное исключение, то значит введенной страны нет в базе
                        self._send_message('\n'.join(('Похоже, что такой страны нет в базе или вы ввели её неправильно(',
                                                      'Выберите страну из списка.')))
                elif chat.subcommand == commands_constants.SubcommandsEnum.REMOVE:
                    self.db_handler.remove_subscription(chat, text)
                    self._send_message('Из ваших подписок была удалена страна {}'.format(text), reply_markup=telegram.ReplyKeyboardRemove())
                else:
                    self._send_message('Something went wrong. Command {} wo subcommand on last step'.format(commands_constants.CommandsEnum.SUBSCRIPTIONS))
                self.db_handler.reset_chat_settings(self.chat)

            else:
                self._send_message('Минуточку, бот ищет данные...', reply_markup=telegram.ReplyKeyboardRemove())
                self._send_typing_action()
                try:
                    corona_info_type = COMMAND_TO_CORONA_INFO_TYPE[chat.command]
                    for chunk in chunk_string(corona_restrictions.get_full_info(text, info_type=corona_info_type), telegram_constants.MAX_MESSAGE_LENGTH):
                        self._send_message(chunk)
                    self.db_handler.reset_chat_settings(self.chat)
                except corona_exceptions.CountryNotFoundError:
                    # если сработало данное исключение, то значит введенной страны нет в базе
                    self._send_message('\n'.join(('Похоже, что такой страны нет в базе или вы ввели её неправильно(',
                                                  'Выберите страну из списка.')))

        else:
            # если ввели что-то неожиданное
            markup = telegram.ReplyKeyboardRemove()
            self._send_message('Бот вас не понимает. Введите /help, чтобы посмотреть доступные команды.',
                               reply_markup=markup)

            self.db_handler.reset_chat_settings(self.chat)


def get_bot_abroad(handler, telegram_update):
    chat_id = telegram_update['message']['chat']['id']
    user = telegram_update['message'].get('from')

    return BotAbroad(handler, chat_id, user)
