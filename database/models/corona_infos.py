from sqlalchemy import Column, Text
from database.__main__ import Base


class CoronaInfos(Base):
    """
    Информация о коронавирусных ограничениях
    """

    __tablename__ = "corona_infos"

    region = Column(Text, primary_key=True)
    country = Column(Text, primary_key=True)
    border_info = Column(Text, default=None)
    requirement_info = Column(Text, default=None)

    def __repr__(self):
        return "{}: {}".format(self.__name__, ', '.join(['{}={}'.format(key, value) for key, value in self.__dict__ if not key.startswith('__')]))
