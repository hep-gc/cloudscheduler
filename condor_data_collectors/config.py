from os.path import join, expanduser, exists, abspath
import sys
import yaml

job_collection_interval = 15
machine_collection_interval = 15
command_sleep_interval = 10
job_log_file = "/var/log/cloudscheduler/csjobs.log"
collector_log_file = "/var/log/cloudscheduler/cscollector.log"

db_host = "localhost"
db_port = 3306
db_user = "csv2"
db_password = ""



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

    if "command_sleep_interval" in cfg["general"]:
        command_sleep_interval = cfg["general"]["command_sleep_interval"]

    if "job_log_file" in cfg["general"]:
        job_log_file = cfg["general"]["job_log_file"]

    if "collector_log_file" in cfg["general"]:
        collector_log_file = cfg["general"]["collector_log_file"]


if "database" in cfg:
    if "db_host" in cfg["database"]:
        db_host = cfg["database"]["db_host"]

    if "db_port" in cfg["database"]:
        db_port = cfg["database"]["db_port"]

    if "db_name" in cfg["database"]:
        db_name = cfg["database"]["db_name"]

    if "db_user" in cfg["database"]:
        db_user = cfg["database"]["db_user"]

    if "db_password" in cfg["database"]:
        db_password = cfg["database"]["db_password"]

