"""
DB utilities and configuration.
"""

import os
import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

class Config:
    def __init__(self, categories, db_config_dict=False):
        """
        Read the DB configuration file and the specified categories configuration from the database.
        """

        # Retrieve the database configuration.
        if os.path.exists("/etc/cloudscheduler/cloudscheduler.yml"):
            path = "/etc/cloudscheduler/cloudscheduler.yml"

        elif os.path.exists("/etc/cloudscheduler/cloudscheduler.yaml"):
            path = "/etc/cloudscheduler/cloudscheduler.yaml"

        else:
            raise Exception('Configuration file (either "/etc/cloudscheduler/cloudscheduler.yml" or ' \
                '"/etc/cloudscheduler/cloudscheduler.yaml") not found.')

        with open(path, 'r') as ymlfile:
            base_config = yaml.load(ymlfile)

        db_config = {}
        if 'database' in base_config:
            for item in base_config['database']:
                db_config[item] = base_config['database'][item]

        if db_config_dict:
            self.__dict__['db_config'] = db_config

        # Open the database.
        self.__dict__['db_engine'] = create_engine(
            'mysql://%s:%s@%s:%s/%s' % (
                db_config['db_user'],
                db_config['db_password'],
                db_config['db_host'],
                str(db_config['db_port']),
                db_config['db_name']
                )
            )

        self.__dict__['db_connection'] = None
        self.__dict__['db_map'] = automap_base()
        self.__dict__['db_map'].prepare(self.__dict__['db_engine'], reflect=True)

        # Retrieve the configuration for the specified category.
        if isinstance(categories, str):
            category_list = [ categories ]
        else:
            category_list = categories

        self.__dict__['db_session'] = Session(self.__dict__['db_engine'])
        for category in category_list:
            rows = self.__dict__['db_session'].query(self.__dict__['db_map'].classes.csv2_configuration).filter(
                self.__dict__['db_map'].classes.csv2_configuration.category == category
                )

            for row in rows:
                if row.type == 'bool':
                    self.__dict__[row.config_key] = row.value == '1' or row.value.lower() == 'yes' or row.value.lower() == 'true'
                elif row.type == 'float':
                    self.__dict__[row.config_key] = float(row.value)
                elif row.type == 'int':
                    self.__dict__[row.config_key] = int(row.value)
                elif row.type == 'null':
                    self.__dict__[row.config_key] = None
                else:
                    self.__dict__[row.config_key] = row.value

        # Close the session.
        self.__dict__['db_session'].close()
        self.__dict__['db_session'] = None

#-------------------------------------------------------------------------------

    def db_close(self, commit=False):
        """
        Commit/rollback and close a session.
        """

        if self.db_session:
            if commit:
                self.db_session.commit()
            else:
                self.db_session.rollback()

            self.db_session.close()
            self.db_session = None

        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None

#-------------------------------------------------------------------------------

    def db_open(self):
        """
        Open and return a database connection.
        """

        self.db_connection = self.db_engine.connect()
        self.db_session = Session(bind=self.db_engine)

#-------------------------------------------------------------------------------

    def db_session_execute(self, request, allow_no_rows=False):
        """
        Execute a DB request and return the response. Also, trap and return errors.
        """

        from sqlalchemy.engine.result import ResultProxy
        import sqlalchemy.exc

        try:
            result_proxy = self.db_session.execute(request)
            if result_proxy.rowcount == 0 and not allow_no_rows:
                return 1, 'the request did not match any rows'
            return 0, result_proxy.rowcount
        except sqlalchemy.exc.IntegrityError as ex:
            return 1, ex.orig
        except Exception as ex:
            return 1, ex

