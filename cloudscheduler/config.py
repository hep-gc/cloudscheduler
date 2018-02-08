import yaml


default_config_file_location = "/etc/cloudscheduler/cloudscheduler.yaml"


class CSConfig():
    def __init__(self, **kwargs):
        self.name = kwargs['general'].get('name', 'cloudscheduler')
        self.keyname = kwargs['general'].get('keyname', None)

        self.cloudscheduler_log_file = kwargs['general'].get('cloudscheduler_log_file', '/var/log/cloudscheduler/cloudscheduler.log')

        self.db_user = kwargs['database'].get('db_user', 'csv2')
        self.db_password = kwargs['database'].get('db_password', None)
        self.db_host = kwargs['database'].get('db_host', 'localhost')
        self.db_port = kwargs['database'].get('db_port', 3306)
        self.db_name = kwargs['database'].get('db_name', 'csv2')

        self.default_instancetype = kwargs['job'].get('instancetype', 'm1.small')
        self.default_image = kwargs['job'].get('image', 'cernvm3-micro-2.8-6.hdd')

    @staticmethod
    def setup(config_file=default_config_file_location):
        # Prime the dict with it's sections:
        config = {'general': {}, 'job': {}}
        # Load up any changed values from file
        try:
            with open(config_file) as f:
                config_file = yaml.load(f.read())
                # Merge them and update the defaults
                for k, v in config_file.items():
                    config[k] = v
        except Exception as e:
            print(e)
        return config


config = CSConfig(**CSConfig.setup())

