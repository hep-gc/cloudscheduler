import yaml

default_config_file_location = "/etc/cloudscheduler/cloudscheduler.yaml"

config = yaml.load("""
name: Test
collectorkeys: [testkey1, testkey2]
jobkeys: [jobkey1]
vmpollkey: vmpoll
redishost: localhost
redisport: 1234
""")

with open(default_config_file_location) as f:
    config = yaml.load(f.read())


