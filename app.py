from flask import Flask, request

from database.database import db_session
from database.models import State

from BotAbroad_bot import main


app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Удаление сессии в конце запроса или при отключении сервера"""
    db_session.remove()


@app.route(f'/{main.bot_token}', methods=['POST'])
def respond():
    """Обработка поступающих от Телеграма запросов"""

    update = request.get_json(force=True)

    if 'message' not in update:
        # если произошло действие, но это действие не отправка сообщения
        return 'ok'

    chat_id = update['message']['chat']['id']
    text = update['message']['text'] if 'text' in update['message'] else None

    chat_state = State.query.filter(State.chat_id == chat_id).first()
    if not chat_state:
        chat_state = State(chat_id=chat_id, state="")
        db_session.add(chat_state)

    main.message_processing(chat_id, text, chat_state)  # обработка сообщения

    db_session.commit()
    return 'ok'


@app.route('/')
def index():
    """Просто для проверки активности сервера"""
    return '.'


if __name__ == '__main__':
    app.run()
