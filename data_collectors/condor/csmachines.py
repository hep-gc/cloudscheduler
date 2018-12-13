import multiprocessing
from multiprocessing import Process
import time
import copy
import logging
import socket
import os
import sys

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.schema import view_redundant_machines
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    build_inventory_for_condor, \
    set_orange_count, \
    start_cycle, \
    wait_cycle

import htcondor
import classad
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

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
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", "flavor"]

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))


    RESOURCE = config.db_map.classes.condor_machines
    CLOUDS = config.db_map.classes.csv2_clouds
    GROUPS = config.db_map.classes.csv2_groups
    GROUP_DEFAULTS = config.db_map.classes.csv2_group_defaults

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    inventory = {}
    #delete_interval = config.delete_interval
    delete_cycle = False
    condor_inventory_built = False
    cycle_count = 0

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, RESOURCE, 'name', debug_hash=(config.log_level<20))
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                grp_def = config.db_session.query(GROUP_DEFAULTS).get(group.group_name)
                if grp_def.htcondor_name is not None and grp_def.htcondor_name == "":
                    condor_hosts_set.add(grp_def.htcondor_name)
                else:
                    condor_hosts_set.add(grp_def.htcondor_fqdn)

            for condor_host in condor_hosts_set:
                logging.info("Polling condor host: %s" % condor_host)
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
                uncommitted_updates = 0
                for resource in condor_resources:
                    r_dict = dict(resource)
                    if 'group_name' not in r_dict:
                        logging.info("Skipping resource with no group_name.")
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

                if abort_cycle:
                    del condor_session
                    config.db_close()
                    del db_session
                    break

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Machine updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.exception("Failed to commit machine updates, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_machine)
                    continue

            if delete_cycle:
                # Check for deletes
                delete_obsolete_database_items('Machines', inventory, db_session, RESOURCE, 'name', poll_time=new_poll_time)
                delete_cycle = False
            del condor_session
            config.db_close(commit=True)
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
    condor_host = socket.gethostname()
    # database setup
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    Resource = config.db_map.classes.condor_machines
    GROUPS = config.db_map.classes.csv2_groups
    GROUP_DEFAULTS = config.db_map.classes.csv2_group_defaults


    try:
        while True:
            logging.info("Beginning command consumer cycle")
            config.db_open()
            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                grp_def = config.db_session.query(GROUP_DEFAULTS).get(group.group_name)
                if grp_def.htcondor_name is not None and grp_def.htcondor_name == "":
                    condor_hosts_set.add(grp_def.htcondor_name)
                else:
                    condor_hosts_set.add(grp_def.htcondor_fqdn)
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
                for resource in db_session.query(Resource).filter(Resource.condor_host == condor_host, Resource.retire_request_time > Resource.retired_time):
                    logging.info("Retiring machine %s" % resource.name)
                    try:
                        condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.name.split("@")[1])[0]
                        master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)

                        resource.retired_time = int(time.time())
                        db_session.merge(resource)
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
                        logging.exception("Failed to issue DaemonsOffPeacefull to  machine: %s, skipping..." % resource.name)
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


            for condor_host in condor_hosts_set:
                # Query database for machines with no associated VM.
                master_list = []
                startd_list = []
                redundant_machine_list = db_session.query(view_redundant_machines).filter(view_redundant_machines.c.condor_host == condor_host)
                for resource in redundant_machine_list:
                    logging.info("Removing classads for machine %s" % resource.name)
                    try:
                        condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.name.split("@")[1])[0]
                        master_list.append(condor_classad)

                        condor_classad = condor_session.query(startd_type, 'Name=="%s"' % resource.name)[0]
                        startd_list.append(condor_classad)
                    except IndexError as exc:
                        pass
                    except Exception as exc:
                        logging.exception("Failed to retrieve machine classads, aborting...")
                        logging.error(exc)
                        abort_cycle = True
                        break

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

            logging.info("Completed command consumer cycle")
            del condor_session
            config.db_close(commit=True)
            del db_session
            time.sleep(config.sleep_interval_command)

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session


if __name__ == '__main__':
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))
    # Don't need db params as each process will create it's own config

    logging.basicConfig(
        filename=config.log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-14s - %(levelname)s - %(message)s')

    logging.info("**************************** starting cscollector *********************************")

    processes = {}
    process_ids = {
        'command':            command_poller,
        'machine':            machine_poller,
        }

    previous_count, current_count = set_orange_count(logging, config, 'csv2_machines_error_count', 1, 0)

    # Wait for keyboard input to exit
    try:
        while True:
            orange = False
            for process in sorted(process_ids):
                if process not in processes or not processes[process].is_alive():
                    if process in processes:
                        orange = True
                        logging.error("%s process died, restarting...", process)
                        del(processes[process])
                    else:
                        logging.info("Restarting %s process", process)
                    processes[process] = Process(target=process_ids[process])
                    processes[process].start()
                    time.sleep(config.sleep_interval_main_short)

            if orange:
                previous_count, current_count = set_orange_count(logging, config, 'csv2_machines_error_count', previous_count, current_count+1)
            else:
                previous_count, current_count = set_orange_count(logging, config, 'csv2_machines_error_count', previous_count, current_count-1)
               
            time.sleep(config.sleep_interval_main_long)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process)
