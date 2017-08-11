import yaml

class CSConfig():
    def __init__(self, **kwargs):
        self.name = kwargs['general']['name']
        self.redishost = kwargs['general']['redishost']
        self.redisport = kwargs['general']['redisport']
        self.job_data_keys = kwargs['general']['job_data_keys']
        self.collector_data_keys = kwargs['general']['collector_data_keys']
        self.vm_data_key = kwargs['general']['vm_data_keys']

        self.default_instancetype = kwargs['job']['instancetype']
        self.default_image = kwargs['job']['image']


default_config_file_location = "/etc/cloudscheduler/cloudscheduler.yaml"

# Declare all the defaults internally so the keys exists
config = yaml.load("""
general:
    name: Test
    collector_data_keys: [condor-resources]
    job_data_keys: [condor-jobs]
    vm_data_keys: [vm-data]
    redishost: localhost
    redisport: 1234
job:
    instancetype: m1.small
    image: CentOS 7
    
""")
# Load up any changed values from file
try:
    with open(default_config_file_location) as f:
        config_file = yaml.load(f.read())
        # Merge them and update the defaults
        for k, v in config_file.items():
            config[k] = v
except Exception as e:
    print(e)

conf = CSConfig(**config)

print(conf.redishost)
print(conf)
