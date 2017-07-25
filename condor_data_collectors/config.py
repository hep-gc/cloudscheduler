from os.path import join, expanduser, exists, abspath
import sys
import yaml

job_collection_interval = 15
machine_collection_interval = 15
command_sleep_interval = 10
job_commands_key = "job_commands"
collector_commands_key = "collector_commands"
job_data_key = "condor-jobs"
collector_data_key = "condor-resources"
job_log_file = "/var/log/csjobs.log"
collector_log_file = "/var/log/cscollector.log"

redis_host = "localhost"
redis_port = 6379
redis_db = 0
redis_password = ""

if exists("/etc/condor_data_collectors.yaml"):
    path = "/etc/condor_data_collectors.yaml"

elif exists("/opt/cloudscheduler/condor_data_collectors/condor_data_collectors.yaml"):
    path = "/opt/cloudscheduler/condor_data_collectors/condor_data_collectors.yaml"


try:
    with open(path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

except Exception as e:
    print >> sys.stderr, "Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path



if "general" in cfg:
    if "job_collection_interval" in cfg["general"]:
        job_collection_interval = cfg["general"]["job_collection_interval"]

    if "machine_collection_interval" in cfg["general"]:
        machine_collection_interval = cfg["general"]["machine_collection_interval"]

    if "command_sleep_interval" in cfg["general"]):
        command_sleep_interval = cfg["general"]["command_sleep_interval"]

    if "job_commands_key" in cfg["general"]:
        job_commands_key = cfg["general"]["job_commands_key"]

    if "collector_commands_key" in cfg["general"]:
        collector_commands_key = cfg["general"]["collector_commands_key"]

    if "job_data_key" in cfg["general"]:
        job_data_key = cfg["general"]["job_data_key"]

    if "collector_data_key":
        collector_data_key = cfg["general"]["collector_data_key"]

    if "job_log_file" in cfg["general"]:
        job_log_file = cfg["general"]["job_log_file"]

    if "collector_log_file" in cfg["general"]:
        collector_log_file = cfg["general"]["collector_log_file"]


if "redis" in cfg:
    if "redis_host" in cfg["redis"]:
        redis_host = cfg["redis"]["redis_host"]

    if "redis_port" in cfg["redis"]:
        redis_port = cfg["redis"]["redis_port"]

    if "redis_db" in cfg["redis"]:
        redis_db = cfg["redis"]["redis_db"]

    if "redis_password" in cfg["redis"]:
        redis_password = cfg["redis"]["redis_password"]

