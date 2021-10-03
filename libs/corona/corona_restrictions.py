import requests
from bs4 import BeautifulSoup
import logging

from libs.corona import exceptions as corona_exceptions
from libs.constants import corona as corona_constants


logger = logging.getLogger(__name__)


def get_countries_by_region(region):
    """Функция для получения всех доступных стран из переданного региона"""

    countries = corona_constants.REGIONS.get(region)
    if not countries:
        raise corona_exceptions.RegionNotFoundError(region)
    return corona_constants.REGIONS[region]


def get_regions():
    """Функция для получения всех доступных регионов"""

    return corona_constants.REGIONS.keys()


def _get_article_href(country):
    """Функция для получения ссылки на страницу с информацией о данной стране"""

    for key, value in corona_constants.ARTICLES.items():
        if country in value:
            part_of_the_article_name = key
            break
    else:
        raise corona_exceptions.CountryNotFoundError(country)

    page = 1
    while True:
        r = requests.get(corona_constants.MID_PAGE_URL_TEMPLATE.format(page=page))

        if r.status_code != 200:
            # пересмотрели все страницы
            raise corona_exceptions.ArticleNotFoundError(part_of_the_article_name)

        soup = BeautifulSoup(r.content, 'html.parser')
        all_articles = soup.find_all('a', {'class': 'anons-title'})
        for article in all_articles:
            if part_of_the_article_name in article.text:
                return article['href']

        page += 1


def _get_info_and_date(country, info_type):
    if info_type not in corona_constants.CoronaInfoType.values():
        raise corona_exceptions.UnknownCoronaInfoType(info_type)

    article_href = _get_article_href(country)

    r = requests.get(article_href)
    soup = BeautifulSoup(r.content, 'html.parser')

    rows_from_article = soup.find_all('tr')[2:-2]
    for row in rows_from_article:
        tds = row.find_all('td')

        if country in tds[1].text:
            if info_type == corona_constants.CoronaInfoType.BORDERS:
                info = tds[2].text.strip('\n')
            elif info_type == corona_constants.CoronaInfoType.REQUIREMENTS:
                info = tds[3].text.strip('\n')
            else:
                raise corona_exceptions.UnknownCoronaInfoType(info_type)

            date_of_relevance = soup.find('p', {'style': 'text-align: right;'}).text
            break
    else:
        raise corona_exceptions.CountryInfoNotFoundError

    return info, date_of_relevance


def get_full_info(country, info_type):
    """Функция для получения информации о стране"""
    if info_type not in corona_constants.CoronaInfoType.values():
        raise corona_exceptions.UnknownCoronaInfoType(info_type)

    logger.info('Getting {} info about {}'.format(info_type, country))
    info, date = _get_info_and_date(country, info_type)

    return '\n\n'.join((country, info, date))
