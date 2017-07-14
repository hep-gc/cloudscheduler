from os.path import join, expanduser, exists, abspath
import sys
import ConfigParser

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

if exists("/etc/condor_data_collectors.cfg"):
    path = "/etc/condor_data_collectors.cfg"

elif exists("/opt/cloudscheduler/condor_data_collectors/condor_data_collectors.cfg"):
    path = "/opt/cloudscheduler/condor_data_collectors/condor_data_collectors.cfg"

config_file = ConfigParser.ConfigParser()
try:
    config_file.read(path)
except IOError:
    print >> sys.stderr, "Configuration file problem: There was a " \
                         "problem reading %s. Check that it is readable," \
                         "and that it exists. " % path

if config_file.has_option("general", "job_collection_interval"):
    job_collection_interval = int(config_file.get("general", "job_collection_interval"))

if config_file.has_option("general", "machine_collection_interval"):
    machine_collection_interval = int(config_file.get("general", "machine_collection_interval"))

if config_file.has_option("general", "command_sleep_interval"):
    command_sleep_interval = int(config_file.get("general", "command_sleep_interval"))

if config_file.has_option("general", "job_commands_key"):
    job_commands_key = config_file.get("general", "job_commands_key")

if config_file.has_option("general", "collector_commands_key"):
    collector_commands_key = config_file.get("general", "collector_commands_key")

if config_file.has_option("general", "job_data_key"):
    job_data_key = config_file.get("general", "job_data_key")

if config_file.has_option("general", "collector_data_key"):
    collector_data_key = config_file.get("general", "collector_data_key")

if config_file.has_option("general", "job_log_file"):
    job_log_file = config_file.get("general", "job_log_file")

if config_file.has_option("general", "collector_log_file"):
    collector_log_file = config_file.get("general", "collector_log_file")



if config_file.has_option("redis", "redis_host"):
    redis_host = config_file.get("redis", "redis_host")

if config_file.has_option("redis", "redis_port"):
    redis_port = config_file.get("redis", "redis_port")

if config_file.has_option("redis", "redis_db"):
    redis_db = config_file.get("redis", "redis_db")

if config_file.has_option("redis", "redis_password"):
    redis_password = config_file.get("redis", "redis_password")

