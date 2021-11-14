import requests
from bs4 import BeautifulSoup
import logging

from libs.corona import exceptions as corona_exceptions
from libs.constants import corona as corona_constants


logger = logging.getLogger(__name__)


def get_countries_by_region(region):
    """Функция для получения всех доступных стран из переданного региона"""

    countries = corona_constants.REGION_TO_COUNTRIES.get(region)
    if not countries:
        raise corona_exceptions.RegionNotFoundError(region)
    return corona_constants.REGION_TO_COUNTRIES[region]


def get_regions():
    """Функция для получения всех доступных регионов"""

    return corona_constants.REGION_TO_COUNTRIES.keys()


def get_region_by_country(country):
    """Функция для получения региона по стране"""

    for region, countries in corona_constants.REGION_TO_COUNTRIES.items():
        if country in countries:
            return region
    raise corona_exceptions.CountryNotFoundError(country)


def _get_article_href(region):
    """Функция для получения ссылки на страницу с информацией о данной стране"""

    key_article_name_part = corona_constants.REGION_TO_KEY_ARTICLE_NAME_PART.get(region)
    if not key_article_name_part:
        raise corona_exceptions.RegionNotFoundError(region)

    page = 1
    while True:
        r = requests.get(corona_constants.MID_PAGE_URL_TEMPLATE.format(page=page))

        if r.status_code != 200:
            # пересмотрели все страницы
            raise corona_exceptions.ArticleNotFoundError(key_article_name_part)

        soup = BeautifulSoup(r.content, 'html.parser')
        all_articles = soup.find_all('a', {'class': 'anons-title'})
        for article in all_articles:
            if key_article_name_part in article.text:
                return article['href']

        page += 1


def _get_date_of_relevance(soup):
    all_suitable_fragments = soup.find_all('p', {'style': 'text-align: right;'})
    for fragment in all_suitable_fragments:
        text = fragment.text
        if text.startswith('По состоянию на'):
            return text
    logger.warning('Can not find date_of_relevance')
    return 'По состоянию на -'


def _get_rows_from_article_soup(soup):
    return soup.find_all('tr')[2:-2]


def _extract_info(soup):
    return soup.text.strip('\n')


def _parse_row(row):
    tds = row.find_all('td')

    country_name = tds[corona_constants.CoronaArticleTableColumn.COUNTRY_NAME].text
    border_info = _extract_info(tds[corona_constants.CoronaArticleTableColumn.BORDER_INFO])
    restriction_info = _extract_info(tds[corona_constants.CoronaArticleTableColumn.RESTRICTION_INFO])

    return country_name, {
        corona_constants.CoronaInfoType.BORDERS: border_info,
        corona_constants.CoronaInfoType.REQUIREMENTS: restriction_info,
    }


def get_full_info(country, info_type):
    """Функция для получения информации о стране"""
    if info_type not in corona_constants.CoronaInfoType.values():
        raise corona_exceptions.UnknownCoronaInfoType(info_type)

    logger.info('Getting {} info about {}'.format(info_type, country))

    region = get_region_by_country(country)
    article_href = _get_article_href(region)

    r = requests.get(article_href)
    soup = BeautifulSoup(r.content, 'html.parser')

    for row in _get_rows_from_article_soup(soup):
        country_name_from_article, type_to_info = _parse_row(row)

        if country in country_name_from_article:
            info = type_to_info[info_type]
            date_of_relevance = _get_date_of_relevance(soup)

            return '\n\n'.join((country, info, date_of_relevance))

    raise corona_exceptions.CountryInfoNotFoundError


def get_full_info_about_all_countries_in_region(region):
    """Функция для получения информации о всех странах региона"""

    logger.info('Getting infos about countries in region {}'.format(region))

    article_href = _get_article_href(region)

    r = requests.get(article_href)
    soup = BeautifulSoup(r.content, 'html.parser')

    country_name_from_article_to_corona_info = {}
    for row in _get_rows_from_article_soup(soup):
        country_name_from_article, type_to_info = _parse_row(row)
        country_name_from_article_to_corona_info[country_name_from_article] = type_to_info

    country_to_corona_info = {}

    ordered_countries_from_article = sorted(country_name_from_article_to_corona_info.keys())
    i = 0
    for country in get_countries_by_region(region):
        while i < len(ordered_countries_from_article):
            country_from_article = ordered_countries_from_article[i]
            if country in country_from_article:
                country_to_corona_info[country] = country_name_from_article_to_corona_info[country_from_article]
                i += 1
                break
            i += 1

    return country_to_corona_info
