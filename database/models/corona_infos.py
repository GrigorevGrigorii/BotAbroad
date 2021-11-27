from sqlalchemy import Column, Text
from database.__main__ import Base

import libs.constants.corona as corona_constants


class BaseCoronaInfosModel:
    country = Column(Text, primary_key=True)
    border_info = Column(Text, default=None)
    requirement_info = Column(Text, default=None)

    def __repr__(self):
        return "{}: {}".format(self.__name__, ', '.join(['{}={}'.format(key, value) for key, value in self.__dict__ if not key.startswith('__')]))


class CoronaInfosAmerica(Base, BaseCoronaInfosModel):
    """
    Информация о коронавирусных ограничениях в Северной и Южной Америке
    """

    __tablename__ = "corona_infos_america"


class CoronaInfosEurope(Base, BaseCoronaInfosModel):
    """
    Информация о коронавирусных ограничениях в Европе
    """

    __tablename__ = "corona_infos_europe"


class CoronaInfosAsia(Base, BaseCoronaInfosModel):
    """
    Информация о коронавирусных ограничениях в Азии и Океании
    """

    __tablename__ = "corona_infos_asia"


class CoronaInfosCIS(Base, BaseCoronaInfosModel):
    """
    Информация о коронавирусных ограничениях в СНГ, Грузии, Абхазии и Южной Осетии
    """

    __tablename__ = "corona_infos_cis"


class CoronaInfosAfrica(Base, BaseCoronaInfosModel):
    """
    Информация о коронавирусных ограничениях в Африке, Ближнем и Среднем Востоке
    """

    __tablename__ = "corona_infos_africa"


REGION_TO_MODEL = {
    corona_constants.Region.AMERICA: CoronaInfosAmerica,
    corona_constants.Region.EUROPE: CoronaInfosEurope,
    corona_constants.Region.ASIA: CoronaInfosAsia,
    corona_constants.Region.CIS: CoronaInfosCIS,
    corona_constants.Region.AFRICA: CoronaInfosAfrica,
}

