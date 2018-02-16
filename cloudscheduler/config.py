"""
Loader for the basic configuration information needed to
connect to the database and initial setup.
"""

import logging
import yaml


class CSConfig:

    """
    CSConfig - loads basic configuration settings for cloudscheduler.
    """
    def __init__(self, **kwargs):
        """
        Load the configs from a dict and set appropriate defaults.
        This may get replaced with a different ConfigParse setup later.

        :param kwargs: dictionary of config key:value pairs
        """
        self.log = logging.getLogger(__name__)
        self.name = kwargs['general'].get('name', 'cloudscheduler')
        self.keyname = kwargs['general'].get('keyname', None)

        self.cloudscheduler_log_file = \
            kwargs['general'].get('cloudscheduler_log_file',
                                  '/var/log/cloudscheduler/cloudscheduler.log')

        self.db_user = kwargs['database'].get('db_user', 'csv2')
        self.db_password = kwargs['database'].get('db_password', None)
        self.db_host = kwargs['database'].get('db_host', 'localhost')
        self.db_port = kwargs['database'].get('db_port', 3306)
        self.db_name = kwargs['database'].get('db_name', 'csv2')

        self.default_instancetype = kwargs['job'].get('instancetype', 'm1.small')
        self.default_image = kwargs['job'].get('image', 'cernvm3-micro-2.8-6.hdd')
        self.default_network = kwargs['job'].get('network', 'private')

    def setup(config_file="/etc/cloudscheduler/cloudscheduler.yaml"):
        """
        Reading a yaml and stuffing into dictionary for use in the constructor.

        :param config_file: the file path where the config is stored on disk
        :return: the config object
        """
        # Prime the dict with it's sections:
        lconfig = {'general': {}, 'job': {}}
        # Load up any changed values from file
        try:
            with open(config_file) as file_handle:
                config_file = yaml.load(file_handle.read())
                # Merge them and update the defaults
                for k, val in config_file.items():
                    lconfig[k] = val
        except FileNotFoundError as ex:
            self.log.exception(ex)
        except yaml.parser.ParserError as ex:
            self.log.exception(ex)
        return lconfig


config = CSConfig(**CSConfig.setup())
