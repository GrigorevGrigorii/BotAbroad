import requests
from bs4 import BeautifulSoup
import json


def get_countries_by_region(region):
    with open('files/regions.json', 'r') as regions_file:
        regions = json.load(regions_file)
        return regions[region]


def get_regions():
    with open('files/regions.json', 'r') as regions_file:
        regions = json.load(regions_file)
        return regions.keys()


def check_and_normalize(country):
    """Функция для проверки наличия страны в базе. В случае наличия возвращает название страны как на сайте МИД"""

    with open('files/countries.json', 'r') as countries_file:
        countries = json.load(countries_file)
        for key, value in countries.items():
            if country.lower() in value:
                country = key
                break
        else:
            raise CountryNotFoundError(country)

    return country


def get_topic_href(country):
    """Функция для получения ссылки на страницу с информацией о данной стране"""

    with open('files/topics.json', 'r') as topics_file:
        topics = json.load(topics_file)
        for key, value in topics.items():
            if country in value:
                topic_name = key
                break
        else:
            raise CountryNotFoundError(country)
        del topics

    r = requests\
        .get('https://www.mid.ru/ru/informacia-dla-rossijskih-i-inostrannyh-grazdan-v-svazi-s-koronavirusnoj-infekciej')
    soup = BeautifulSoup(r.content, 'html.parser')
    all_topics = soup.find_all('a', {'class': 'anons-title'})

    for topic in all_topics:
        if topic.text == topic_name:
            href = topic['href']
            break
    else:
        raise TopicNotFoundError(topic_name)

    return href


def get_info(country, borders: bool = False, requirements: bool = False):
    """Функция для получения информации о стране"""

    country = check_and_normalize(country)
    response = country + '\n\n'
    topic_href = get_topic_href(country)

    r = requests.get(topic_href)
    soup = BeautifulSoup(r.content, 'html.parser')

    rows_from_topic = soup.find_all('tr')[2:-2]
    for row in rows_from_topic:
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


# Exceptions

class CountryNotFoundError(Exception):
    """Исключение. Используется, когда данная страна не найдена в базе."""
    def __init__(self, country_name):
        self.message = f"There is no country {country_name} in our database!"
        super().__init__(self.message)


class TopicNotFoundError(Exception):
    """Исключение. Используется, когда статья на сайте МИД с данным именем отсутствует"""
    def __init__(self, topic_name):
        self.message = f"There is no topic with such name: {topic_name}"
        super().__init__(self.message)
