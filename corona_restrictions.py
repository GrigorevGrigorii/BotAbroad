import requests
from bs4 import BeautifulSoup


def get_countries_by_region(region):
    """Функция для получения всех доступных стран из переданного региона"""

    return regions[region]


def get_regions():
    """Функция для получения всех доступных регионов"""

    return regions.keys()


def get_article_href(country):
    """Функция для получения ссылки на страницу с информацией о данной стране"""

    for key, value in articles.items():
        if country in value:
            part_of_the_article_name = key
            break
    else:
        raise CountryNotFoundError(country)

    page = 1
    while True:
        r = requests.get(f"https://www.mid.ru/ru/informacia-dla-rossijskih-i-inostrannyh-grazdan-v-svazi-s-koronavirusnoj-infekciej?p_p_id=101_INSTANCE_UUDFpNltySPE&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=1&p_p_col_count=2&_101_INSTANCE_UUDFpNltySPE_delta=20&_101_INSTANCE_UUDFpNltySPE_keywords=&_101_INSTANCE_UUDFpNltySPE_advancedSearch=false&_101_INSTANCE_UUDFpNltySPE_andOperator=true&p_r_p_564233524_resetCur=false&_101_INSTANCE_UUDFpNltySPE_cur={page}")

        if r.status_code != 200:
            raise ArticleNotFoundError(part_of_the_article_name)

        soup = BeautifulSoup(r.content, 'html.parser')
        all_articles = soup.find_all('a', {'class': 'anons-title'})
        for article in all_articles:
            if part_of_the_article_name in article.text:
                return article['href']

        page += 1


def get_info(country, borders: bool = False, requirements: bool = False):
    """Функция для получения информации о стране"""

    article_href = get_article_href(country)
    response = country + '\n\n'

    r = requests.get(article_href)
    soup = BeautifulSoup(r.content, 'html.parser')

    rows_from_article = soup.find_all('tr')[2:-2]
    for row in rows_from_article:
        tds = row.find_all('td')

        if country in tds[1].text:
            if borders and requirements:
                response += tds[2].text.strip('\n')
                response += '\n\n'
                response += tds[3].text.strip('\n')

            elif borders:
                response += tds[2].text.strip('\n')

            elif requirements:
                response += tds[3].text.strip('\n')

            response += '\n\n' + soup.find('u').text
            break

    return response


regions = {
    'Северная и Южная Америка': ('Аргентина', 'Багамские острова', 'Белиз', 'Боливия', 'Бразилия', 'Венесуэла', 'Гайана', 'Гватемала', 'Гондурас', 'Доминиканская Республика', 'Канада', 'Колумбия', 'Коста-Рика', 'Куба', 'Мексика', 'Никарагуа', 'Панама', 'Парагвай', 'Перу', 'Сальвадор', 'США', 'Суринам', 'Уругвай', 'Чили', 'Эквадор'),
    'Европа': ('Австрия', 'Албания', 'Бельгия', 'Болгария', 'Босния и Герцеговина', 'Великобритания', 'Венгрия', 'Германия', 'Греция', 'Дания', 'Ирландия', 'Исландия', 'Испания', 'Италия', 'Кипр', 'Латвия', 'Литва', 'Люксембург', 'Мальта', 'Нидерланды', 'Норвегия', 'Польша', 'Португалия', 'Румыния', 'Сан-Марино', 'Северная Македония', 'Сербия', 'Словакия', 'Словения', 'Турция', 'Финляндия', 'Франция', 'Хорватия', 'Черногория', 'Чехия', 'Швейцария', 'Швеция', 'Эстония'),
    'Азия и Океания': ('Австралия', 'Бангладеш', 'Бруней-Даруссалам', 'Вьетнам', 'Демократическая Республика Восточный Тимор', 'Индия', 'Индонезия', 'Камбоджа', 'Кирибати', 'КНДР', 'КНР', 'Лаос', 'Малайзия', 'Мальдивская Республика', 'Монголия', 'Мьянма', 'Науру', 'Непал', 'Новая Зеландия', 'Пакистан', 'Папуа-Новая Гвинея', 'Республика Вануату', 'Республика Корея', 'Республика Фиджи', 'Самоа', 'Сингапур', 'Таиланд', 'Тонга', 'Тувалу', 'Филиппины', 'Шри-Ланка', 'Япония'),
    'СНГ, Грузия, Абхазия и Южная Осетия': ('Абхазия', 'Азербайджан', 'Армения', 'Белоруссия', 'Грузия', 'Казахстан', 'Киргизия', 'Молдавия', 'Таджикистан', 'Туркменистан', 'Узбекистан', 'Украина', 'Южная Осетия'),
    'Африка, Ближний и Средний Восток': ('Алжир', 'Ангола', 'Афганистан', 'Бахрейн', 'Бенин', 'Ботсвана', 'Буркина Фасо', 'Габон', 'Гана', 'Гвинея', 'Гвинея-Бисау', 'Демократическая Республика Конго', 'Джибути', 'Египет', 'Замбия', 'Зимбабве', 'Израиль', 'Иордания', 'Ирак', 'Иран', 'Кабо-Верде', 'Камерун', 'Катар', 'Кения', 'Конго (Республика Конго)', 'Кот-д’Ивуар', 'Кувейт', 'Лесото', 'Либерия', 'Ливан', 'Маврикий', 'Мавритания', 'Мадагаскар', 'Малави', 'Мали', 'Марокко', 'Мозамбик', 'Намибия', 'Нигер', 'Нигерия', 'ОАЭ', 'Оман', 'Руанда', 'Саудовская Аравия', 'Сейшельские острова', 'Сенегал', 'Сирия', 'Сомали', 'Сьерра-Леоне', 'Судан', 'Танзания', 'Того', 'Тунис', 'Уганда', 'Чад', 'Экваториальная Гвинея', 'Эритрея', 'Эфиопия', 'ЮАР', 'Южный Судан')
}

# здесь хранятся ключевые части названий статей с ограничениями для разных групп стран
articles = {
    'Северной и Южной Америки': regions['Северная и Южная Америка'],
    'Европы': regions['Европа'],
    'Азии и Океании': regions['Азия и Океания'],
    'СНГ, Грузию, Абхазию и Южную Осетию': regions['СНГ, Грузия, Абхазия и Южная Осетия'],
    'Африки, Ближнего и Среднего Востока': regions['Африка, Ближний и Средний Восток']
}


# Exceptions

class CountryNotFoundError(Exception):
    """Исключение. Используется, когда данная страна не найдена в базе."""
    def __init__(self, country_name):
        self.message = f"There is no country {country_name} in our database!"
        super().__init__(self.message)


class ArticleNotFoundError(Exception):
    """Исключение. Используется, когда статья на сайте МИД с данным ключевым фрагментом отсутствует"""
    def __init__(self, article_name):
        self.message = f"There is no article with such key part of the name: {article_name}"
        super().__init__(self.message)
