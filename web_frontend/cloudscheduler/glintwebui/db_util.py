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
        from cloudscheduler.lib.db_config import Config
        config = Config('/etc/cloudscheduler/cloudscheduler.yaml', 'web_frontend', pool_size=4)
        config.db_open()
        Base = config.db_map
        Engine = config.db_engine
        session = config.db_session
        return (Base, session)

