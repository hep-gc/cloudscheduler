from os.path import join, expanduser, exists, abspath
import sys
import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

poller_log_file = "/var/log/cloudscheduler/openstackpoller.log"
vm_sleep_interval = 60
vm_cleanup_interval = 120
network_sleep_interval = 300
network_cleanup_interval = 3600
image_sleep_interval = 300
image_cleanup_interval = 3600
limit_sleep_interval = 300
limit_cleanup_interval = 3600
flavor_sleep_interval = 300
flavor_cleanup_interval = 3600
cacert = "/etc/ssl/certs/CABundle.crt"
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
    print >> sys.stderr, "Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path

# Database config loaded from local file

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


# Specific configuration loaded from the database

# First do the database setup
try:
    Base = automap_base()
    engine = create_engine("mysql://" + db_user + ":" + db_password + "@" + db_host + ":" + str(db_port) + "/" + db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Conf = Base.classes.csv2_config

    # Query General openstack config
    db_yaml = db_session.query(Conf).get("os_general")

    try:
        cfg = yaml.load(db_yaml.yaml)   
        if "general" in cfg:
            if "poller_log_file" in cfg["general"]:
                poller_log_file = cfg["general"]["poller_log_file"]

            if "cacert" in cfg["general"]:
                cacert = cfg["general"]["cacert"]

            if "log_level" in cfg["general"]:
                log_level = cfg["general"]["log_level"]
    except yaml.YAMLError:
        print >> sys.stderr, "Unable to load general os config from yaml blob in database" \
                         "Please check the yaml in database and retry"
        sys.exit(1)

    # Query VM config
    db_yaml = db_session.query(Conf).get("os_vms")

    try:
        cfg = yaml.load(db_yaml.yaml)
        if "openstack_vms" in cfg:
            if "sleep_interval" in cfg["openstack_vms"]:
                vm_sleep_interval = cfg["openstack_vms"]["sleep_interval"]

            if "cleanup_interval" in cfg["openstack_vms"]:
                vm_cleanup_interval = cfg["openstack_vms"]["cleanup_interval"]
    except yaml.YAMLError:
        print >> sys.stderr, "Unable to load os vm config from yaml blob in database" \
                         "Please check the yaml in database and retry"
        sys.exit(1)


    # Query Networks config
    db_yaml = db_session.query(Conf).get("os_networks")

    try:
        cfg = yaml.load(db_yaml.yaml)
        if "openstack_networks" in cfg:
            if "sleep_interval" in cfg["openstack_networks"]:
                network_sleep_interval = cfg["openstack_networks"]["sleep_interval"]

    except yaml.YAMLError:
        print >> sys.stderr, "Unable to load os network config from yaml blob in database" \
                         "Please check the yaml in database and retry"
        sys.exit(1)


    # Query Images config
    db_yaml = db_session.query(Conf).get("os_images")

    try:
        cfg = yaml.load(db_yaml.yaml)
        if "openstack_images" in cfg:
            if "sleep_interval" in cfg["openstack_images"]:
                image_sleep_interval = cfg["openstack_images"]["sleep_interval"]

    except yaml.YAMLError:
        print >> sys.stderr, "Unable to load os image config from yaml blob in database" \
                         "Please check the yaml in database and retry"
        sys.exit(1)


    # Query Limits config
    db_yaml = db_session.query(Conf).get("os_limits")

    try:
        cfg = yaml.load(db_yaml.yaml)
        if "openstack_limits" in cfg:
            if "sleep_interval" in cfg["openstack_limits"]:
                limit_sleep_interval = cfg["openstack_limits"]["sleep_interval"]

    except yaml.YAMLError:
        print >> sys.stderr, "Unable to load os limit config from yaml blob in database" \
                         "Please check the yaml in database and retry"
        sys.exit(1)


    # Query Flavors config
    db_yaml = db_session.query(Conf).get("os_flavors")

    try:
        cfg = yaml.load(db_yaml.yaml)
        if "openstack_flavors" in cfg:
            if "sleep_interval" in cfg["openstack_flavors"]:
                flavor_sleep_interval = cfg["openstack_flavors"]["sleep_interval"]

    except yaml.YAMLError:
        print >> sys.stderr, "Unable to load os flavor config from yaml blob in database" \
                         "Please check the yaml in database and retry"
        sys.exit(1)



except Exception as e:
    print >> sys.stderr, "Unable to connect to the database and extract relevent config," \
                     "please ensure the database parameters are correct and restart csmetadata"
    print >> sys.stderr, e
    sys.exit(1)
