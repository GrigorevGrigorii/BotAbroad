import os
from flask import Flask, request

from database.lib.handler import DBHandler
from libs.bot.bot_abroad import get_bot_abroad


app = Flask(__name__)


@app.route(f"/{os.environ.get('TOKEN')}", methods=['POST'])
def respond():
    """Обработка поступающих от Телеграма запросов"""

    update = request.get_json(force=True)

    if 'message' not in update:
        # если произошло действие, но это действие не отправка сообщения
        return 'ok'

    with DBHandler() as db_handler:
        bot = get_bot_abroad(db_handler, update)
        bot.message_processing(update['message'].get('text'))  # обработка сообщения

    return 'ok'


@app.route('/')
def index():
    """Просто для проверки активности сервера"""
    return '.'


if __name__ == '__main__':
    app.run()
