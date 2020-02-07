import multiprocessing
import time
import logging
import signal
import socket
import os
import sys
import yaml

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, check_pid, terminate
from cloudscheduler.lib.schema import view_condor_host
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.htc_config import configure_htc
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    build_inventory_for_condor, \
    start_cycle, \
    wait_cycle
from cloudscheduler.lib.rpc_client import RPC

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient

import htcondor
import classad
import boto3
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


def _get_nova_client(session, region=None):
    nova = novaclient.Client("2", session=session, region_name=region, timeout=10)
    return nova

def _get_openstack_session(cloud):
    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
        return False
    if version == 2:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project)
    else:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project,
            user_domain=cloud.user_domain_name,
            project_domain_name=cloud.project_domain_name)
    if session is False:
        logging.error("Failed to setup session, skipping %s", cloud.cloud_name)
        if version == 2:
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s" %
                          (cloud.authurl, cloud.username, cloud.project))
        else:
            logging.error(
                "Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s" %
                (cloud.authurl, cloud.username, cloud.project, cloud.user_domain_name, cloud.project_domain_name))
    return session


def _get_openstack_session_v1_v2(auth_url, username, password, project, user_domain="Default", project_domain_name="Default"):
    authsplit = auth_url.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad openstack URL: %s, could not determine version, aborting session", auth_url)
        return False
    if version == 2:
        try:
            auth = v2.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                tenant_name=project)
            sess = session.Session(auth=auth, verify=config.categories["csmachines.py"]["cacerts"])
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s::%s" % (auth_url, exc))
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
            return False
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project,
                user_domain_name=user_domain,
                project_domain_name=project_domain_name)
            sess = session.Session(auth=auth, verify=config.categories["csmachines.py"]["cacerts"])
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess



def _get_ec2_session(cloud):
    return boto3.session.Session(region_name=cloud.region,
                                 aws_access_key_id=cloud.username,
                                 aws_secret_access_key=cloud.password)

def _get_ec2_client(session):
    return session.client('ec2')

# condor likes to return extra keys not defined in the projection
# this function will trim the extra ones so that we can use kwargs
# to initiate a valid table row based on the data returned
def trim_keys(dict_to_trim, key_list):
    keys_to_trim = []
    for key in dict_to_trim:
        if key not in key_list or isinstance(dict_to_trim[key], classad.classad.Value):
            keys_to_trim.append(key)
    for key in keys_to_trim:
        dict_to_trim.pop(key, None)
    return dict_to_trim

def machine_poller():
    multiprocessing.current_process().name = "Machine Poller"
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", \
                           "Activity", "VMType", "MyCurrentTime", "EnteredCurrentState", "Cpus", \
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", \
                           "cloud_name", "cs_host_id", "condor_host", "flavor", "TotalDisk"]

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), "SQL", "ProcessMonitor"], pool_size=3, refreshable=True, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])


    RESOURCE = config.db_map.classes.condor_machines
    CLOUDS = config.db_map.classes.csv2_clouds
    GROUPS = config.db_map.classes.csv2_groups

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

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, RESOURCE, 'name', debug_hash=(config.categories["csmachines.py"]["log_level"]<20))
        configure_htc(config, logging)
        config.db_open()
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                    condor_hosts_set.add(group.htcondor_container_hostname)
                else:
                    condor_hosts_set.add(group.htcondor_fqdn)

            # need to make a data structure so that we can verify the the polled machines actually fit into a valid grp-cloud
            # need to check:
            #       - group_name (in both group_name and machine)
            #       - cloud_name (only in machine?)
            host_groups = {}
            groups = db_session.query(GROUPS)
            for group in groups:
                cloud_list = []
                clouds = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group.group_name)
                for cloud in clouds:
                    cloud_list.append(cloud.cloud_name)
                host_groups[group.group_name] = cloud_list

            for condor_host in condor_hosts_set:
                logging.debug("Polling condor host: %s" % condor_host)
                forgein_machines = 0
                try:
                    condor_session = htcondor.Collector(condor_host)
                except Exception as exc:
                    logging.exception("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.error(exc)
                    continue

                #if not condor_inventory_built:
                #    build_inventory_for_condor(inventory, db_session, CLOUDS)
                #    condor_inventory_built = True

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
                        if group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                            if group.htcondor_fqdn == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]
                        else:
                            if group.htcondor_container_hostname == condor_host:
                                if group.group_name not in failure_dict:
                                    failure_dict[group.group_name] = 1
                                    fail_count = failure_dict[group.group_name]
                                else:
                                    failure_dict[group.group_name] = failure_dict[group.group_name] + 1
                                    fail_count = failure_dict[group.group_name]

                    logging.error("Failed to get machines from condor collector object, aborting poll on host %s" % condor_host)
                    logging.error(exc)
                    if fail_count > 3:
                        logging.critical("More than 3 consecutive failed polls on host: %s, Configuration error or condor issues" % condor_host)
                    continue

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
                    r_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=r_dict)
                    if unmapped:
                        logging.error("attribute mapper found unmapped variables:")
                        logging.error(unmapped)

                    # Check if this item has changed relative to the local cache, skip it if it's unchanged
                    if test_and_set_inventory_item_hash(inventory, r_dict["group_name"], r_dict["cloud_name"], r_dict["name"], r_dict, new_poll_time, debug_hash=(config.categories["csmachines.py"]["log_level"]<20)):
                        continue

                    logging.info("Adding/updating machine %s", r_dict["name"])
                    new_resource = RESOURCE(**r_dict)
                    try:
                        db_session.merge(new_resource)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge machine entry, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
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
                    if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                        if group.htcondor_container_hostname == condor_host:
                             failure_dict.pop(group.group_name, None)
                    else:
                        if group.htcondor_fqdn == condor_host:
                            failure_dict.pop(group.group_name, None)

                           
                if abort_cycle:
                    del condor_session
                    config.db_session.rollback()
                    break

            if 'db_session'in locals() and uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Machine updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.exception("Failed to commit machine updates, aborting cycle...")
                    logging.error(exc)
                    config.db_session.rollback()
                    time.sleep(config.categories["csmachines.py"]["sleep_interval_machine"])
                    continue

            if delete_cycle:
                # Check for deletes
                delete_obsolete_database_items('Machines', inventory, db_session, RESOURCE, 'name', poll_time=new_poll_time, failure_dict=failure_dict)
                delete_cycle = False
            config.db_session.commit()
            cycle_count = cycle_count + 1
            if cycle_count > config.categories["csmachines.py"]["delete_cycle_interval"]:
                delete_cycle = True
                cycle_count = 0
            
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            wait_cycle(cycle_start_time, poll_time_history, config.categories["csmachines.py"]["sleep_interval_machine"], config)

    except Exception as exc:
        logging.exception("Machine poller while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def command_poller():
    multiprocessing.current_process().name = "Command Poller"

    # database setup
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), "AMQP", "ProcessMonitor"], pool_size=3, refreshable=True, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    Resource = config.db_map.classes.condor_machines
    GROUPS = config.db_map.classes.csv2_groups
    VM = config.db_map.classes.csv2_vms
    CLOUD = config.db_map.classes.csv2_clouds
    JOB_SCHED = config.db_map.classes.csv2_job_schedulers

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]


    cycle_count = 0


    try:
        config.db_open()
        while True:
            logging.debug("Beginning command consumer cycle")
            config.refresh()

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                if group.htcondor_container_hostname is not None and group.htcondor_container_hostname != "":
                    condor_hosts_set.add(group.htcondor_container_hostname)
                else:
                    condor_hosts_set.add(group.htcondor_fqdn)

            uncommitted_updates = 0
            logging.debug(condor_hosts_set)
            for condor_host in condor_hosts_set:
                condor_rpc = None
                # check on agent satus every ~5 cycles
                if cycle_count >= 5:
                    try:
                        condor_rpc = RPC(config.categories["AMQP"]["host"], config.categories["AMQP"]["port"], config.categories["AMQP"]["queue_prefix_htc"] +"_" + condor_host, "csv2_htc_" + condor_host)
                    except Exception as exc:
                        logging.error("Failed to create condor RPC client, skipping...:")
                        logging.error(exc)
                        continue
                    command_dict = {
                        'command': "noop",
                    }
                    command_yaml = yaml.dump(command_dict)
                    logging.debug("Running noop for host %s" % (condor_host))
                    command_results = condor_rpc.call(command_yaml, timeout=30)
                    if command_results is None or command_results[0] != 0:
                        # command failed
                        if command_results == None:
                            # we got a timeout
                            # timeout on the call, agent problems or offline
                            logging.error("RPC call to host: %s timed out, agent offline or in error" % condor_host)

                            jsched = {
                                "htcondor_fqdn": condor_host,
                                "agent_status":  0
                            }
                            new_jsched = JOB_SCHED(**jsched)
                            js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                            if js.count()>0:
                                config.db_session.merge(new_jsched)
                                uncommitted_updates += 1
                            else:
                                config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                                config.db_session.merge(new_jsched)
                                uncommitted_updates += 1

                        logging.error("RPC noop failed on host: %s, agent offline or in error" % condor_host)

                        continue
                    else:
                        #it was successfull
                        jsched = {
                            "htcondor_fqdn": condor_host,
                            "agent_status":  1
                        }
                        new_jsched = JOB_SCHED(**jsched)
                        js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                        if js.count()>0:
                            config.db_session.merge(new_jsched)
                            uncommitted_updates += 1
                        else:
                            config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                            config.db_session.merge(new_jsched)
                            uncommitted_updates += 1

                master_type = htcondor.AdTypes.Master
                startd_type = htcondor.AdTypes.Startd

                # Query database for machines to be retired.
                abort_cycle = False
                for resource in db_session.query(view_condor_host).filter(view_condor_host.c.htcondor_fqdn==condor_host, or_(view_condor_host.c.retire>=1, view_condor_host.c.terminate>=1)):
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
                    #logging.debug("%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (resource.group_name, resource.cloud_name, resource.htcondor_fqdn, resource.vmid, resource.hostname, resource[5], resource[6], resource.retire, resource.retiring, resource.terminate, resource.machine))
                    # First check the slots to see if its time to terminate this machine

                    #check if retire flag set & a successful retire has happened  and  (htcondor_dynamic_slots<1 || NULL) and htcondor_partitionable_slots>0, issue condor_off and increment retire by 1.
                    if resource.retire >= 1:
                        if (resource[6] is None or resource[6]<1) and (resource[5] is None or resource[5]<1):
                            #check if terminate has already been set
                            if not resource[8] >= 1:
                              # set terminate=1
                              # need to get vm classad because we can't update via the view.
                              try:
                                  logging.info("slots are zero or null on %s, setting terminate, last updater: %s" % (resource.hostname, resource.updater))
                                  vm_row = db_session.query(VM).filter(VM.group_name==resource.group_name, VM.cloud_name==resource.cloud_name, VM.vmid==resource.vmid)[0]
                                  vm_row.terminate = 1
                                  vm_row.updater = str(get_frame_info() + ":t1")
                                  db_session.merge(vm_row)
                                  db_session.commit()
                                  #uncommitted_updates = uncommitted_updates + 1

                              except Exception as exc:
                                  # unable to get VM row error
                                  logging.exception(exc)
                                  logging.error("%s ready to be terminated but unable to locate vm_row" % resource.vmid)
                                  continue
                        if resource.retire >= 10:
                            continue


                    if config.categories["csmachines.py"]["retire_off"]:
                        logging.critical("Retires disabled, normal operation would retire %s" % resource.hostname)
                        continue


                    # check the retire time to see if it has been enough time since the last retire was issued
                    # if it's none we haven't issued a retire yet and can skip the check
                    if resource.retire_time is not None:
                        if int(time.time()) - resource.retire_time < config.categories["csmachines.py"]["retire_interval"]:
                            # if the time since last retire is less than the configured retire interval, continue
                            logging.debug("Resource has been retired recently... skipping for now.")
                            continue


                    logging.info("Retiring (%s) machine %s primary slots: %s dynamic slots: %s, last updater: %s" % (resource.retire, resource.machine, resource[5], resource[6], resource.updater))
                    try:
                        # Old code from before RPC
                        #if resource.terminate is not None and resource.machine is not "":
                        #    condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.machine)[0]
                        #else:
                        #    condor_classad = condor_session.query(master_type, 'regexp("%s", Name, "i")' % resource.hostname)[0]
                        #master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)
                        if condor_rpc is None:
                            try:
                                condor_rpc = RPC(config.categories["AMQP"]["host"], config.categories["AMQP"]["port"], config.categories["AMQP"]["queue_prefix_htc"] +"_" + condor_host, "csv2_htc_" + condor_host)
                            except Exception as exc:
                                logging.error("Failed to create condor RPC client, skipping...:")
                                logging.error(exc)
                                continue
                        command_dict = {
                            'command': "retire",
                            'machine': resource.machine,
                            'hostname': resource.hostname
                        }
                        command_yaml = yaml.dump(command_dict)
                        command_results = condor_rpc.call(command_yaml, timeout=30)
                        if command_results is None or command_results[0] != 0:
                            # command failed
                            if command_results == None:
                                # we got a timeout
                                # timeout on the call, agent problems or offline
                                logging.error("RPC call timed out, agent offline or in error: %s" % (condor_host))
                                logging.debug(condor_host)
                                jsched = {
                                    "htcondor_fqdn": condor_host,
                                    "agent_status":  0
                                }
                                new_jsched = JOB_SCHED(**jsched)
                                js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                                if js.count()>0:
                                    config.db_session.merge(new_jsched)
                                    uncommitted_updates += 1
                                else:
                                    config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                                    config.db_session.merge(new_jsched)
                                    uncommitted_updates += 1

                            logging.error("RPC retire failed for machine: %s//%s" % (resource.machine, resource.hostname))
                            #logging.error(command_results)
                            if command_results[0] == 2:
                                #condor error, report the failure
                                jsched = {
                                    "htcondor_fqdn": condor_host,
                                    "agent_status":  0
                                }
                                new_jsched = JOB_SCHED(**jsched)
                                js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                                if js.count()>0:
                                    config.db_session.merge(new_jsched)
                                    uncommitted_updates += 1
                                else:
                                    config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                                    config.db_session.merge(new_jsched)
                                    uncommitted_updates += 1

                            if command_results is not None:
                                logging.error(command_results[1])
                            continue
                        else:
                            #it was successfull
                            logging.debug("retire results: %s" % command_results[1])
                            jsched = {
                                "htcondor_fqdn": condor_host,
                                "agent_status":  1
                            }
                            new_jsched = JOB_SCHED(**jsched)
                            js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                            if js.count()>0:
                                config.db_session.merge(new_jsched)
                                uncommitted_updates += 1
                            else:
                                config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                                config.db_session.merge(new_jsched)
                                uncommitted_updates += 1
                        #get vm entry and update retire = 2
                        vm_row = db_session.query(VM).filter(VM.group_name==resource.group_name, VM.cloud_name==resource.cloud_name, VM.vmid==resource.vmid)[0]
                        vm_row.retire = vm_row.retire + 1
                        vm_row.updater = str(get_frame_info() + ":r+")
                        vm_row.retire_time = int(time.time())
                        db_session.merge(vm_row)
                        uncommitted_updates = uncommitted_updates + 1
                        if uncommitted_updates >= config.categories["csmachines.py"]["batch_commit_size"]:
                            try:
                                db_session.commit()
                                uncommitted_updates = 0
                            except Exception as exc:
                                logging.exception("Failed to commit batch of retired machines, aborting cycle...")
                                logging.error(exc)
                                abort_cycle = True
                                break

                    except Exception as exc:
                        logging.exception(exc)
                        logging.error("Failed to issue DaemonsOffPeacefull to machine: %s, hostname: %s missing classad or condor miscomunication." % (resource.machine, resource.hostname))
                        logging.debug(condor_host)
                        continue

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit retire machine, aborting cycle...")
                    logging.error(exc)
                    config.db_session.rollback()
                    time.sleep(config.categories["csmachines.py"]["sleep_interval_command"])
                    continue

            # Now do the same thing for vms that need to be terminated
            # Query view for list of vms to terminate
            # Get vm_row for terminate
            # issue terminate, update vm_row
            # invalidate classads related to that vm
            
            for condor_host in condor_hosts_set:
                master_list = []
                startd_list = []
                #get list of vm/machines from this condor host
                redundant_machine_list = db_session.query(view_condor_host).filter(view_condor_host.c.htcondor_fqdn == condor_host, view_condor_host.c.terminate >= 1)
                for resource in redundant_machine_list:
                    if resource[6] is not None:
                        if resource[5] is not None:
                            if resource.terminate == 1 and resource[6] >= 1 and resource[5] >=1:
                                logging.info("VM still has active slots, skipping terminate on %s" % resource.vmid)
                                continue


                    # we need the relevent vm row to check if its in manual mode and if not, terminate and update termination status
                    try:
                        vm_row = db_session.query(VM).filter(VM.group_name == resource.group_name, VM.cloud_name == resource.cloud_name, VM.vmid == resource.vmid)[0]
                    except Exception as exc:
                        logging.error("Unable to retrieve VM row for vmid: %s, skipping terminate..." % resource.vmid)
                        continue
                    if vm_row.manual_control == 1:
                        logging.info("VM %s under manual control, skipping terminate..." % resource.vmid)
                        continue


                    # Get session with hosting cloud.
                    cloud = db_session.query(CLOUD).filter(
                        CLOUD.group_name == vm_row.group_name,
                        CLOUD.cloud_name == vm_row.cloud_name).first()

                    if cloud.cloud_type == "openstack":
                        session = _get_openstack_session(cloud)
                        if session is False:
                            continue
                     
                        if config.categories["csmachines.py"]["terminate_off"]:
                            logging.critical("Terminates disabled, normal operation would terminate %s" % vm_row.hostname)
                            continue

                        # terminate the vm
                        nova = _get_nova_client(session, region=cloud.region)
                        try:
                            # may want to check for result here Returns: An instance of novaclient.base.TupleWithMeta so probably not that useful
                            vm_row.terminate = vm_row.terminate + 1
                            old_updater = vm_row.updater
                            vm_row.updater = str(get_frame_info() + ":t+")

                            try:
                                nova.servers.delete(vm_row.vmid)
                            except novaclient.exceptions.NotFound:
                                logging.error("VM not found on cloud, deleting vm entry %s" % vm_row.vmid)
                                db_session.delete(vm_row)
                                uncommitted_updates = uncommitted_updates+1
                                if uncommitted_updates > 10:
                                    try:
                                        db_session.commit()
                                        uncomitted_updates = 0
                                    except Exception as exc:
                                        logging.exception("Failed to commit vm delete, aborting cycle...")
                                        logging.error(exc)
                                        abort_cycle = True
                                        break
                                continue #skip rest of logic since this vm is gone anywheres 
                                    

                            except Exception as exc:
                                logging.error("Unable to delete vm, vm doesnt exist or openstack failure:")
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                logging.error(exc_type)
                                logging.error(exc)
                                continue
                            logging.info("VM Terminated(%s): %s primary slots: %s dynamic slots: %s, last updater: %s" % (vm_row.terminate, vm_row.hostname, vm_row.htcondor_partitionable_slots, vm_row.htcondor_dynamic_slots, old_updater))
                            db_session.merge(vm_row)
                            # log here if terminate # /10 = remainder zero
                            if vm_row.terminate %10 == 0:
                                logging.critical("%s failed terminates on %s user action required" % (vm_row.terminate - 1, vm_row.hostname))
                        except Exception as exc:
                            logging.error("Failed to terminate VM: %s, terminates issued: %s" % (vm_row.hostname, vm_row.terminate - 1))
                            logging.error(exc)

                        # Now that the machine is terminated, we can speed up operations by invalidating the related classads
                        if resource.machine is not None:
                            logging.info("Removing classads for machine %s" % resource.machine)
                        else:
                            logging.info("Removing classads for machine %s" % resource.hostname)
                        try:
                            if condor_rpc is None:
                                try:
                                    condor_rpc = RPC(config.categories["AMQP"]["host"], config.categories["AMQP"]["port"], config.categories["AMQP"]["queue_prefix_htc"] +"_" + condor_host, "csv2_htc_" + condor_host)
                                except Exception as exc:
                                    logging.error("Failed to create condor RPC client, skipping...:")
                                    logging.error(exc)
                                    continue
                            command_dict = {
                                'command': "invalidate",
                                'machine': resource.machine,
                                'hostname': resource.hostname
                            }
                            command_yaml = yaml.dump(command_dict)
                            command_results = condor_rpc.call(command_yaml, timeout=30)
                            if command_results is None or command_results[0] != 0:
                                # command failed
                                if command_results is None:
                                    # timeout on the call, agent problems or offline
                                    logging.error("RPC call timed out, agent offline or in error")
                                    jsched = {
                                        "htcondor_fqdn": condor_host,
                                        "agent_status": 0 
                                    }
                                    new_jsched = JOB_SCHED(**jsched)
                                    js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                                    if js.count()>0:
                                        config.db_session.merge(new_jsched)
                                        uncommitted_updates += 1
                                    else:
                                        config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                                        config.db_session.merge(new_jsched)
                                        uncommitted_updates += 1
                                    continue
                                # if we get here the command successfully reached the agent but something failed on the condor side
                                jsched = {
                                    "htcondor_fqdn": condor_host,
                                    "agent_status":  1
                                }
                                new_jsched = JOB_SCHED(**jsched)
                                js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                                if js.count()>0:
                                    config.db_session.merge(new_jsched)
                                    uncommitted_updates += 1
                                else:
                                    config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                                    config.db_session.merge(new_jsched)
                                 
                                logging.error("RPC invalidate failed for machine: %s//%s" % (resource.machine, resource.hostname))
                                if command_results is not None:
                                    logging.error(command_results[1])
                                continue
                            else:
                                #it was successfull
                                logging.debug("retire results: master: %s  startd: %s" % (command_results[1], command_results[2]))
                                jsched = {
                                    "htcondor_fqdn": condor_host,
                                    "agent_status":  1
                                }
                                new_jsched = JOB_SCHED(**jsched)
                                js = config.db_session.query(JOB_SCHED).filter(JOB_SCHED.htcondor_fqdn==condor_host)
                                if js.count()>0:
                                    config.db_session.merge(new_jsched)
                                    uncommitted_updates += 1
                                else:
                                    config.db_session.execute('insert into csv2_job_schedulers (htcondor_fqdn) values("%s")' % condor_host)
                                    config.db_session.merge(new_jsched)
                                    uncommitted_updates += 1

                            #if resource.machine is not None and resource.machine is not "":
                            #    condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.machine)[0]
                            #else:
                            #    condor_classad = condor_session.query(master_type, 'regexp("%s", Name, "i")' % resource.hostname)[0]
                            #master_list.append(condor_classad)

                            # this could be a list of adds if a machine has many slots
                            #condor_classads = condor_session.query(startd_type, 'Machine=="%s"' % resource.hostname)
                            #for classad in condor_classads:
                            #    startd_list.append(classad)
                        #except IndexError as exc:
                        #    pass
                        except Exception as exc:
                            logging.error("RPC invalidate failed...")
                            logging.error(exc)
                            abort_cycle = True
                            break

                    elif cloud.cloud_type == "amazon":
                        if config.categories["csmachines.py"]["terminate_off"]:
                            logging.critical("Terminates disabled, normal operation would terminate %s" % vm_row.hostname)
                            continue
                        #terminate the vm
                        amz_session = _get_ec2_session(cloud)
                        amz_client = _get_ec2_client(amz_session)
                        try:
                            vm_row.terminate = vm_row.terminate + 1
                            old_updater = vm_row.updater
                            vm_row.updater = str(get_frame_info() + ":t+")
                            #destroy amazon vm, first we'll need to check if its a reservation
                            if vm_row.vmid[0:3].lower() == "sir":
                                #its a reservation just delete it and destroy the vm
                                # not sure what the difference between a client and connection from csv1 is but there is more work to be done here
                                #
                                # need the command to remove reservation:
                                # cancel_spot_instance_requests(list_of_request_ids)
                                #
                                # need to terminate request, and possible image if instance_id isn't empty
                                try:
                                    logging.info("Canceling amazon spot price request: %s" % vm_row.vmid)
                                    amz_client.cancel_spot_instance_requests(SpotInstanceRequestIds=[vm_row.vmid])
                                    if vm_row.instance_id is not None:
                                        #spot price vm running need to terminate it:
                                        logging.info("Terminating amazon vm: %s" % vm_row.instance_id)
                                        amz_client.terminate_instances(InstanceIds=[vm_row.instance_id])
                                except Exception as exc:
                                    logging.error("Unable to terminate %s due to:" % vm_row.vmid)
                                    logging.error(exc)
                            else:
                                #its a regular instance and just terminate it
                                logging.info("Terminating amazon vm: %s" % vm_row.vmid)
                                amz_client.terminate_instances(InstanceIds=[vm_row.vmid])
                        except Exception as exc:
                            logging.error("Unable to terminate %s due to:" % vm_row.vmid)
                            logging.error(exc)


                    else:
                        # Other cloud types will need to be implemented here to terminate any vms not from openstack
                        logging.info("Vm not from openstack, or amazon cloud, skipping...")
                        continue
                if uncommitted_updates > 0:
                    try:
                        db_session.commit()
                    except Exception as exc:
                        logging.exception("Failed to commit retire machine, aborting cycle...")
                        logging.error(exc)
                        config.db_session.rollback()
                        time.sleep(config.categories["csmachines.py"]["sleep_interval_command"])
                        continue

                if abort_cycle:
                    abort_cycle = False
                    continue

                # Execute condor_advertise to remove classads.
                #if startd_list:
                #    startd_advertise_result = condor_session.advertise(startd_list, "INVALIDATE_STARTD_ADS")
                #    logging.info("condor_advertise result for startd ads: %s", startd_advertise_result)

                #if master_list:
                #    master_advertise_result = condor_session.advertise(master_list, "INVALIDATE_MASTER_ADS")
                #    logging.info("condor_advertise result for master ads: %s", master_advertise_result)

            logging.debug("Completed command consumer cycle")
            cycle_count = cycle_count + 1
            # Every ~5 cycles check
            if cycle_count > 5:
                cycle_count = 0

            
            try:
                config.db_session.commit()
            except Exception as exc:
                logging.error("Error during final commit, likely that a vm was removed from database before final terminate update was comitted..")
                logging.exception(exc)

            if 'db_session'in locals():
                del db_session
            
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            wait_cycle(cycle_start_time, poll_time_history, config.categories["csmachines.py"]["sleep_interval_command"], config)
            time.sleep(config.categories["csmachines.py"]["sleep_interval_command"])

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)




def service_registrar():
    multiprocessing.current_process().name = "Service Registrar"

    # database setup
    db_category_list = [os.path.basename(sys.argv[0]), "general", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, refreshable=True, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    SERVICE_CATALOG = config.db_map.classes.csv2_service_catalog

    service_fqdn = socket.gethostname()
    service_name = "csv2-machines"

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    config.db_open()
    while True:
        config.refresh()
        if not os.path.exists(PID_FILE):
            logging.info("Stop set, exiting...")
            break

        service_dict = {
            "service":             service_name,
            "fqdn":                service_fqdn,
            "last_updated":        None,
            "flag_htcondor_allow": 1,
            "yaml_attribute_name": "cs_condor_remote_machine_poller"
        }
        service = SERVICE_CATALOG(**service_dict)
        try:
            config.db_session.merge(service)
            config.db_session.commit()
        except Exception as exc:
            logging.exception("Failed to merge service catalog entry, aborting...")
            logging.error(exc)
            return -1
        wait_cycle(cycle_start_time, poll_time_history, config.categories["general"]["sleep_interval_registrar"], config)

    return -1




if __name__ == '__main__':

    process_ids = {
        'command':    command_poller,
        'machine':    machine_poller,
        'registrar':  service_registrar,
    }

    db_category_list = [os.path.basename(sys.argv[0]), "ProcessMonitor", "general", "signal_manager"]

    procMon = ProcessMonitor(config_params=db_category_list, pool_size=333, process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))

    logging.info("**************************** starting cscollector - Running %s *********************************" % version)

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        signal.signal(signal.SIGTERM, terminate)
        while True:
            config.refresh()
            stop = check_pid(PID_FILE)
            procMon.check_processes(stop=stop)
            time.sleep(config.categories["ProcessMonitor"]["sleep_interval_main_long"])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")
    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()
