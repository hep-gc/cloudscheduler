from os.path import exists, abspath
import sys
import configparser

# set default values
static_files_root = "/var/www/glintv2/static/"
cert_auth_bundle_path = "/etc/glintv2/CABundle.crt"
log_file_path = "/var/log/glintv2/glintv2.log"
database_path = "/etc/glintv2/"
database_name = "db.sqlite3"
celery_url = "redis://localhost:6379/0"
celery_backend = "redis://localhost:6379/"
redis_host = "localhost"
redis_port = 6379
redis_db = 0
image_collection_interval = 12
cache_expire_time = 604800 #default 7 days (in seconds)


# find config file by first checking the /etc/glintv2 location
# if its not there look for the default one in the glintv2 install location

if exists("/etc/cloudscheduler/glintv2.conf"):
    path = "/etc/cloudscheduler/glintv2.conf"
elif  exists(abspath(sys.path[0]+"/../config/glintv2.conf")):
    path = abspath(sys.path[0]+"/../config/glintv2.conf")
else:
    print("Configuration file problem: There doesn't " \
          "seem to be a configuration file. " \
          "You can specify one in /etc/glintv2/glintv2.conf", file=sys.stderr)
    sys.exit(1)

config_file = configparser.ConfigParser()
try:
    config_file.read(path)
except IOError:
    print("Configuration file problem: There was a " \
          "problem reading %s. Check that it is readable," \
          "and that it exists. " % path, file=sys.stderr)
    raise
except ConfigParser.ParsingError:
    print("Configuration file problem: Couldn't " \
          "parse your file. Check for spaces before or after variables.", file=sys.stderr)
    raise
except:
    print("Configuration file problem: There is something wrong with " \
          "your config file.", file=sys.stderr)
    raise

# sets defaults to the options in the config_file
if config_file.has_option("general", "static_files_root"):
    static_files_root = config_file.get("general", "static_files_root")

if config_file.has_option("general", "cert_auth_bundle_path"):
    cert_auth_bundle_path = config_file.get("general", "cert_auth_bundle_path")

if config_file.has_option("general", "log_file_path"):
    log_file_path = config_file.get("general", "log_file_path")

if config_file.has_option("general", "database_path"):
    database_path = config_file.get("general", "database_path")

if config_file.has_option("general", "database_name"):
    database_name = config_file.get("general", "database_name")

if config_file.has_option("general", "image_collection_interval"):
    image_collection_interval = int(config_file.get("general", "image_collection_interval"))

if config_file.has_option("general", "cache_expire_time"):
    cache_expire_time = int(config_file.get("general", "cache_expire_time"))




if config_file.has_option("celery", "celery_url"):
    celery_url = config_file.get("celery", "celery_url")

if config_file.has_option("celery", "celery_backend"):
    celery_backend = config_file.get("celery", "celery_backend")



if config_file.has_option("redis", "redis_host"):
    redis_host = config_file.get("redis", "redis_host")

if config_file.has_option("redis", "redis_port"):
    redis_port = config_file.get("redis", "redis_port")

if config_file.has_option("redis", "redis_db"):
    redis_db = config_file.get("redis", "redis_db")
    
