from flask import Flask, request

from database.lib.handler import Handler

from libs.bot.bot_abroad import BotAbroad


app = Flask(__name__)


@app.route(f'/{BotAbroad.token}', methods=['POST'])
def respond():
    """Обработка поступающих от Телеграма запросов"""

    update = request.get_json(force=True)

    if 'message' not in update:
        # если произошло действие, но это действие не отправка сообщения
        return 'ok'

    chat_id = update['message']['chat']['id']
    text = update['message'].get('text')

    with Handler() as handler:
        bot = BotAbroad(handler, chat_id)
        bot.message_processing(text)  # обработка сообщения

    return 'ok'


@app.route('/')
def index():
    """Просто для проверки активности сервера"""
    return '.'


if __name__ == '__main__':
    app.run()
