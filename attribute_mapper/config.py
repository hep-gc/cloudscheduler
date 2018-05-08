import os
import sys
import yaml

log_file = "/var/log/cloudscheduler/attribute_mapper.log"
log_level = 20 #INFO

db_host = "localhost"
db_port = 3306
db_user = "csv2"
db_password = ""



if os.path.isfile("/etc/cloudscheduler/cloudscheduler.yaml"):
    path = "/etc/cloudscheduler/cloudscheduler.yaml"

elif os.path.isfile("/opt/cloudscheduler/cloudscheduler.yaml"):
    path = "/opt/cloudscheduler/cloudscheduler.yaml"

else:
    path = os.path.dirname(os.path.realpath(__file__)) + "/attribute_mapper.yaml"


try:
    with open(path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

except Exception as e:
    print >> sys.stderr, "Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path


if "general" in cfg:

    if "log_file" in cfg["general"]:
        log_file = cfg["general"]["log_file"]

    if "log_level" in cfg["general"]:
        log_level = cfg["general"]["log_level"]


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
