from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import telegram
import corona_restrictions
import os


bot_token = os.environ.get('TOKEN')
bot = telegram.Bot(token=bot_token)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class State(db.Model):
    """
    Здесь для каждого пользователя хранится спискок соятоний его бота. Возможные состояния:
    region_selection - ожидается ввод региона;
    country_selection - ожидается ввод страны;
    borders_command - происходит обработка команды /borders;
    requirements_command - происходит обработка команды /requirements;
    Состояние может отсутсвовать (бот в покое).
    Возможно также комбинировать некоторые состояния.
    Все состояная хранятся в виде строки. Несколько состояний разделены символом / (слэш).
    Состоянию покоя соответствует пустая строка.
    """
    __tablename__ = "states"
    _id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, unique=True, nullable=False)
    state = db.Column(db.String(40), default='')
    # Максимальная длина состояния (включая возможные комбинации) не превышает 38, поэтому здесь с запасом 40.
    # При добавлении каких-то состояний пересчитать максимальную длину и возможно увеличить допустимую длину.

    def __repr__(self):
        return f"<State: chat_id={self.chat_id}, state={self.state}>"


class User(db.Model):
    """Здесь хранятся все пользователи, которые хоть раз вводили /start (эта команда всегда вводится первой)"""
    __tablename__ = "users"
    _id = db.Column(db.Integer, primary_key=True)
    user_telegram_id = db.Column(db.Integer, unique=True, nullable=False)
    user_first_name = db.Column(db.String(40))
    user_last_name = db.Column(db.String(40))

    def __repr__(self):
        return f"<User: user_first_name={self.user_first_name}, user_last_name={self.user_last_name}>"


@app.route(f'/{bot_token}', methods=['POST'])
def respond():
    """Обработка поступающих от Телеграма запросов"""

    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if not update.message:
        # если произошло действие, но это действие не отправка сообщения
        return 'ok'

    chat_id = update.message.chat.id
    text = update.message.text

    chat_state = State.query.filter_by(chat_id=chat_id).first()
    if not chat_state:
        chat_state = State(chat_id=chat_id, state="")
        db.session.add(chat_state)

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
                if user and not User.query.filter_by(user_telegram_id=user.id).first():
                    db.session.add(
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
                def chunk_string(string, length):
                    """Возвращает string разбитую по части длины не больше length по словам"""
                    if len(string) <= length:
                        return [string]

                    chunked_string = ['']
                    for word in string.split(' '):
                        if len(word) > length:
                            raise AttributeError('Length should be more than the longest word!')

                        if len(chunked_string[-1] + ' ' + word) <= length:
                            chunked_string[-1] += (' ' + word) if chunked_string[-1] != '' else word
                        else:
                            chunked_string.append(word)
                    return chunked_string

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

    db.session.commit()
    return 'ok'


@app.route('/')
def index():
    """Просто для проверки активности сервера"""
    return '.'


if __name__ == '__main__':
    app.run()
