import yaml


default_config_file_location = "/etc/cloudscheduler/cloudscheduler.yaml"

class CSConfig():
    def __init__(self, **kwargs):
        self.name = kwargs['general'].get('name', 'CloudScheduler')
        self.redishost = kwargs['general'].get('redishost', 'localhost')
        self.redisport = kwargs['general'].get('redisport', 6379)
        self.job_data_keys = kwargs['general'].get('job_data_keys', ['condor-jobs'])
        self.collector_data_keys = kwargs['general'].get('collector_data_keys', ['condor-resources'])
        self.vm_data_key = kwargs['general'].get('vm_data_keys', ['vm-data'])

        self.default_instancetype = kwargs['job'].get('instancetype', 'm1.small')
        self.default_image = kwargs['job'].get('image', 'Cent OS 7')

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


#conf = CSConfig(**CSConfig.setup())

