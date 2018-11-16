from django.conf import settings
config = settings.CSV2_CONFIG

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


def get_db_base_and_session():
    config.db_open()
    Base = config.db_map
    Engine = config.db_engine
    session = config.db_session
    return (Base, session)