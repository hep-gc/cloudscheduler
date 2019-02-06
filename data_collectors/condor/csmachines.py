import multiprocessing
import time
import logging
import socket
import os
import sys

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor
from cloudscheduler.lib.schema import view_condor_host
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    build_inventory_for_condor, \
    start_cycle, \
    wait_cycle

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient

import htcondor
import classad
from sqlalchemy import create_engine
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
            sess = session.Session(auth=auth, verify=config.cacerts)
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
            sess = session.Session(auth=auth, verify=config.cacerts)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess

# condor likes to return extra keys not defined in the projection
# this function will trim the extra ones so that we can use kwargs
# to initiate a valid table row based on the data returned
def trim_keys(dict_to_trim, key_list):
    keys_to_trim = []
    for key in dict_to_trim:
        if key not in key_list or isinstance(dict_to_trim[key], classad._classad.Value):
            keys_to_trim.append(key)
    for key in keys_to_trim:
        dict_to_trim.pop(key, None)
    return dict_to_trim

def machine_poller():
    multiprocessing.current_process().name = "Machine Poller"
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", \
                           "Activity", "VMType", "MyCurrentTime", "EnteredCurrentState", "Cpus", \
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", "flavor", "TotalDisk"]

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]), pool_size=4)


    RESOURCE = config.db_map.classes.condor_machines
    CLOUDS = config.db_map.classes.csv2_clouds
    GROUPS = config.db_map.classes.csv2_groups

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    inventory = {}
    #delete_interval = config.delete_interval
    delete_cycle = False
    condor_inventory_built = False
    cycle_count = 0
    uncommitted_updates = 0

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, RESOURCE, 'name', debug_hash=(config.log_level<20))
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                if group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                    condor_hosts_set.add(group.htcondor_fqdn)
                else:
                    condor_hosts_set.add(group.htcondor_container_hostname)

            # need to make a data structure so that we can verify the the polled machines actually fit into a valid grp-cloud
            # need to check:
            #       - group_name (in both group_name and machine)
            #       - cloud_name (only in machine?)
            host_groups = {}
            for group in groups:
                cloud_list = []
                clouds = config.db_session.query(CLOUDS).filter(CLOUDS.group_name == group.group_name)
                for cloud in clouds:
                    cloud_list.append(cloud.cloud_name)
                host_groups[group.group_name] = cloud_list

            forgein_machines = 0
            for condor_host in condor_hosts_set:
                logging.debug("Polling condor host: %s" % condor_host)
                try:
                    condor_session = htcondor.Collector(condor_host)
                except Exception as exc:
                    logging.exception("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.error(exc)
                    continue

                if not condor_inventory_built:
                    build_inventory_for_condor(inventory, db_session, CLOUDS)
                    condor_inventory_built = True

                # Retrieve machines.
                try:
                    condor_resources = condor_session.query(
                        ad_type=htcondor.AdTypes.Startd,
                        projection=resource_attributes
                         )
                except Exception as exc:
                    # Due to some unknown issues with condor we've changed this to a hard reboot of the poller
                    # instead of simpyl handling the error and trying again
                    logging.error("Failed to get machines from condor collector object, aborting poll on host %s" % condor_host)
                    logging.error(exc)
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
                    if r_dict['group_name'] not in host_groups:
                        logging.debug("Skipping resource, group did not match any valid groups for this host")
                        forgein_machines = forgein_machines + 1
                        if "badgrp" not in machine_errors:
                            machine_errors["badgrp"] = 1
                        else:
                            machine_errors["badgrp"] = machine_errors["badgrp"] + 1
                        continue
                    mach_str = r_dict['Machine'].split("--")
                    # check group name from machine string
                    if mach_str[0] not in host_groups:
                        logging.debug("Skipping resource with bad group name in machine string")
                        forgein_machines = forgein_machines + 1
                        if "badgrp" not in machine_errors:
                            machine_errors["badgrp"] = 1
                        else:
                            machine_errors["badgrp"] = machine_errors["badgrp"] + 1
                        continue
                    # check cloud name form machine string
                    if mach_str[1] not in host_groups[r_dict['group_name']]:
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

                    r_dict["condor_host"] = condor_host

                    # Check if this item has changed relative to the local cache, skip it if it's unchanged
                    if test_and_set_inventory_item_hash(inventory, r_dict["group_name"], "-", r_dict["name"], r_dict, new_poll_time, debug_hash=(config.log_level<20)):
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
                    logging.info("Ignored %s forgein machines" % forgein_machines)
                    if "nogrp" in machine_errors:
                        logging.info("%s ignored for missing group name" % machine_errors["nogrp"])
                    if "badgrp" in machine_errors:
                        logging.info("%s ignored for bad group name" % machine_errors["badgrp"])
                    if "badcld" in machine_errors:
                        logging.info("%s ignored for invalid cloud name" % machine_errors["badcld"])

                           

                if abort_cycle:
                    del condor_session
                    config.db_close()
                    break

            if 'db_session'in locals() and uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Machine updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.exception("Failed to commit machine updates, aborting cycle...")
                    logging.error(exc)
                    config.db_close()
                    time.sleep(config.sleep_interval_machine)
                    continue

            if delete_cycle:
                # Check for deletes
                delete_obsolete_database_items('Machines', inventory, db_session, RESOURCE, 'name', poll_time=new_poll_time)
                delete_cycle = False
            config.db_close(commit=True)
            if 'db_session' in locals():
                del db_session
            cycle_count = cycle_count + 1
            if cycle_count > config.delete_cycle_interval:
                delete_cycle = True
                cycle_count = 0
            
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_machine)

    except Exception as exc:
        logging.exception("Machine poller while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def command_poller():
    multiprocessing.current_process().name = "Command Poller"

    # database setup
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]), pool_size=4)

    Resource = config.db_map.classes.condor_machines
    GROUPS = config.db_map.classes.csv2_groups
    VM = config.db_map.classes.csv2_vms
    CLOUD = config.db_map.classes.csv2_clouds


    try:
        while True:
            logging.debug("Beginning command consumer cycle")
            config.db_open()
            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                if group.htcondor_fqdn is not None and group.htcondor_fqdn != "":
                    condor_hosts_set.add(group.htcondor_fqdn)
                else:
                    condor_hosts_set.add(group.htcondor_container_hostname)
            uncommitted_updates = 0
            for condor_host in condor_hosts_set:
                try:
                    condor_session = htcondor.Collector(condor_host)
                except Exception as exc:
                    logging.exception("Failed to locate condor daemon, skipping...:")
                    logging.error(exc)
                    continue

                master_type = htcondor.AdTypes.Master
                startd_type = htcondor.AdTypes.Startd

                # Query database for machines to be retired.
                abort_cycle = False
                for resource in db_session.query(view_condor_host).filter(view_condor_host.c.htcondor_fqdn==condor_host, view_condor_host.c.retire>=1):
                    # Since we are querying a view we dont get an automapped object and instead get a 'result' tuple of the following format
                    #index=attribute
                    #0=group
                    #1=cloud
                    #2=htcondor_fqdn
                    #3=vmid
                    #4=hostname
                    #5=retireflag
                    #6=retiring flag
                    #7=terminate flag
                    #8=machine
                    # First check if we have already issued a retire & its retiring

                    if resource[5] >= 2 and resource[6] == 1:
                        #resource has already been retired, skip it
                        continue


                    logging.info("Retiring machine %s" % resource[8])
                    try:
                        if resource[7] is not None and resource[8] is not "":
                            condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource[8])[0]
                        else:
                            condor_classad = condor_session.query(master_type, 'regexp("%s", Name, "i")' % resource.hostname)[0]
                        master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)

                        #get vm entry and update retire = 2
                        vm_row = db_session.query(VM).filter(VM.group_name==resource[0], VM.cloud_name==resource[1], VM.vmid==resource[3])[0]
                        vm_row.retire = vm_row.retire + 1
                        vm_row.updater = get_frame_info()
                        db_session.merge(vm_row)
                        uncommitted_updates = uncommitted_updates + 1
                        if uncommitted_updates >= config.batch_commit_size:
                            try:
                                db_session.commit()
                                uncommitted_updates = 0
                            except Exception as exc:
                                logging.exception("Failed to commit batch of retired machines, aborting cycle...")
                                logging.error(exc)
                                abort_cycle = True
                                break

                    except Exception as exc:
                        logging.error(exc)
                        logging.exception("Failed to issue DaemonsOffPeacefull to machine: %s, hostname: %s missing classad or condor miscomunication." % (resource[8], resource[4]))
                        continue

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit retire machine, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_command)
                    continue

            # Now do the same thing for vms that need to be terminated
            # Query view for list of vms to terminate
            # Get vm_row for terminate
            # issue terminate, update vm_row
            # invalidate classads related to that vm
            
            for condor_host in condor_hosts_set:
                # Query database for machines with no associated VM.
                master_list = []
                startd_list = []
                #get list of vm/machines from this condor host
                redundant_machine_list = db_session.query(view_condor_host).filter(view_condor_host.c.htcondor_fqdn == condor_host, view_condor_host.c.terminate >= 1)
                for resource in redundant_machine_list:

                    # we need the relevent vm row to check if its in manual mode and if not, terminate and update termination status
                    try:
                        vm_row = db_session.query(VM).filter(VM.group_name == resource.group_name, VM.cloud_name == resource.cloud_name, VM.vmid == resource.vmid)[0]
                    except Exception as exc:
                        logging.error("Unable retrieve VM row for vmid: %s, skipping terminate..." % resource.vmid)
                        continue
                    if vm_row.manual_control == 1:
                        logging.info("VM %s uner manual control, skipping terminate..." % resource.vmid)

                    # Get session with hosting cloud.
                    cloud = db_session.query(CLOUD).filter(
                        CLOUD.group_name == vm_row.group_name,
                        CLOUD.cloud_name == vm_row.cloud_name).first()
                    session = _get_openstack_session(cloud)
                    if session is False:
                        continue

                    if cloud.cloud_type == "openstack":

                        # terminate the vm
                        nova = _get_nova_client(session, region=cloud.region)
                        try:
                            # may want to check for result here Returns: An instance of novaclient.base.TupleWithMeta so probably not that useful
                            vm_row.terminate = vm_row.terminate + 1
                            vm_row.updater = get_frame_info()
                            nova.servers.delete(vm_row.vmid)
                            logging.info("VM Terminated: %s, updating db entry", (vm_row.hostname,))
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
                            if resource.machine is not None and resource.machine is not "":
                                condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.machine)[0]
                            else:
                                condor_classad = condor_session.query(master_type, 'regexp("%s", Name, "i")' % resource.hostname)[0]
                            master_list.append(condor_classad)

                            # this could be a list of adds if a machine has many slots
                            condor_classads = condor_session.query(startd_type, 'Machine=="%s"' % resource.hostname)
                            for classad in condor_classads:
                                startd_list.append(classad)
                        except IndexError as exc:
                            pass
                        except Exception as exc:
                            logging.exception("Failed to retrieve machine classads, aborting...")
                            logging.error(exc)
                            abort_cycle = True
                            break
                    else:
                        # Other cloud types will need to be implemented here to terminate any vms not from openstack
                        logging.info("Vm not from openstack cloud, skipping...")
                        continue

                if abort_cycle:
                    abort_cycle = False
                    continue

                # Execute condor_advertise to remove classads.
                if startd_list:
                    startd_advertise_result = condor_session.advertise(startd_list, "INVALIDATE_STARTD_ADS")
                    logging.info("condor_advertise result for startd ads: %s", startd_advertise_result)

                if master_list:
                    master_advertise_result = condor_session.advertise(master_list, "INVALIDATE_MASTER_ADS")
                    logging.info("condor_advertise result for master ads: %s", master_advertise_result)

            logging.debug("Completed command consumer cycle")
            del condor_session
            config.db_close(commit=True)
            del db_session
            time.sleep(config.sleep_interval_command)

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()




def service_registrar():
    multiprocessing.current_process().name = "Service Registrar"

    # database setup
    db_category_list = [os.path.basename(sys.argv[0]), "general"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=4)
    SERVICE_CATALOG = config.db_map.classes.csv2_service_catalog

    service_fqdn = socket.gethostname()
    service_name = "csv2-machines"

    while True:
        config.db_open()

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
            config.db_close(commit=True)
        except Exception as exc:
            logging.exception("Failed to merge service catalog entry, aborting...")
            logging.error(exc)
            return -1
        time.sleep(config.sleep_interval_registrar)

    return -1




if __name__ == '__main__':

    process_ids = {
        'command':    command_poller,
        'machine':    machine_poller,
        'registrar':  service_registrar,
    }

    procMon = ProcessMonitor(file_name=os.path.basename(sys.argv[0]), pool_size=4, orange_count_row='csv2_machines_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    logging.info("**************************** starting cscollector - Running %s *********************************" % version)

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        while True:
            procMon.check_processes()
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")
    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.join_all()
