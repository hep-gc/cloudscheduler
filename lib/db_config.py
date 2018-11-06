"""
DB utilities and configuration.
"""

import os
import socket
import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

class Config:
    def __init__(self, db_yaml, categories, db_config_dict=False):
        """
        Read the DB configuration file and the specified categories configuration from the database.
        """

        # Retrieve the database configuration.
        if os.path.exists(db_yaml):
            with open(db_yaml, 'r') as ymlfile:
                base_config = yaml.load(ymlfile)
        else:
            raise Exception('Configuration file "%s" does not exist.' % db_yaml)

        db_config = {}
        if 'database' in base_config:
            for item in base_config['database']:
                db_config[item] = base_config['database'][item]

            if 'db_table' not in db_config:
                db_config['db_table'] = 'configuration'

        if db_config_dict:
            self.db_config = db_config

        # Open the database.
        self.db_engine = create_engine(
            'mysql://%s:%s@%s:%s/%s' % (
                db_config['db_user'],
                db_config['db_password'],
                db_config['db_host'],
                str(db_config['db_port']),
                db_config['db_name']
                ),
            isolation_level="READ_COMMITTED",
            pool_pre_ping=True
            )

        self.db_connection = None
        self.db_map = automap_base()
        self.db_map.prepare(self.db_engine, reflect=True)

        # Create a unique instance ID from our FQDN and, if necessary, save it in the database
        self.csv2_host_id = sum(socket.getfqdn().encode())

        self.db_session = Session(self.db_engine)
        rows = self.db_session.query(self.db_map.classes[db_config['db_table']]).filter(
            (self.db_map.classes[db_config['db_table']].category == 'SQL') &
            (self.db_map.classes[db_config['db_table']].config_key == 'csv2_host_id')
            )

        if self.csv2_host_id != rows[0].csv2_host_id:
            try:
                self.db_session.update(self.db_map.classes[db_config['db_table']]).where(
                    (self.db_map.classes[db_config['db_table']].category == 'SQL') &
                    (self.db_map.classes[db_config['db_table']].config_key == 'csv2_host_id')
                    ).values({'config_value': self.csv2_host_id})

                self.db_session.commit()

            except:
                if rc != 0:
                    print("Error updating csv2_host_id in db_config: %s" % msg)

        # Retrieve the configuration for the specified category.
        if isinstance(categories, str):
            category_list = [ categories ]
        else:
            category_list = categories

        for category in category_list:
            rows = self.db_session.query(self.db_map.classes[db_config['db_table']]).filter(
                self.db_map.classes[db_config['db_table']].category == category
                )

            for row in rows:
                if row.config_type == 'bool':
                    self.__dict__[row.config_key] = row.config_value == '1' or row.config_value.lower() == 'yes' or row.config_value.lower() == 'true'
                elif row.config_type == 'float':
                    self.__dict__[row.config_key] = float(row.config_value)
                elif row.config_type == 'int':
                    self.__dict__[row.config_key] = int(row.config_value)
                elif row.config_type == 'null':
                    self.__dict__[row.config_key] = None
                else:
                    self.__dict__[row.config_key] = row.config_value

        # Close the session.
        self.db_session.close()
        self.db_session = None

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

