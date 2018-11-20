from django.conf import settings
config = settings.CSV2_CONFIG

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


def get_db_base_and_session():
    try:
        config.db_open()
        Base = config.db_map
        Engine = config.db_engine
        session = config.db_session
        return (Base, session)
    except:
        from . import config as old_config
        Base = automap_base()
        Engine = create_engine("mysql://" + old_config.db_user + ":" + old_config.db_password + \
                               "@" + old_config.db_host+ ":" + str(old_config.db_port) + "/" + old_config.db_name,
                               pool_size=50, max_overflow=10)
        Base.prepare(Engine, reflect=True)
        session = Session(Engine)
        return (Base, session)

