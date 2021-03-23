from flask import Flask, request
from database import db_session
from models import State, User

import telegram
import os

import corona_restrictions
from secondary_functions import chunk_string


bot_token = os.environ.get('TOKEN')
bot = telegram.Bot(token=bot_token)

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Удаление сессии в конце запроса или при отключении сервера"""
    db_session.remove()


@app.route(f'/{bot_token}', methods=['POST'])
def respond():
    """Обработка поступающих от Телеграма запросов"""

    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if not update.message:
        # если произошло действие, но это действие не отправка сообщения
        return 'ok'

    chat_id = update.message.chat.id
    text = update.message.text

    chat_state = State.query.filter(State.chat_id == chat_id).first()
    if not chat_state:
        chat_state = State(chat_id=chat_id, state="")
        db_session.add(chat_state)

    if text is None:
        # если ввели не текстовое сообщение

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

    elif text.startswith('/'):
        # обработка команд

        if text == '/start' or text == '/help':
            # обработка команд /start и /help

            if text == '/start':
                # заносим пользователя в таблицу если его там нет
                user = update.message.from_user
                if user and not User.query.filter(User.user_telegram_id == user.id).first():
                    db_session.add(
                        User(user_telegram_id=user.id, user_first_name=user.first_name, user_last_name=user.last_name))

            chat_state.state = ''  # сбрасываем состояния

            markup = telegram.ReplyKeyboardRemove()
            bot.sendMessage(chat_id, """
Для того, чтобы получить ответ бота используйте следующие команды:
/borders - получить информацию о границе между определенной страной и Россией.
/requirements - получить информацию о требованиях страны.""", reply_markup=markup)

        elif text == '/borders' or text == '/requirements':
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

    else:
        # обработка текста

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

    db_session.commit()
    return 'ok'


@app.route('/')
def index():
    """Просто для проверки активности сервера"""
    return '.'


if __name__ == '__main__':
    app.run()
