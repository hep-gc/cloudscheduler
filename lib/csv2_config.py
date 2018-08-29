"""
Load configuration.
"""

import os
import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

class Config:
    def __init__(self, category):
        """
        Read the DB configuration file and the specified catagories configuration from the database.
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

        if 'database' in base_config:
            for item in base_config['database']:
                self.__dict__[item] = base_config['database'][item]

        # Open the database.
        db = {
            'base': automap_base(),
            'engine': create_engine(
                'mysql://%s:%s@%s:%s/%s' % (
                    self.db_user,
                    self.db_password,
                    self.db_host,
                    str(self.db_port),
                    self.db_name
                    )
                )
            }
        db['session'] = Session(db['engine'])

        db['base'].prepare(db['engine'], reflect=True)

        # Retrieve the configuration for the specified category.
        rows = db['session'].query(db['base'].classes.csv2_configuration).filter(
            db['base'].classes.csv2_configuration.category == category
            )

        for row in rows:
            if row.type == 'bool':
                self.__dict__[row.config_key] = row.value == '1' or row.value.lower() == 'yes' or row.value.lower() == 'true'
            elif row.type == 'float':
                self.__dict__[row.config_key] = float(row.value)
            elif row.type == 'int':
                self.__dict__[row.config_key] = int(row.value)
            else:
                self.__dict__[row.config_key] = row.value

        # Close the database.
        del db
