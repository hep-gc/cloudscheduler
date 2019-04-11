from os.path import join, expanduser, exists, abspath
import sys
import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

static_files_root = "/var/www/glintv2/static/"
cert_auth_bundle_path = "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"
log_file_path = "/var/log/cloudscheduler/csv2_web.log"
celery_url = "redis://localhost:6379/0"
celery_backend = "redis://localhost:6379/"
redis_host = "localhost"
redis_port = 6379
redis_db = 0
image_collection_interval = 30
cache_expire_time = 604800 #default 7 days (in seconds)

db_host = "localhost"
db_port = 3306
db_user = "csv2"
db_password = ""



if exists("/etc/cloudscheduler/cloudscheduler.yaml"):
    path = "/etc/cloudscheduler/cloudscheduler.yaml"

elif exists("/opt/cloudscheduler/cloudscheduler.yaml"):
    path = "/opt/cloudscheduler/cloudscheduler.yaml"
else:
    path = None

try:
    with open(path, 'r') as ymlfile:
        cfg = yaml.full_load(ymlfile)

except Exception as e:
    print("Configuration file problem: There was a " \
          "problem reading %s. Check that it is readable," \
          "and that it exists. " % path, file=sys.stderr)
    cfg = None
    
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

        # Query glint config
        db_yaml = db_session.query(Conf).get("glint")

        try:
            cfg = yaml.full_load(db_yaml.yaml)
            if "redis" in cfg:
                if "redis_host" in cfg["redis"]:
                    redis_host = cfg["redis"]["redis_host"]

                if "redis_port" in cfg["redis"]:
                    redis_port = cfg["redis"]["redis_port"]

                if "redis_db" in cfg["redis"]:
                    redis_db = cfg["redis"]["redis_db"]

            if "general" in cfg:
                if "image_collection_interval" in cfg["general"]:
                    image_collection_interval = cfg["general"]["image_collection_interval"]

                if "cache_expire_time" in cfg["general"]:
                    cache_expire_time = cfg["general"]["cache_expire_time"]

            if "celery" in cfg:
                if "celery_url" in cfg["celery"]:
                    celery_url = cfg["celery"]["celery_url"]

                if "celery_backend" in cfg["celery"]:
                    celery_backend = cfg["celery"]["celery_backend"]

        except yaml.YAMLError:
            print("Unable to load condor jobs config from yaml blob in database" \
                  " Please check the yaml in database and retry", file=sys.stderr)
            sys.exit(1)


    except Exception as e:
        print("Unable to connect to the database and extract relevent config," \
              " please ensure the database parameters are correct and restart", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)
