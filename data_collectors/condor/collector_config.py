from os.path import join, expanduser, exists, abspath
import sys
import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

collection_interval = 15
command_sleep_interval = 10
cleanup_sleep_interval = 120
log_file = "/var/log/cloudscheduler/cscollector.log"
log_level = 20 #INFO

db_host = "localhost"
db_port = 3306
db_user = "csv2"
db_password = ""



if exists("/etc/cloudscheduler/cloudscheduler.yaml"):
    path = "/etc/cloudscheduler/cloudscheduler.yaml"

elif exists("/opt/cloudscheduler/cloudscheduler.yaml"):
    path = "/opt/cloudscheduler/cloudscheduler.yaml"


try:
    with open(path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

except Exception as e:
    print("Configuration file problem: There was a " \
          "problem reading %s. Check that it is readable," \
          "and that it exists. " % path, file=sys.stderr)

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

try:
    Base = automap_base()
    engine = create_engine("mysql+pymysql://" + db_user + ":" + db_password + "@" + db_host + ":" + str(db_port) + "/" + db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Conf = Base.classes.csv2_config

    # Query General openstack config
    db_yaml = db_session.query(Conf).get("condor_machines")

    try:
        cfg = yaml.load(db_yaml.yaml)   
        if "condor_machines" in cfg:
            if "collection_interval" in cfg["condor_machines"]:
                collection_interval = cfg["condor_machines"]["collection_interval"]

            if "command_sleep_interval" in cfg["condor_machines"]:
                command_sleep_interval = cfg["condor_machines"]["command_sleep_interval"]

            if "cleanup_sleep_interval" in cfg["condor_machines"]:
                cleanup_sleep_interval = cfg["condor_machines"]["cleanup_sleep_interval"]

            if "log_file" in cfg["condor_machines"]:
                log_file = cfg["condor_machines"]["log_file"]

            if "log_level" in cfg["condor_machines"]:
                log_level = cfg["condor_machines"]["log_level"]       

    except yaml.YAMLError:
        print("Unable to load condor machines config from yaml blob in database" \
              " Please check the yaml in database and retry", file=sys.stderr)
        sys.exit(1)


except Exception as e:
    print("Unable to connect to the database and extract relevent config," \
          " please ensure the database parameters are correct and restart csjobs", file=sys.stderr)
    print(e, file=sys.stderr)
    sys.exit(1)
