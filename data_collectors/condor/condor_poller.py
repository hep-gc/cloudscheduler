import multiprocessing
import time
import signal
import socket
import logging
import subprocess
from multiprocessing import Process
import os
import re
import sys
import yaml

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.fw_config import configure_fw
from cloudscheduler.lib.poller_functions import \
    inventory_cleanup, \
    inventory_obsolete_database_items_delete, \
    inventory_get_item_hash_from_db_query_rows, \
    inventory_test_and_set_item_hash, \
    start_cycle, \
    wait_cycle, \
    log_heartbeat_message
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, check_pid, terminate
from cloudscheduler.lib.watchdog_utils import watchdog_send_heartbeat

import htcondor
import classad
import boto3
import datetime

MASTER_TYPE = htcondor.AdTypes.Master
STARTD_TYPE = htcondor.AdTypes.Startd

# DB permissions comments:
#    mysql_privileges_map_table_to_variables condor_machines  RESOURCE
#    mysql_privileges_map_table_to_variables condor_jobs      JOB Job
#    mysql_privileges_map_table_to_variables csv2_clouds      CLOUD CLOUDS cloud_table 
#    mysql_privileges_map_table_to_variables csv2_groups      GROUPS
#    mysql_privileges_map_table_to_variables csv2_user        USERS
#    mysql_privileges_map_table_to_variables csv2_vms         VM
#    config.db_merge(csv2_clouds)
#    config.db_merge(csv2_service_catalog)
#    config.db_merge(csv2_configuration)
#    config.db_merge(csv2_watchdog)
#    config.db_update(csv2_watchdog)
#    config.db_update(csv2_clouds)
#    config.db_update('condor_worker_gsi')
#    .db_query('condor_worker_gsi')
#    .db_query('csv2_clouds')
#    .db_query('csv2_groups')
#    .db_query('csv2_attribute_mapping')
#    .db_query('csv2_user_groups')
#    .db_query('csv2_watchdog')


# condor likes to return extra keys not defined in the projection
# this function will trim the extra ones so that we can use kwargs
# to initiate a valid table row based on the data returned
def trim_keys(dict_to_trim, key_list):
    keys_to_trim = ["Owner"]
    for key in dict_to_trim:
        if key == "group_name" or key == "target_alias":
            continue
        if key not in key_list or isinstance(dict_to_trim[key], classad.Value):
            keys_to_trim.append(key)
    for key in keys_to_trim:
        dict_to_trim.pop(key, None)
    return dict_to_trim


def get_condor_dict(config, logging):
    condor_dict = {}
    rc, msg, group_list = config.db_query('csv2_groups', select=['group_name', 'htcondor_fqdn'])
    for group in group_list:
        try:
            condor_ip = socket.gethostbyname(group['htcondor_fqdn'])
            if group['htcondor_fqdn'] not in condor_dict:
                condor_dict[group['htcondor_fqdn']] = []

            condor_dict[group['htcondor_fqdn']].append(group['group_name'])

        except:
            logging.debug('Ignoring invalid condor host "%s".' % group['htcondor_fqdn'])

    return condor_dict


def fill_attributes(old_dict, attributes, config, additional_attributes = []):
    # create a dictionary and map its attributes
    new_dict = old_dict.copy()
    attributes_dict = {key: None for key in attributes}
    attributes_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=attributes_dict, config=config)
    
    # fill missing attributes in filled_job_dict
    all_keys = list(attributes_dict.keys()) + additional_attributes
    new_dict.update({key: None for key in all_keys if key not in new_dict})

    return new_dict


def if_null(val, col=None):
    if col:
        if val:
            return '%s="%s"' % (col, val)
        else:
            return '%s=NULL' % col

    else:
        if val:
            return val
        else:
            return 'NULL'



def condor_off(condor_classad):
    try:
        logging.debug("Sending condor_off to %s" % condor_classad)
        master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)
        if master_result is None:
            # None is good in this case it means it was a success
            master_result = "Success"
        logging.info("Condor_off result: %s" % master_result)
        return master_result
    except Exception as exc:
        logging.error("Condor off failed:")
        logging.error(exc)
        return False

def decode(obj):
    if not obj:
        return ''
    elif isinstance(obj, str):
        return obj
    else:
        return obj.decode('utf-8')

def get_condor_session(hostname=None):
    try:
        condor_session = htcondor.Collector(hostname)
        return condor_session
    except Exception as exc:
        logging.error("Failed to get condor session for %s:" % hostname)
        logging.error(exc)
        return False

def get_gsi_cert_subject_and_eol(cert):
    if not os.access(cert, os.R_OK):
        logging.warning('function: get_gsi_cert_subject_and_eol, pem: %s is unreadable.' % cert)
        return 'unreadable', -999999

    if os.path.isfile(cert):
        p1 = subprocess.Popen([
            'openssl',
            'x509',
            '-noout',
            '-subject',
            '-in',
            cert
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p1.communicate()

        stdout = decode(stdout)
        if p1.returncode == 0 and stdout != '':
            words = decode(stdout).split()
            subject = words[1]

            p1 = subprocess.Popen([
                'openssl',
                'x509',
                '-noout',
                '-dates',
                '-in',
                cert
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            p2 = subprocess.Popen([
                'awk',
                '/notAfter=/ {print substr($0,10)}'
                ], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p2.communicate()

            if p2.returncode == 0:
                eol = int(time.mktime(time.strptime(decode(stdout[:-1]), '%b %d %H:%M:%S %Y %Z')))
                return subject, eol
            else:
                logging.error('function: get_gsi_cert_subject_and_eol(openssl x509 -dates), cert: %s, rc: %s, stdout: %s, stderr: %s' % (cert, p2.returncode, decode(stdout), decode(stderr)))
        else:
            logging.error('function: get_gsi_cert_subject_and_eol(openssl x509 -subject), cert: %s, rc: %s, stdout: %s, stderr: %s' % (cert, p1.returncode, decode(stdout), decode(stderr)))
    else:
        logging.error('function: get_gsi_cert_subject_and_eol(openssl x509 -subject), cert: "%s" does not exist.' % cert)

    return None, None


def get_master_classad(session, machine, hostname):
    try:
        if machine != "":
            condor_classad = session.query(MASTER_TYPE, 'Name=="%s"' % machine)[0]
        else:
            condor_classad = session.query(MASTER_TYPE, 'regexp("%s", Name, "i")' % hostname)[0]
        return condor_classad
    except IndexError:
        logging.error("Failed to retrieve classad from condor. No matching classad")
    except Exception as exc:
        logging.error("Failed to retrieve classad from condor. Communication error :")
        logging.error(exc)
        return -1
    return False


def get_startd_classads(session, machine):
    startd_list = []
    try:
        condor_classads = session.query(STARTD_TYPE, 'Machine=="%s"' % machine)
        for classad in condor_classads:
            startd_list.append(classad)
        return startd_list
    except Exception as exc:
        logging.error("Failed to retrieve machine classads, aborting...")
        logging.error(exc)
        return False


def invalidate_master_classad(session, classad):
    return session.advertise([classad], "INVALIDATE_MASTER_ADS")

def invalidate_startd_classads(session, classad_list):
    return session.advertise(classad_list, "INVALIDATE_STARTD_ADS")
       
def yaml_full_load(yaml_string):
    if hasattr(yaml, 'full_load'):
        return yaml.full_load(yaml_string)
    else:
        return yaml.load(yaml_string)

def zip_base64(path):
    if not os.access(path, os.R_OK):
        logging.warning('function: zip_base64, pem: %s is unreadable.' % path)
        return 'unreadable'

    if os.path.isfile(path):
        p1 = subprocess.Popen([
            'gzip',
            '-c',
            path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        p2 = subprocess.Popen([
            'base64'
            ], stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p2.communicate()

        if p2.returncode == 0:
            return decode(stdout)
        else:
            logging.error('function: zip_base64, pem: %s, rc: %s, stdout: %s, stderr: %s' % (path, p2.returncode, decode(stdout), decode(stderr)))

    return None


def process_group_cloud_commands(pair, condor_host, config):
    group_name = pair["group_name"]
    cloud_name = pair["cloud_name"]


    VM = "csv2_vms"
    CLOUD = "csv2_clouds"

    retire_off = config.categories["condor_poller.py"]["retire_off"]
    retire_interval = config.categories["condor_poller.py"]["retire_interval"]

    master_type = htcondor.AdTypes.Master
    startd_type = htcondor.AdTypes.Startd


    #logging.info("Processing commands for group:%s, cloud:%s" % (group_name, cloud_name))
    logging.debug("Processing commands for group:%s, cloud:%s" % (group_name, cloud_name))


    # RETIRE CODE:
    # Query database for machines to be retired.
    where_clause = "htcondor_fqdn='%s' and cloud_name='%s' and group_name='%s' and (retire>=1 or terminate>=1)" % (condor_host, cloud_name, group_name)
    logging.debug("Query where clause: %s" % where_clause)
    #logging.info("Query where clause: %s" % where_clause)

    rc, msg, resources_list = config.db_query("view_condor_host", where=where_clause)
    logging.debug("Query returned %s actionable VMs..." % len(resources_list))
    for resource in resources_list:
        # Since we are querying a view we dont get an automapped object and instead get a 'result' tuple of the following format
        #index=attribute
        #0=group
        #1=cloud
        #2=htcondor_fqdn
        #3=vmid
        #4=hostname
        ##5primary_slots
        ##6dynamic_slots
        #7=retireflag
        #8=terminate flag
        #9=machine
        #10=updater
        #logging.debug("%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (resource.group_name, resource.cloud_name, resource.htcondor_fqdn, resource.vmid, resource.hostname, resource[5], resource[6], resource.retire, resource.updater, resource.terminate, resource.machine))
        # First check the slots to see if its time to terminate this machine

        #check if retire flag set & a successful retire has happened  and  (htcondor_dynamic_slots<1 || NULL) and htcondor_partitionable_slots>0, issue condor_off and increment retire by 1.
        if resource["retire"] >= 1:
            if (resource["dynamic_slots"] is None or resource["dynamic_slots"]<1) and (resource["primary_slots"] is None or resource["primary_slots"]<1):
                #check if terminate has already been set
                if not resource["terminate"] >= 1:
                  # set terminate=1
                  # need to get vm classad because we can't update via the view.
                  try:
                      logging.info("slots are zero or null on %s, setting terminate, last updater: %s" % (resource["hostname"], resource["updater"]))
                      logging.debug("group_name:%s\ncloud_name:%s\nhtcondor_fqdn:%s\nvmid:%s\nhostname%s\nPrimary Slots:%s\nDynamic Slots:%s\nretire:%s\nupdater:%s\nterminate:%s\nmachine:%s" % (resource["group_name"], resource["cloud_name"], resource["htcondor_fqdn"], resource["vmid"], resource["hostname"], resource["primary_slots"], resource["dynamic_slots"], resource["retire"], resource["updater"], resource["terminate"], resource["machine"]))

                      where_clause = "group_name='%s' and cloud_name='%s' and vmid='%s'" % (resource["group_name"], resource["cloud_name"], resource["vmid"])
                      rc, msg, vm_rows = config.db_query(VM, where=where_clause)
                      vm_row = vm_rows[0]
                      vm_row["terminate"] = 1
                      vm_row["updater"] = str(get_frame_info() + ":t1")
                      config.db_merge(VM, vm_row)
                      config.db_commit()

                  except Exception as exc:
                      # unable to get VM row error
                      logging.error(exc)
                      logging.error("%s ready to be terminated but unable to locate vm_row" % resource["vmid"])
                      continue
            if resource["retire"] >= 10:
                continue


        if retire_off:
            logging.critical("Retires disabled, normal operation would retire %s" % resource["hostname"])
            continue


        # check the retire time to see if it has been enough time since the last retire was issued
        # if it's none we haven't issued a retire yet and can skip the check
        if resource["retire_time"] is not None:
            if int(time.time()) - resource["retire_time"] < retire_interval:
                # if the time since last retire is less than the configured retire interval, continue
                logging.debug("Resource has been retired recently... skipping for now.")
                continue


        logging.info("Retiring (%s) machine %s primary slots: %s dynamic slots: %s, last updater: %s" % (resource["retire"], resource["machine"], resource["dynamic_slots"], resource["primary_slots"], resource["updater"]))
        try:
            condor_session = get_condor_session()
# crlb #    if resource["machine"] is not "":
            if resource["machine"] and len(resource["machine"]) > 0:
                condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource["machine"])[0]
            else:
                condor_classad = condor_session.query(master_type, 'regexp("%s", Name, "i")' % resource["hostname"])[0]

            if not condor_classad or condor_classad == -1:
                #there was a condor error
                logging.error("Unable to retrieve condor classad, skipping %s ..." % resource["machine"])

            try:
                logging.info("Issuing DaemonsOffPeaceful to %s" % condor_classad)
                master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)
                logging.debug("Result: %s " % master_result)
            except Exception as exc:
                # this should be tightened to catch exact errors coming from condor
                # since the bindings method of retire seems to have failed lets issue a local system command
                logging.info("failed to retire via condor bindings, attempting system command")
                logging.debug("condor_drain -exit-on-completion %s" % resource["name"] ) 
                cndr_drain = subprocess.run(["condor_drain", "-exit-on-completion", resource["name"]])
                logging.debug("Command executed")
                logging.debug(cndr_drain.stdout)
                logging.debug(cndr_drain.stderr)
                # the command below will throw an error if the condor_drain command fails but presently it fails when the machine is already draining
                # and the output and error are empty to we cant distinguish between an error because it's already draining from any other without more commands
                #cndr_drain.check_returncode() 
                
            #get vm entry and update retire = 2
            where_clause = "group_name='%s' and cloud_name='%s' and vmid='%s'" % (resource["group_name"], resource["cloud_name"], resource["vmid"])
            rc, msg, vm_rows = config.db_query(VM, where=where_clause)
            vm_row = vm_rows[0]
            vm_row["retire"] = vm_row["retire"] + 1
            vm_row["updater"] = str(get_frame_info() + ":r+")
            vm_row["retire_time"] = int(time.time())
            config.db_merge(VM, vm_row)
            try:
                config.db_commit()
            except Exception as exc:
                logging.exception("Failed to commit batch of retired machines, aborting cycle...")
                logging.error(exc)
                break

        except Exception as exc:
            logging.debug(exc)
            logging.error("Failed to issue DaemonsOffPeacefull to machine: %s, hostname: %s missing classad or condor miscomunication." % (resource["machine"], resource["hostname"]))
            logging.debug(condor_host)
            continue

    try:
        config.db_commit()
    except Exception as exc:
        logging.exception("Failed to commit retire machine, aborting cycle...")
        logging.error(exc)
        config.db_rollback()
        return

    logging.debug("Commands complete...")
    return



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def job_poller():
    multiprocessing.current_process().name = "Job Poller"
    job_attributes = ["TargetClouds", "JobStatus", "RequestMemory", "GlobalJobId", "HoldReason",
                      "RequestDisk", "RequestCpus", "RequestScratch", "RequestSwap", "Requirements",
                      "JobPrio", "ClusterId", "ProcId", "User", "VMInstanceType", "VMNetwork",
                      "VMImage", "VMKeepAlive", "VMMaximumPrice", "VMUserData", "VMJobPerCore", "Owner",
                      "EnteredCurrentStatus", "QDate", "HoldReasonCode", "HoldReasonSubCode", 
                      "LastRemoteHost", "TargetAlias", "CpusProvisioned"]
    # Not in the list that seem to be always returned:
    # FileSystemDomian, MyType, ServerTime, TargetType
    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    fail_count = 0
    inventory = {}
    delete_cycle = True
    cycle_count = 0
    uncommitted_updates = 0
    failure_dict = {}

    config = Config(sys.argv[1], ["condor_poller.py", "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])


    JOB = "condor_jobs"
    CLOUDS = "csv2_clouds"
    GROUPS = "csv2_groups"
    USERS = "csv2_user_groups"
    ikey_names = ["global_job_id", "group_name", "htcondor_host_id"]
    last_heartbeat_time = 0


    try:
        config.db_open()
        where_clause = "htcondor_host_id='%s'" % config.local_host_id
        rc, msg, rows = config.db_query(JOB, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()

        #old inventory
        #inventory = get_inventory_item_hash_from_database(config.db_engine, JOB, 'global_job_id', debug_hash=(config.categories["condor_poller.py"]["log_level"]<20), condor_host=config.local_host_id)
        while True:
            config.db_open()
            last_heartbeat_time = log_heartbeat_message(last_heartbeat_time, "JOB POLLER")
            #
            # Setup - initialize condor and database objects and build user-group list
            #
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
            config.refresh()

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            where_clause = "htcondor_host_id='%s'" % config.local_host_id
            rc, msg, groups = config.db_query(GROUPS, where=where_clause)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            condor_host_groups = {}
            group_users = {}
            for group in groups:
                if group["htcondor_container_hostname"] is not None and group["htcondor_container_hostname"] != "":
                    condor_central_manager = group["htcondor_container_hostname"]
                    condor_hosts_set.add(group["htcondor_container_hostname"])
                elif group.get("htcondor_fqdn") is not None and group.get("htcondor_fqdn") != "":
                    condor_central_manager = group.get("htcondor_fqdn")
                    condor_hosts_set.add(group.get("htcondor_fqdn"))
                else:
                    # no condor location set
                    logging.debug("No condor location set")
                    continue                

                if condor_central_manager not in condor_host_groups:
                    condor_host_groups[condor_central_manager] = [group["group_name"]]
                else:
                    condor_host_groups[condor_central_manager].append(group["group_name"])

                # build group_users dict
                htcondor_other_submitters = group["htcondor_other_submitters"]
                user_list = []
                if htcondor_other_submitters == 'ALL':
                    #rc, msg, users = config.db_query(USERS)
                    #for usr in users:
                    #    user_list.append(usr["username"])
                    user_list = ["ALL"]
                else:
                    where_clause = "group_name='%s'" % group["group_name"]
                    rc, msg, users = config.db_query(USERS, where=where_clause)
                    if htcondor_other_submitters is not None:
                        user_list = group["htcondor_other_submitters"].split(',')
                    else:
                        user_list = []
                    # need to append users from group defaultts (htcondor_supplementary_submitters) here
                    # alternatively we can just have 2 lists and check both wich would save on memory if there was a ton of users but cost cycles
                    for usr in users:
                        user_list.append(usr["username"])

                group_users[group["group_name"]] = user_list
            
            fail_commit = False
            uncommitted_updates = 0
            foreign_jobs = 0
            for condor_host in condor_hosts_set:
                logging.debug("Polling %s" % condor_host)
                foreign_jobs = 0
                held_jobs = 0
                held_job_ids = []
                logging.info("Polling condor host: %s" % condor_host)
                try:
                    coll = htcondor.Collector(condor_host)
                    try:
                        scheddAd = coll.locate(htcondor.DaemonTypes.Schedd, condor_host)
                    except:
                        #sometimes the name of the process doesnt match the name of the host but if we don't provide a name it will look for a local one
                        scheddAd = coll.locate(htcondor.DaemonTypes.Schedd)
                    condor_session = htcondor.Schedd(scheddAd)

                except Exception as exc:
                    # if we fail we need to mark all these groups as failed so we don't delete the entrys later
                    fail_count = 0
                    for group in groups:
                        if group.get("htcondor_fqdn") is not None and group["htcondor_fqdn"] != "":
                            if group["htcondor_fqdn"] == condor_host:
                                if group["group_name"] not in failure_dict:
                                    failure_dict[group["group_name"]] = 1
                                    fail_count = failure_dict[group["group_name"]]
                                else:
                                    failure_dict[group["group_name"]] = failure_dict[group["group_name"]] + 1
                                    fail_count = failure_dict[group["group_name"]]
                        else:
                            if group["htcondor_container_hostname"] == condor_host:
                                if group["group_name"] not in failure_dict:
                                    failure_dict[group["group_name"]] = 1
                                    fail_count = failure_dict[group["group_name"]]
                                else:
                                    failure_dict[group["group_name"]] = failure_dict[group["group_name"]] + 1
                                    fail_count = failure_dict[group["group_name"]]
                    logging.error("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.debug(exc)
                    delete_cycle = False

                    if fail_count > 3 and fail_count < 1500:
                        logging.critical("%s failed polls on host: %s, Configuration error or condor issues" % (fail_count, condor_host))
                    elif fail_count > 1500:
                        logging.critical("Over 1500 failed polls on host: %s, Configuration error or condor issues" % (fail_count, condor_host))
                    continue

                # Retrieve jobs.
                
                logging.debug("getting job list from condor")
                try:
                    job_list = condor_session.xquery(
                        projection=job_attributes
                        )
                except Exception as exc:
                    # if we fail we need to mark all these groups as failed so we don't delete the entrys later
                    fail_count = 0
                    for group in groups:
                        if group.get("htcondor_fqdn") is not None and group["htcondor_fqdn"] != "":
                            if group["htcondor_fqdn"] == condor_host:
                                if group["group_name"] not in failure_dict:
                                    failure_dict[group["group_name"]] = 1
                                    fail_count = failure_dict[group["group_name"]]
                                else:
                                    failure_dict[group["group_name"]] = failure_dict[group["group_name"]] + 1
                                    fail_count = failure_dict[group["group_name"]]
                        else:
                            if group["htcondor_container_hostname"] == condor_host:
                                if group["group_name"] not in failure_dict:
                                    failure_dict[group["group_name"]] = 1
                                    fail_count = failure_dict[group["group_name"]]
                                else:
                                    failure_dict[group["group_name"]] = failure_dict[group["group_name"]] + 1
                                    fail_count = failure_dict[group["group_name"]]
                    logging.error("Failed to get jobs from condor scheddd object, aborting poll on host: %s" % condor_host)
                    logging.error(exc)
                    delete_cycle = False
                    if fail_count > 3:
                        logging.critical("%s failed polls on host: %s, Configuration error or condor issues" % (fail_count, condor_host))
                    continue

                # Process job data & insert/update jobs in Database
                abort_cycle = False
                job_errors = {}
                logging.debug(job_list)
                for job_ad in job_list:
                    logging.debug(job_ad)
                    job_dict = dict(job_ad)
                    if "Requirements" in job_dict:
                        ca1=classad.ClassAd(job_dict)
                        et2 = ca1.flatten(job_dict).eval()
                        job_dict['Requirements'] = str(et2['Requirements'])
                        if "RequestMemory" in job_dict:
                            try:    
                                if isinstance(et2['RequestMemory'], int):
                                    job_dict['RequestMemory'] = et2['RequestMemory']
                                else:   
                                    job_dict['RequestMemory'] = et2['RequestMemory'].eval()
                                if isinstance(job_dict['RequestMemory'], int):
                                    pass    
                                else:   
                                    job_dict['RequestMemory'] = ca1['RequestMemory'].eval()
                            except Exception as exc: 
                                #need to tighten this exception but basically if the memory isnt an expression this isn't going to work 
                                #it might be better to instead check the data type in the dictionary then base execution off that than to depends on error handling
                                pass    

                        # Parse group_name out of requirements
                        try:
                            #pattern = '(group_name is ")(.*?)(")'
                            pattern = '(group_name is "|group_name == "|group_name =\?= "|group_name =\?= toLower\("|group_name is toLower\("|group_name == toLower\(")(.*?)(")'
                            grp_name = re.search(pattern, job_dict['Requirements'])
                            job_dict['group_name'] = grp_name.group(2).lower()
                        except Exception as exc:
                            logging.debug("No group name found in requirements expression... ignoring foreign job.")
                            foreign_jobs = foreign_jobs+1
                            if "nogrp" not in job_errors:
                                job_errors["nogrp"] = 1
                                job_errors["nogrpinfo"] = {"Submitter: %s" % job_dict['Owner']}
                            else:
                                job_errors["nogrp"] = job_errors["nogrp"] + 1
                                job_errors["nogrpinfo"].add("Submitter: %s" % job_dict['Owner'])
                            continue
                        # Look for a target_alias in requirements string
                        try:
                            pattern = '(target_alias is "|target_alias == "|target_alias =\?= "|target_alias =\?= toLower\("|target_alias is toLower\("|target_alias == toLower\(")(.*?)(")'
                            target_alias = re.search(pattern, job_dict['Requirements'])
                            job_dict['target_alias'] = target_alias.group(2).lower()
                        except Exception as exc:
                            logging.debug("No alias found in requirements expression")
                    else:
                        logging.debug("No requirements attribute found, not a csv2 job... ignoring foreign job.")
                        foreign_jobs = foreign_jobs+1
                        if "noreq" not in job_errors:
                            job_errors["noreq"] = 1
                            job_errors["noreqinfo"] = {"Submitter: %s" % job_dict['Owner']}
                        else:
                            job_errors["noreq"] = job_errors["noreq"] + 1
                            job_errors["noreqinfo"].add("Submitter: %s" % job_dict['Owner'])
                        continue

                    #check group_name is valid for this host
                    if job_dict['group_name'] not in condor_host_groups[condor_host]:
                        # not a valid group for this host
                        logging.debug("%s is not a valid group for %s, ignoring foreign job." % (job_dict['group_name'], condor_host))
                        foreign_jobs = foreign_jobs+1
                        held_jobs = held_jobs + 1
                        #check if job is already held
                        if job_dict["JobStatus"] != 5:
                            held_job_ids.append(str(job_dict["ClusterId"]) +"."+ str(job_dict["ProcId"]))
                        if "invalidgrp" not in job_errors:
                            job_errors["invalidgrp"] = 1
                            job_errors["invalidgrpinfo"] = {"Invalid group: %s" % job_dict['group_name']}
                        else:
                            job_errors["invalidgrp"] = job_errors["invalidgrp"] + 1
                            job_errors["invalidgrpinfo"].add("Invalid group: %s" % job_dict['group_name'])

                        continue

                    # check if user is valid for this group
                    if group_users[job_dict['group_name']] and "ALL" not in group_users[job_dict['group_name']]:
                        if job_dict['Owner'] not in group_users[job_dict['group_name']]:
                            # this user isn''t registered with this group and thus cannot submit jobs to it
                            logging.debug("User '%s' is not registered to submit jobs to %s, excluding as foreign job." % (job_dict['Owner'], job_dict['group_name']))
                            foreign_jobs = foreign_jobs+1
                            held_jobs = held_jobs + 1
                            if job_dict["JobStatus"] != 5:
                                held_job_ids.append(str(job_dict["ClusterId"]) +"."+ str(job_dict["ProcId"]))
                            if "invalidusr" not in job_errors:
                                job_errors["invalidusr"] = 1
                                job_errors["invalidusrinfo"] = {"Invalid user: %s for group: %s" % (job_dict['Owner'], job_dict['group_name'])}
                            else:
                                job_errors["invalidusr"] = job_errors["invalidusr"] + 1
                                job_errors["invalidusrinfo"].add("Invalid user: %s for group: %s" % (job_dict['Owner'], job_dict['group_name']))
                            continue

                    # Some jobs have an expression for the request disk causing us to store a string
                    # this should resolve the expression or us an alternative if unable
                    try:
                        job_dict["RequestDisk"] = int(job_dict["RequestDisk"])
                    except Exception as exc:
                        job_dict["RequestDisk"] = int(job_dict["DiskUsage"])
                    try:
                        job_dict["RequestCpus"] = int(job_dict["RequestCpus"])
                    except Exception as exc:
                        logging.debug("Request Cpus not set, setting minimum (1)")
                        job_dict["RequestCpus"] = 1

                    try:
                        # This is a fix specifically for dune which only submits pilot jobs that then pick up bigger jobs
                        # the intention is to use the core count of the real job instead of the pilot
                        job_dict["RequestCpus"] = job_dict["CpusProvisioned"]
                    except:
                        pass


                    job_dict = trim_keys(job_dict, job_attributes)
                    job_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=job_dict, config=config)
                    logging.debug("Adding job %s", job_dict["global_job_id"])
                    job_dict["htcondor_host_id"] = config.local_host_id
                    logging.debug(job_dict)
                    if unmapped:
                        logging.debug("attribute mapper found unmapped variables:")
                        logging.debug(unmapped)

                    # Check if this item has changed relative to the local cache, skip it if it's unchanged
                    # old inventory function
                    #if test_and_set_inventory_item_hash(inventory, job_dict["group_name"], "-", job_dict["global_job_id"], job_dict, new_poll_time, debug_hash=(config.categories["condor_poller.py"]["log_level"]<20)):
                    
                    # fill any missing keys in job_dict with None
                    filled_job_dict = fill_attributes(job_dict, job_attributes, config, ["hold_job_reason", "target_alias"])

                    # New inventory function:
                    if inventory_test_and_set_item_hash(ikey_names, filled_job_dict, inventory, new_poll_time, debug_hash=(config.categories["condor_poller.py"]["log_level"]<20)):
                        continue

                    try:
                        config.db_merge(JOB, job_dict)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.error("Failed to merge job entry, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break

                    try:
                        config.db_commit()
                    except Exception as exc:
                        logging.error("Failed to commit new jobs, aborting cycle...")
                        logging.error(exc)
                        config.db_rollback()
                        abort_cycle = True
                        fail_commit = True
                        break

                if held_jobs > 0:
                    #hold all the jobs
                    logging.info("%s jobs held or to be held due to invalid user or group specifications." % held_jobs)
                    logging.debug("Holding: %s" % held_job_ids)
                    try:
                        logging.debug("Executing job action hold on %s" % condor_host)
                        logging.debug("<< SKIPPING HOLDS, AUTHENTICATION NOT SET UP FOR REMOTE HOLDS >>")
                        #hold_result = condor_session.act(htcondor.JobAction.Hold, held_job_ids)
                        #logging.debug("Hold result: %s" % hold_result)
                        #condor_session.edit(held_job_ids, "HoldReason", '"Invalid user or group name for htondor host %s, held by job poller"' % condor_host)
                    except Exception as exc:
                        logging.debug("Failure holding jobs: %s" % exc)
                        logging.debug("Aborting cycle...")
                        abort_cycle = True
                        break


                config.update_service_catalog(counter=foreign_jobs)

                        
                if foreign_jobs > 0:
                    logging.debug("Ignored total of: %s jobs on %s. Summary:" % (foreign_jobs, condor_host))
                    if "nogrp" in job_errors:
                        logging.debug("    %s jobs ignored for missing group name" % job_errors["nogrp"])
                        for item in job_errors["nogrpinfo"]:
                            logging.debug("        %s" % item)
                    if "noreq" in job_errors:
                        logging.debug("    %s jobs ignored for missing requirements string" % job_errors["noreq"])
                        for item in job_errors["noreqinfo"]:
                            logging.debug("        %s" % item)
                    if "invalidgrp" in job_errors:
                        logging.debug("    %s jobs ignored & held for submitting to invalid group for host" % job_errors["invalidgrp"])
                        for item in job_errors["invalidgrpinfo"]:
                            logging.debug("        %s" % item)
                    if "invalidusr" in job_errors:
                        logging.debug("    %s ignored & held for submitting to a group without permission" % job_errors["invalidusr"])
                        for item in job_errors["invalidusrinfo"]:
                            logging.debug("        %s" % item)

                # Poll successful, update failure_dict accordingly
                for group in groups:
                    if group.get("htcondor_fqdn") is not None and group["htcondor_fqdn"] != "":
                        if group["htcondor_fqdn"] == condor_host:
                             failure_dict.pop(group["group_name"], None)
                    else:
                        if group["htcondor_container_hostname"] == condor_host:
                            failure_dict.pop(group["group_name"], None)


                if abort_cycle:
                    config.db_rollback()
                    break

            if uncommitted_updates > 0:
                logging.info("Job updates committed: %d" % uncommitted_updates)
            if fail_commit:
                logging.info("Previous had failed commit")
                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                time.sleep(config.categories["condor_poller.py"]["sleep_interval_job"])
                continue

            if delete_cycle:
                # Check for deletes
                # New poller function:
                where_clause = "htcondor_host_id='%s'" % config.local_host_id
                rc, msg, rows = config.db_query(JOB, where=where_clause)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, JOB)

                #old inventory func
                #delete_obsolete_database_items('Jobs', inventory, db_session, JOB, 'global_job_id', poll_time=new_poll_time, failure_dict=failure_dict, condor_host=config.local_host_id)

                delete_cycle = False

            cycle_count = cycle_count + 1
            if cycle_count >= config.categories["condor_poller.py"]["delete_cycle_interval"]:
                delete_cycle = True
                cycle_count = 0

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, config.signals['SIGINT'])    
            config.db_close()
            wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_job"], config)

    except Exception as exc:
        logging.exception("Job Poller while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()


def machine_poller():
    multiprocessing.current_process().name = "Machine Poller"
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", \
                           "Activity", "VMType", "MyCurrentTime", "EnteredCurrentState", "Cpus", \
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", \
                           "cloud_name", "cs_host_id", "condor_host", "flavor", "TotalDisk"]

    config = Config(sys.argv[1], ["condor_poller.py", "SQL", "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])


    RESOURCE = "condor_machines"
    CLOUDS = "csv2_clouds"
    GROUPS = "csv2_groups"

    ikey_names = ["name", "group_name", "htcondor_host_id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    inventory = {}
    #delete_interval = config.delete_interval
    delete_cycle = False
    #condor_inventory_built = False
    cycle_count = 0
    uncommitted_updates = 0
    failure_dict = {}
    last_heartbeat_time = 0

    try:
        config.db_open()
        where_clause = "htcondor_host_id='%s'" % config.local_host_id
        rc, msg, rows = config.db_query(RESOURCE, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)

        # old inventory func
        #inventory = get_inventory_item_hash_from_database(config.db_engine, RESOURCE, 'name', debug_hash=(config.categories["condor_poller.py"]["log_level"]<20), condor_host=config.local_host_id)
        configure_fw(config, logging)
        config.db_close()
        while True:
            last_heartbeat_time = log_heartbeat_message(last_heartbeat_time, "MACHINE POLLER")
            config.db_open()
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            where_clause = "htcondor_host_id='%s'" % config.local_host_id
            rc, msg, groups = config.db_query(GROUPS, where=where_clause)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                if group.get("htcondor_container_hostname") is not None and group["htcondor_container_hostname"] != "":
                    condor_hosts_set.add(group["htcondor_container_hostname"])
                else:
                    condor_hosts_set.add(group["htcondor_fqdn"])

            # need to make a data structure so that we can verify the the polled machines actually fit into a valid grp-cloud
            # need to check:
            #       - group_name (in both group_name and machine)
            #       - cloud_name (only in machine?)
            host_groups = {}
            for group in groups:
                cloud_list = []
                where_clause = "group_name='%s'" % group["group_name"]
                rc, msg, clouds = config.db_query(CLOUDS, select=["cloud_name"], where=where_clause)
                for cloud in clouds:
                    cloud_list.append(cloud["cloud_name"])
                host_groups[group["group_name"]] = cloud_list

            fail_commit = False
            for condor_host in condor_hosts_set:
                logging.debug("Polling condor host: %s" % condor_host)
                forgein_machines = 0
                try:
                    condor_session = htcondor.Collector(condor_host)
                except Exception as exc:
                    logging.exception("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.error(exc)
                    delete_cycle = False
                    continue


                # Retrieve machines.
                try:
                    condor_resources = condor_session.query(
                        ad_type=htcondor.AdTypes.Startd,
                        projection=resource_attributes
                         )
                except Exception as exc:
                    # if we fail we need to mark all these groups as failed so we don't delete the entrys later
                    fail_count = 0
                    for group in groups:
                        if group.get("htcondor_fqdn") is not None and group["htcondor_fqdn"] != "":
                            if group["htcondor_fqdn"] == condor_host:
                                if group["group_name"] not in failure_dict:
                                    failure_dict[group["group_name"]] = 1
                                    fail_count = failure_dict[group["group_name"]]
                                else:
                                    failure_dict[group["group_name"]] = failure_dict[group["group_name"]] + 1
                                    fail_count = failure_dict[group["group_name"]]
                        else:
                            if group["htcondor_container_hostname"] == condor_host:
                                if group["group_name"] not in failure_dict:
                                    failure_dict[group["group_name"]] = 1
                                    fail_count = failure_dict[group["group_name"]]
                                else:
                                    failure_dict[group["group_name"]] = failure_dict[group["group_name"]] + 1
                                    fail_count = failure_dict[group["group_name"]]

                    logging.error("Failed to get machines from condor collector object, aborting poll on host %s" % condor_host)
                    logging.error(exc)
                    delete_cycle = False
                    if fail_count > 3:
                        logging.critical("More than 3 consecutive failed polls on host: %s, Configuration error or condor issues" % condor_host)
                    continue

                fail_commit = False
                abort_cycle = False
                machine_errors = {}
                uncommitted_updates = 0
                for resource in condor_resources:
                    r_dict = dict(resource)
                    if 'group_name' not in r_dict:
                        logging.debug("Skipping resource with no group_name.")
                        forgein_machines = forgein_machines + 1
                        if "nogrp" not in machine_errors:
                            machine_errors["nogrp"] = 1
                        else:
                            machine_errors["nogrp"] = machine_errors["nogrp"] + 1
                        continue
                    if 'cloud_name' not in r_dict:
                        logging.debug("Skipping resource with no cloud_name.")
                        forgein_machines = forgein_machines + 1
                        if "nocld" not in machine_errors:
                            machine_errors["nocld"] = 1
                        else:
                            machine_errors["nocld"] = machine_errors["nocld"] + 1
                        continue
                    if 'cs_host_id' not in r_dict:
                        logging.debug("Skipping resource with no host id.")
                        forgein_machines = forgein_machines + 1
                        if "nohost" not in machine_errors:
                            machine_errors["nohost"] = 1
                        else:
                            machine_errors["nohost"] = machine_errors["nohost"] + 1
                        continue
                        # check group name
                    if r_dict['group_name'] not in host_groups:
                        logging.debug("Skipping resource, group did not match any valid groups for this host: %s" % r_dict['group_name'])
                        forgein_machines = forgein_machines + 1
                        if "badgrp" not in machine_errors:
                            machine_errors["badgrp"] = 1
                        else:
                            machine_errors["badgrp"] = machine_errors["badgrp"] + 1
                        continue
                    # check cs host
                    if str(r_dict['cs_host_id']) != str(config.categories["SQL"]["csv2_host_id"]):
                        logging.debug("Skipping resource with bad cs_host_id: %s, should be %s" % (r_dict['cs_host_id'], config.categories["SQL"]["csv2_host_id"]))
                        forgein_machines = forgein_machines + 1
                        if "badgrp" not in machine_errors:
                            machine_errors["badgrp"] = 1
                        else:
                            machine_errors["badgrp"] = machine_errors["badgrp"] + 1
                        continue
                    # check cloud name
                    if r_dict['cloud_name'] not in host_groups[r_dict['group_name']]:
                        logging.debug("Skipping resource with cloud name that is invalid for group")
                        forgein_machines = forgein_machines + 1
                        if "badcld" not in machine_errors:
                            machine_errors["badcld"] = 1
                        else:
                            machine_errors["badcld"] = machine_errors["badcld"] + 1
                        continue


                    if "Start" in r_dict:
                        r_dict["Start"] = str(r_dict["Start"])
                    r_dict = trim_keys(r_dict, resource_attributes)
                    r_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=r_dict, config=config)
                    if unmapped:
                        logging.debug("attribute mapper found unmapped variables:")
                        logging.debug(unmapped)
                    logging.debug("Adding/updating machine %s", r_dict["name"])
                    r_dict["htcondor_host_id"] = config.local_host_id

                    # Check if this item has changed relative to the local cache, skip it if it's unchanged
                    # old inventory func
                    #if test_and_set_inventory_item_hash(inventory, r_dict["group_name"], r_dict["cloud_name"], r_dict["name"], r_dict, new_poll_time, debug_hash=(config.categories["condor_poller.py"]["log_level"]<20)):

                    # fill any missing keys in job_dict with None
                    filled_r_dict = fill_attributes(r_dict, resource_attributes, config)

                    if inventory_test_and_set_item_hash(ikey_names, filled_r_dict, inventory, new_poll_time, debug_hash=(config.categories["condor_poller.py"]["log_level"]<20)):
                        continue

                    try:
                        config.db_merge(RESOURCE, r_dict)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge machine entry, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break

                    try:
                        config.db_commit()
                    except Exception as exc:
                        logging.exception("Failed to commit machine updates, aborting cycle...")
                        logging.error(exc)
                        config.db_rollback()
                        abort_cycle = True
                        fail_commit = True
                        break

                if forgein_machines > 0:
                    logging.info("Ignored %s total forgein machines" % forgein_machines)
                    if "nogrp" in machine_errors:
                        logging.info("    %s ignored for missing group name" % machine_errors["nogrp"])
                    if "badgrp" in machine_errors:
                        logging.info("    %s ignored for bad group name" % machine_errors["badgrp"])
                    if "badcld" in machine_errors:
                        logging.info("    %s ignored for invalid cloud name" % machine_errors["badcld"])
                    if "nocld" in machine_errors:
                        logging.info("    %s ignored for missing cloud name" % machine_errors["nocld"])
                    if "nohost" in machine_errors:
                        logging.info("    %s ignored for missing host id" % machine_errors["nohost"])
                    if "badhost" in machine_errors:
                        logging.info("    %s ignored for missing host id" % machine_errors["badhost"])

                # Poll successful, update failure_dict accordingly
                for group in groups:
                    if group.get("htcondor_container_hostname") is not None and group["htcondor_container_hostname"] != "":
                        if group["htcondor_container_hostname"] == condor_host:
                             failure_dict.pop(group["group_name"], None)
                    else:
                        if group["htcondor_fqdn"] == condor_host:
                            failure_dict.pop(group["group_name"], None)

                           
                if abort_cycle:
                    config.db_rollback()
                    break

            if uncommitted_updates > 0:
                logging.info("Machine updates committed: %d" % uncommitted_updates)
            if fail_commit:
                logging.info("Previous had failed commit")
                time.sleep(config.categories["condor_poller.py"]["sleep_interval_machine"])
                continue

            if delete_cycle:
                # Check for deletes
                # New poller function:
                where_clause = "htcondor_host_id='%s'" % config.local_host_id
                rc, msg, rows = config.db_query(RESOURCE, where=where_clause)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, RESOURCE)

                #old inventory func
                #delete_obsolete_database_items('Machines', inventory, db_session, RESOURCE, 'name', poll_time=new_poll_time, failure_dict=failure_dict, condor_host=config.local_host_id)
                delete_cycle = False
            config.db_commit()
            cycle_count = cycle_count + 1
            if cycle_count > config.categories["condor_poller.py"]["delete_cycle_interval"]:
                delete_cycle = True
                cycle_count = 0
            
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            config.db_close()
            wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_machine"], config)
            

    except Exception as exc:
        logging.exception("Machine poller while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def machine_command_poller(arg_list):
    target_group =  arg_list[0]
    target_cloud = arg_list[1]
    pair = {
        "group_name": target_group,
        "cloud_name": target_cloud
    }
    multiprocessing.current_process().name = "Machine Command Poller - %s:%s" % (target_group, target_cloud)

    # database setup
    config = Config(sys.argv[1], ["condor_poller.py",  "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    Resource = "condor_machines"
    GROUPS = "csv2_groups"
    VM = "csv2_vms"
    CLOUD = "csv2_clouds"

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    cycle_count = 0
    last_heartbeat_time = 0


    loop_breaker = 0
    try:
        while True:
            if pair["cloud_name"] == "otter-test":
                loop_breaker = loop_breaker + 1

            config.db_open()
            last_heartbeat_time = log_heartbeat_message(last_heartbeat_time, "MACHINE COMMAND POLLER")
            config.refresh()

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                config.db_close()
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)
            local_condor = socket.gethostname()
            
            process_group_cloud_commands(pair, local_condor, config)
            
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                config.db_close()
                break
            config.db_close()
            wait_cycle(cycle_start_time, poll_time_history, config.categories["condor_poller.py"]["sleep_interval_command"], config)

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def worker_gsi_poller():
    multiprocessing.current_process().name = "Worker GSI Poller"

    config = Config(sys.argv[1], ["condor_poller.py", 'ProcessMonitor'], pool_size=6, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    last_heartbeat_time = 0

    try:
        while True:
            last_heartbeat_time = log_heartbeat_message(last_heartbeat_time, "WORKER GSI POLLER")
            config.db_open()
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                config.db_close()
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)


            condor_dict = get_condor_dict(config, logging)

            deleted = []
            condor = socket.gethostname()
            worker_cert = {}


            #if 'GSI_DAEMON_CERT' in htcondor.param or config.condor_poller["token_auth"]:
            if 'condor_worker_cert' in config.condor_poller and config.condor_poller['condor_worker_cert'] is not None and config.condor_poller['condor_worker_cert'] != "":
                try:
                    worker_cert['subject'], worker_cert['eol'] = get_gsi_cert_subject_and_eol(config.condor_poller['condor_worker_cert'])
                    worker_cert['cert'] = zip_base64(config.condor_poller['condor_worker_cert'])
                except:
                    logging.info("Unable to find condor_worker_cert from local configuration.")

                if worker_cert['eol']:
                    days_until_eol = (datetime.datetime(*time.gmtime(worker_cert['eol'])[:6]) - datetime.datetime(*time.gmtime()[:6])).days
                    condor_poller_config = config.categories['condor_poller.py']
                    
                    if days_until_eol <= config.get_config_by_category('GSI')['GSI']['cert_days_left_bad'] and \
                        condor_poller_config['sleep_interval_worker_gsi'] > condor_poller_config['sleep_interval_worker_expiring']:
                        condor_poller_config['sleep_interval_worker_gsi'] = condor_poller_config['sleep_interval_worker_expiring']
                
                try:
                    worker_cert['key'] = zip_base64(config.condor_poller['condor_worker_key'])
                    if worker_cert['key'] == 'unreadable':
                        worker_cert['eol'] = -999999
                except Exception as ex:
                    logging.info("Unable to find condor_worker_key from local configuration")
                    logging.info(ex)
            new_cwg = {}
            if worker_cert or config.condor_poller["token_auth"]:
                try:
                    if worker_cert and config.condor_poller["token_auth"]:
                        new_cwg = {
                            "htcondor_fqdn": condor,
                            "htcondor_host_id": config.local_host_id,
                            "worker_dn": worker_cert['subject'],
                            "worker_eol":  worker_cert['eol'],
                            "worker_cert": worker_cert['cert'],
                            "worker_key": worker_cert['key'],
                            "auth_token": zip_base64(config.condor_poller["token_path"])
                        }
                    elif worker_cert and not config.condor_poller["token_auth"]:
                        new_cwg = {
                            "htcondor_fqdn": condor, 
                            "htcondor_host_id": config.local_host_id,
                            "worker_dn": worker_cert['subject'],
                            "worker_eol":  worker_cert['eol'],
                            "worker_cert": worker_cert['cert'],
                            "worker_key": worker_cert['key']
                        }
                    elif not worker_cert and config.condor_poller["token_auth"]:
                        new_cwg = {
                            "htcondor_fqdn": condor, 
                            "htcondor_host_id": config.local_host_id,
                            "auth_token": zip_base64(config.condor_poller["token_path"]),
                            "worker_dn": "",
                            "worker_eol": 0,
                            "worker_cert": "",
                            "worker_key": ""
                        }
                    #check to see if db row exists
                    where_clause = "htcondor_fqdn='%s'" % condor
                    rc, msg, cwg_rows = config.db_query('condor_worker_gsi', where=where_clause)
                    if len(cwg_rows) > 0:
                        #row exists in db, do an update
                        rc, msg = config.db_update('condor_worker_gsi', new_cwg)
                        if rc == 1:
                            logging.error(msg)
                            raise(Exception(msg))
                    else:
                        #row does not exist in db, do an insert
                        rc, msg = config.db_insert('condor_worker_gsi', new_cwg)
                        if rc == 1:
                            logging.error(msg)
                            raise(Exception(msg))
                    config.db_commit()

                    if 'subject' in worker_cert:
                        logging.info('Condor host: "%s", condor_worker_gsi inserted.' % condor)
                    else:
                        logging.info('Condor host: "%s", condor_worker_gsi (not configured) inserted.' % condor)

                except Exception as ex:
                    config.db_rollback()

                    if worker_cert['subject']:
                        logging.error('Condor host: "%s", condor_worker_gsi update failed, exception: %s' % (condor, ex))
                    else:
                        logging.error('Condor host: "%s", condor_worker_gsi (not configured) update failed, exception: %s' % (condor, ex))

            else:
                logging.warning('Condor host: "%s", GSI not enabled, nothing to do...' % condor)

            config.db_close()
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break

            wait_cycle(cycle_start_time, poll_time_history, config.categories['condor_poller.py']['sleep_interval_worker_gsi'], config)

    except Exception as exc:
        logging.exception("Worker GSI while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()



def condor_gsi_poller():
    multiprocessing.current_process().name = "Condor GSI Poller"

    config = Config(sys.argv[1], ["condor_poller.py", 'ProcessMonitor'], pool_size=6, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    last_heartbeat_time = 0


    try:
        while True:
            config.db_open()
            last_heartbeat_time = log_heartbeat_message(last_heartbeat_time, "CONDOR GSI POLLER")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                config.db_close()
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)


            condor = socket.gethostname()
            condor_cert = {}
            if 'GSI_DAEMON_CERT' in htcondor.param:
                condor_hostcert = htcondor.param['GSI_DAEMON_CERT']
            else:
                try:
                    condor_hostcert = config.condor_poller.get("condor_hostcert")
                except:
                    condor_hostcert = None

            if condor_hostcert:
                condor_cert['subject'], condor_cert['eol'] = get_gsi_cert_subject_and_eol(condor_hostcert)

            if condor_cert:
                if condor_cert['eol']:
                    days_until_eol = (datetime.datetime(*time.gmtime(condor_cert['eol'])[:6]) - datetime.datetime(*time.gmtime()[:6])).days
                    condor_poller_config = config.categories['condor_poller.py']
                    if days_until_eol <= config.get_config_by_category('GSI')['GSI']['cert_days_left_bad'] and \
                        condor_poller_config['sleep_interval_condor_gsi'] > condor_poller_config['sleep_interval_condor_expiring']:
                        condor_poller_config['sleep_interval_condor_gsi'] = condor_poller_config['sleep_interval_condor_expiring']
                
                try:
                    config.db_execute('update csv2_groups set %s,htcondor_gsi_eol=%d where htcondor_fqdn="%s";' % (if_null(condor_cert['subject'], col='htcondor_gsi_dn'), condor_cert['eol'], condor))
                    config.db_commit()

                    if condor_cert['subject']:
                        logging.info('Condor host: "%s" GSI updated.' % condor)
                    else:
                        logging.info('Condor host: "%s" GSI (not configured) updated.' % condor)

                except Exception as ex:
                    config.db_rollback()

                    if condor_cert['subject']:
                        logging.error('Condor host: "%s" GSI update failed, exception: %s' % (condor, ex))
                    else:
                        logging.error('Condor host: "%s",  GSI (not configured) update failed, exception: %s' % (condor, ex))

            else:
                try:
                    config.db_execute('update csv2_groups set htcondor_gsi_dn=NULL,htcondor_gsi_eol=0 where htcondor_fqdn="%s";' % condor) 
                    logging.warning('Unable to retrieve certificate')
                except Exception as ex:
                    logging.error('Condor host: "%s" GSI unset failed, exception: %s' % (condor, ex))

            config.db_rollback()

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break

            config.db_close()
            wait_cycle(cycle_start_time, poll_time_history, config.categories['condor_poller.py']['sleep_interval_condor_gsi'], config)

    except Exception as exc:
        logging.exception("Condor GSI while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def alias_auditor():
    multiprocessing.current_process().name = "VM Alias Auditor"

    config = Config(sys.argv[1], ["condor_poller.py", 'ProcessMonitor'], pool_size=6, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    last_heartbeat_time = 0
    #can probably be largely reduced in this poller since we only need enough info to check the alias and match it to the relevent VM
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", \
                           "Activity", "VMType", "MyCurrentTime", "EnteredCurrentState", "Cpus", \
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", \
                           "cloud_name", "cs_host_id", "condor_host", "flavor", "TotalDisk", "target_alias"]


    VMS = "csv2_vms"
    CLOUDS = "csv2_clouds"
    GROUPS = "csv2_groups"


    try:
        while True:
            config.db_open()
            last_heartbeat_time = log_heartbeat_message(last_heartbeat_time, "VM Alias Auditor")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            watchdog_send_heartbeat(config, os.getpid(), config.local_host_id)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                config.db_close()
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            # get VM list from database maybe just hostname and alias
            # get condor classads
            # check alias vs database entry
            config.db_open()
            #may want to restrict this query to have less fields for efficiency (should only need host and alias)
            rc, msg, rows = config.db_query(VMS)

            # it would be good to parse the vm results out into a hashed data structure (dictionary) for quick access doing the checks
            vm_dict = {}
            for vm in rows:
                vm_dict[vm["hostname"]] = vm["target_alias"]
                vm_dict[vm["hostname"] + "id"] = vm["vmid"]

            where_clause = "htcondor_host_id='%s'" % config.local_host_id
            rc, msg, groups = config.db_query(GROUPS, where=where_clause)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups: 
                if group.get("htcondor_container_hostname") is not None and group["htcondor_container_hostname"] != "":
                    condor_hosts_set.add(group["htcondor_container_hostname"])
                else:
                    condor_hosts_set.add(group["htcondor_fqdn"])
            for condor_host in condor_hosts_set:
                condor_session = htcondor.Collector(condor_host)
                # Retrieve machines.
                try:
                    condor_resources = condor_session.query(ad_type=htcondor.AdTypes.Startd, projection=resource_attributes)
                except Exception as exc:
                    logging.error("unable to retrieve condor classads:")
                    logging.error(exc)
                    break
                for classad in condor_resources:
                    condor_alias = classad["target_alias"]
                    if condor_alias == "None":
                        condor_alias = None
                    try:
                        csv2_alias = vm_dict[classad["Machine"]]
                    except:
                        # if we get here a VM is missing from the database but still exists in condor
                        # we will skip any action here because we need to wait for the openstack poller to put the VM info back in
                        logging.warning("VM detected in condor missing from csv2: %s   skipping alias update until machine exists in csv2..." % classad["Machine"])
                        continue
                    if condor_alias != csv2_alias:
                        logging.info("alias mismatch detected: %s : %s" % (classad["target_alias"], vm_dict[classad["Machine"]]))
                        split_host = classad["Machine"].split("--")
                        vm_rw = {
                            'group_name': split_host[0],
                            'cloud_name': split_host[1],
                            'target_alias': condor_alias,
                            'vmid': vm_dict[classad["Machine"] + "id"]
                        }
                        config.db_merge(VMS, vm_rw)
                        config.db_commit()

                    else:
                        logging.debug("no alias mismatch")

            time.sleep(300)
 

    except Exception as exc:
        logging.exception("VM Alias Auditor while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()


if __name__ == '__main__':

    process_ids = {
        'job':              job_poller,
        'machine_command':  [machine_command_poller, 'select distinct cc.group_name, cloud_name from csv2_clouds as cc left outer join csv2_groups as cg on cc.group_name = cg.group_name where htcondor_fqdn = "%s";' % socket.gethostname()],
        'machine':          machine_poller,
        'condor_gsi':       condor_gsi_poller,
        'worker_gsi':       worker_gsi_poller,
        'alias_auditor':    alias_auditor,
    }

    db_category_list = ["condor_poller.py", "ProcessMonitor", "general", "signal_manager"]
    watchdog_exemptions = [ "condor_gsi", "worker_gsi"] 

    #procMon = ProcessMonitor(config_params=db_category_list, pool_size=3, process_ids=process_ids, config_file=sys.argv[1], log_file="/var/log/cloudscheduler/condor_poller.log", log_level=20)
    procMon = ProcessMonitor(config_params=db_category_list, pool_size=3, process_ids=process_ids, config_file=sys.argv[1], log_key="condor_poller", watchdog_exemption_list=watchdog_exemptions)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()
    is_hostname_localhost = config.is_hostname_localhost()

    if is_hostname_localhost:
        logging.error("Hostname can not be localhost, exiting...")
        exit(1)
    
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))

    logging.info("**************************** starting condor poller - Running %s *********************************" % version)

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        signal.signal(signal.SIGTERM, terminate)
        while True:
            config.refresh()
            config.update_service_catalog()
            stop = check_pid(PID_FILE)
            procMon.check_processes(stop=stop)
            time.sleep(config.categories["ProcessMonitor"]["sleep_interval_main_long"])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")
    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()
