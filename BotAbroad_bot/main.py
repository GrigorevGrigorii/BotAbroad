import os
import telegram
from BotAbroad_bot import corona_restrictions
from BotAbroad_bot.secondary_functions import chunk_string


bot_token = os.environ.get('TOKEN')
bot = telegram.Bot(token=bot_token)


def process_non_text_message(chat_id, chat_state):
    """Обработка не текстового сообщения"""

    if "region_selection" in chat_state.state:
        # если ожидался ввод региона
        bot.sendMessage(chat_id, """
Бот принимает только текстовые сообщения.
Вы должны ввести регион. Выберите его из списка.""")

    elif "country_selection" in chat_state.state:
        # если ожидался ввод страны
        bot.sendMessage(chat_id, """
Бот принимает только текстовые сообщения.
Вы должны ввести страну. Выберите её из списка.""")

    else:
        markup = telegram.ReplyKeyboardRemove()
        bot.sendMessage(chat_id, "Бот принимает только текстовые сообщения. Введите /help, чтобы посмотреть доступные команды.",
                        reply_markup=markup)


def process_command(chat_id, text, chat_state):
    """Обработка введённой команды"""

    if text == '/start' or text == '/help':
        # обработка команд /start и /help

        chat_state.state = ''  # сбрасываем состояния

        markup = telegram.ReplyKeyboardRemove()
        bot.sendMessage(chat_id, """
Для того, чтобы получить ответ бота используйте следующие команды:
/borders - получить информацию о границе между определенной страной и Россией.
/requirements - получить информацию о требованиях страны.""", reply_markup=markup)

    elif text == '/borders' or text == '/requirements':
        # обработка команд /borders и /requirements

        items = []
        for region in corona_restrictions.get_regions():
            items.append([telegram.KeyboardButton(region)])
        markup = telegram.ReplyKeyboardMarkup(items)
        bot.sendMessage(chat_id, "Выберите регион:", reply_markup=markup)

        chat_state.state = f"region_selection/{text[1:]}_command"

    else:
        # если ввели недопустимую команду

        chat_state.state = ''  # сбрасываем состояния

        markup = telegram.ReplyKeyboardRemove()
        bot.sendMessage(chat_id, """
Вы используете какую-то странную команду...
Для того, чтобы получить ответ бота используйте следующие команды:
/borders - получить информацию о границе между определенной страной и Россией.
/requirements - получить информацию о требованиях страны.""", reply_markup=markup)


def process_text(chat_id, text, chat_state):
    """Обработка введённого текста"""

    if "region_selection" in chat_state.state:
        # если ожидался ввод региона
        try:
            items = []
            for country in corona_restrictions.get_countries_by_region(text):
                items.append([telegram.KeyboardButton(country)])
            markup = telegram.ReplyKeyboardMarkup(items)
            bot.sendMessage(chat_id, "Выберите страну:", reply_markup=markup)

            chat_state.state = chat_state.state.replace('region', 'country')
        except KeyError:
            # если сработало данное исключение, то значит введенного региона нет в базе
            bot.sendMessage(chat_id, "Вы ввели какой-то странный регион. Выберите из списка.")

    elif "country_selection" in chat_state.state:
        # если ожидался ввод страны
        bot.sendMessage(chat_id, "Минуточку, бот ищет данные...")
        try:
            markup = telegram.ReplyKeyboardRemove()
            if "borders_command" in chat_state.state:
                # если пользователь хочет узнать информацию о границах страны
                for chunk in chunk_string(corona_restrictions.get_info(text, borders=True), 4096):
                    bot.sendMessage(chat_id, chunk, reply_markup=markup)
            elif "requirements_command" in chat_state.state:
                # если пользователь хочет узнать информацию о требованиях страны
                for chunk in chunk_string(corona_restrictions.get_info(text, requirements=True), 4096):
                    bot.sendMessage(chat_id, chunk, reply_markup=markup)

            chat_state.state = ''  # сбрасываем состояния
        except corona_restrictions.CountryNotFoundError:
            # если сработало данное исключение, то значит введенной страны нет в базе
            bot.sendMessage(chat_id, """
Похоже, что такой страны нет в базе или вы ввели её неправильно(
Выберите страну из списка.""")

    else:
        # если ввели что-то неожиданное
        markup = telegram.ReplyKeyboardRemove()
        bot.sendMessage(chat_id, "Бот вас не понимает. Введите /help, чтобы посмотреть доступные команды.",
                        reply_markup=markup)


def message_processing(chat_id, text, chat_state):
    """Определение типа сообщения и перенаправление на дальнейшую обработку"""

    if text is None:
        # если ввели не текстовое сообщение
        process_non_text_message(chat_id, chat_state)

    elif text.startswith('/'):
        # обработка команд
        process_command(chat_id, text, chat_state)

    else:
        # обработка текста
        process_text(chat_id, text, chat_state)
