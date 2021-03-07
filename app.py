from flask import Flask, request
import telegram
from telebot import corona_restrictions
from telebot.state import State
import os


bot_token = os.environ.get('TOKEN')
bot = telegram.Bot(token=bot_token)
state = State()  # здесь для каждого пользователя хранится спискок соятоний его бота
# Возможные состояния:
# choosing_region - ожидается ввод региона
# choosing_страны - ожидается ввод страны
# borders_command - происходит обработка команды /borders
# requirements_command - происходит обработка команды /requirements
# Состояние может отсутсвовать (бот в покое).
# Возможно также комбинировать некоторые состояния.


app = Flask(__name__)


@app.route(f'/{bot_token}', methods=['POST'])
def respond():
    global state

    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id

    text = update.message.text.encode('utf-8').decode()

    if text.startswith('/'):
        # обработка команд

        if text == '/start' or text == '/help':
            # обработка команд /start и /help
            state[chat_id] = []  # сбрасываем состояния

            markup = telegram.ReplyKeyboardRemove()
            bot.sendMessage(chat_id, """
            Для того, чтобы получить ответ бота используйте следующие команды:
            /borders - получить информацию о границе между определенной страной и Россией.
            /requirements - получить информацию о требованиях страны.
            """, reply_markup=markup)

        elif text == '/borders' or text == '/requirements':
            items = []
            for region in corona_restrictions.get_regions():
                items.append([telegram.KeyboardButton(region)])
            markup = telegram.ReplyKeyboardMarkup(items)
            bot.sendMessage(chat_id, "Выберите регион:", reply_markup=markup)

            state[chat_id] = ["choosing_region", f"{text[1:]}_command"]

        else:
            # если ввели недопустимую команду

            state[chat_id] = []  # сбрасываем состояния

            markup = telegram.ReplyKeyboardRemove()
            bot.sendMessage(chat_id, """
            Вы используете какую-то странную команду...
            Для того, чтобы получить ответ бота используйте следующие команды:
            /borders - получить информацию о границе между определенной страной и Россией.
            /requirements - получить информацию о требованиях страны.
            """, reply_markup=markup)

    else:
        # обработка текста

        if "choosing_region" in state[chat_id]:
            # если ожидался ввод региона
            try:
                items = []
                for country in corona_restrictions.get_countries_by_region(text):
                    items.append([telegram.KeyboardButton(country)])
                markup = telegram.ReplyKeyboardMarkup(items)
                bot.sendMessage(chat_id, "Выберите страну:", reply_markup=markup)

                state[chat_id] = ["choosing_country", state[chat_id][1]]
            except KeyError:
                # если сработало данное исключение, то значит введенного региона нет в базе
                bot.sendMessage(chat_id, "Вы ввели какой-то странный регион. Выберите из нашего списка.")

        elif "choosing_country" in state[chat_id]:
            # если ожидался ввод страны
            bot.sendMessage(chat_id, "Минуточку, мы ищем данные...")
            try:
                def chunk_string(string, length):
                    return (string[0 + i:length + i] for i in range(0, len(string), length))

                markup = telegram.ReplyKeyboardRemove()
                if "borders_command" in state[chat_id]:
                    # если пользователь хочет узнать информацию о границах страны
                    for chunk in chunk_string(corona_restrictions.get_info(text, borders=True), 4096):
                        bot.sendMessage(chat_id, chunk, reply_markup=markup)
                elif "requirements_command" in state[chat_id]:
                    # если пользователь хочет узнать информацию о требованиях страны
                    for chunk in chunk_string(corona_restrictions.get_info(text, requirements=True), 4096):
                        bot.sendMessage(chat_id, chunk, reply_markup=markup)

                state[chat_id] = []  # сбрасываем состояния
            except corona_restrictions.CountryNotFoundError:
                # если сработало данное исключение, то значит введенной страны нет в базе
                bot.sendMessage(chat_id, "Похоже, что такой страны нет в нашей базе или вы ввели её неправильно(\nВыберите страну из нашего списка.")

        else:
            # если ввели что-то неожиданное
            bot.sendMessage(chat_id, "Я вас не понимаю. Введите /help, чтобы посмотреть доступные команды.")

    return 'ok'


@app.route('/')
def index():
    return '.'


if __name__ == '__main__':
    app.run()
