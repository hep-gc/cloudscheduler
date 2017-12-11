import os
import sys
import yaml


db_host = "localhost"
db_port = 3306
db_user = "csv2"
db_password = ""



if os.path.isfile("/etc/csv2_web.yaml"):
    path = "/etc/csv2_web.yaml"

elif os.path.isfile("/opt/cloudscheduler/web_frontend/cloudscheduler/csv2/csv2_web.yaml"):
    path = "/opt/cloudscheduler/web_frontend/cloudscheduler/csv2/csv2_web.yaml"


try:
    with open(path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

except Exception as e:
    print >> sys.stderr, "Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path



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
