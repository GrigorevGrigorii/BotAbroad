from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import os

engine = create_engine(os.environ.get('DATABASE_URL'), convert_unicode=True)
Base = declarative_base()


def init_db():
    from database.models import chat_id_to_command_and_state
    from database.models import users
    from database.models import corona_infos
    Base.metadata.create_all(bind=engine)
