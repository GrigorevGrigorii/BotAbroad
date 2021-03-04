import corona_restrictions
import telebot
from state import State


bot = telebot.TeleBot('%token%', parse_mode=None)

state = State()  # здесь для каждого пользователя хранится спискок соятоний его бота
# Возможные состояния:
# choosing_region - ожидается ввод региона
# choosing_страны - ожидается ввод страны
# borders_command - происходит обработка команды /borders
# requirements_command - происходит обработка команды /requirements
# Состояние может отсутсвовать (бот в покое).
# Возможно также комбинировать некоторые состояния.


def chunk_string(string, length):
    """Разделяет переданную строку на части размера length"""
    return (string[0 + i:length + i] for i in range(0, len(string), length))


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработка команд /start и /help"""
    global state
    state[message.from_user.id] = []  # сбрасываем состояния

    markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, """
Для того, чтобы получить ответ бота используйте следующие команды:
/borders - получить информацию о границе между определенной страной и Россией.
/requirements - получить информацию о требованиях страны.
""", reply_markup=markup)


@bot.message_handler(commands=['borders', 'requirements'])
def send_borders_or_requirements(message):
    """Обработка команд /borders и /requirements"""
    global state

    markup = telebot.types.ReplyKeyboardMarkup()
    for region in corona_restrictions.get_regions():
        item = telebot.types.KeyboardButton(region)
        markup.row(item)
    bot.send_message(message.from_user.id, "Выберите регион:", reply_markup=markup)

    state[message.from_user.id] = ["choosing_region", f"{message.text[1:]}_command"]


@bot.message_handler(content_types=['text'])
def send_response(message):
    """Обработка текстового ввода"""
    global state

    if "choosing_region" in state[message.from_user.id]:
        # если ожидался ввод региона
        try:
            markup = telebot.types.ReplyKeyboardMarkup()
            for country in corona_restrictions.get_countries_by_region(message.text):
                item = telebot.types.KeyboardButton(country)
                markup.row(item)
            bot.send_message(message.from_user.id, "Выберите страну:", reply_markup=markup)

            state[message.from_user.id] = ["choosing_country", state[message.from_user.id][1]]
        except KeyError:
            # если сработало данное исключение, то значит введенного региона нет в базе
            bot.send_message(message.from_user.id, "Вы ввели какой-то странный регион. Выберите из нашего списка.")

    elif "choosing_country" in state[message.from_user.id]:
        # если ожидался ввод страны
        bot.send_message(message.from_user.id, "Минуточку, мы ищем данные...")
        try:
            markup = telebot.types.ReplyKeyboardRemove()
            if "borders_command" in state[message.from_user.id]:
                # если пользователь хочет узнать информацию о границах страны
                for chunk in list(chunk_string(corona_restrictions.get_info(message.text, borders=True), 4096)):
                    bot.send_message(message.from_user.id, chunk, reply_markup=markup)
            elif "requirements_command" in state[message.from_user.id]:
                # если пользователь хочет узнать информацию о требованиях страны
                for chunk in list(chunk_string(corona_restrictions.get_info(message.text, requirements=True), 4096)):
                    bot.send_message(message.from_user.id, chunk, reply_markup=markup)

            state[message.from_user.id] = []  # сбрасываем состояния
        except corona_restrictions.CountryNotFoundError:
            # если сработало данное исключение, то значит введенной страны нет в базе
            bot.send_message(message.from_user.id, "Похоже, что такой страны нет в нашей базе или вы ввели её неправильно(\nВыберите страну из нашего списка.")

    else:
        # если ввели что-то неожиданное
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, "Я вас не понимаю. Введите /help, чтобы посмотреть доступные команды.", reply_markup=markup)


bot.polling(none_stop=True, interval=0)
