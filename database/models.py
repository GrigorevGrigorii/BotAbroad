from sqlalchemy import Column, Integer, String
from database.database import Base


class State(Base):
    """
    Здесь для каждого пользователя хранится список состояний его бота. Возможные состояния:
    region_selection - ожидается ввод региона;
    country_selection - ожидается ввод страны;
    borders_command - происходит обработка команды /borders;
    requirements_command - происходит обработка команды /requirements;
    Состояние может отсутствовать (бот в покое).
    Возможно также комбинировать некоторые состояния.
    Все состояния хранятся в виде строки. Несколько состояний разделены символом / (слэш).
    Состоянию покоя соответствует пустая строка.
    """

    __tablename__ = "states"

    _id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    state = Column(String(40), default='')
    # Максимальная длина состояния (включая возможные комбинации) не превышает 38, поэтому здесь с запасом 40.
    # При добавлении каких-то состояний пересчитать максимальную длину и возможно увеличить допустимую длину.

    def __repr__(self):
        return f"<State: chat_id={self.chat_id}, state={self.state}>"
