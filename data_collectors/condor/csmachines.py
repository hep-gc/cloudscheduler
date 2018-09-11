import multiprocessing
from multiprocessing import Process
import time
import copy
import logging
import socket
import os
import sys

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.csv2_config import Config
from cloudscheduler.lib.schema import view_redundant_machines
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    build_inventory_for_condor

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
                           "Activity", "VMType", "MyCurrentTime", "EnteredCurrentState", \
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", "flavor"]

    condor_host = socket.gethostname()
    fail_count = 0
    # Initialize database objects
    Base = automap_base()
    db_engine = create_engine(
        'mysql://%s:%s@%s:%s/%s' % (
            config.db_user,
            config.db_password,
            config.db_host,
            str(config.db_port),
            config.db_name
            )
        )
    Base.prepare(db_engine, reflect=True)
    RESOURCE = Base.classes.condor_machines
    CLOUDS = Base.classes.csv2_group_resources

    last_poll_time = 0
    inventory = {}
    #delete_interval = config.delete_interval
    delete_cycle = False
    condor_inventory_built = False
    cycle_count = 0

    try:
        inventory = get_inventory_item_hash_from_database(db_engine, RESOURCE, 'name', debug_hash=(config.log_level<20))
        while True:
            logging.info("Beginning machine poller cycle")

            try:
                condor_session = htcondor.Collector()
            except Exception as exc:
                fail_count += 1
                logging.exception("Failed to locate condor daemon, failures=%s, sleeping...:" % fail_count)
                logging.error(exc)
                time.sleep(config.sleep_interval_machine)
                continue

            fail_count = 0

            db_session = Session(db_engine)
            new_poll_time = int(time.time())

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
                logging.error("Failed to get machines from condor queue, aborting cycle")
                logging.error(exc)
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_job)
                continue

            abort_cycle = False
            uncommitted_updates = 0
            for resource in condor_resources:
                r_dict = dict(resource)
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
                db_session.close()
                time.sleep(config.sleep_interval_machine)
                continue

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Machine updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.exception("Failed to commit machine updates, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    db_session.close()
                    time.sleep(config.sleep_interval_machine)
                    continue

            if delete_cycle:
                # Check for deletes
                logging.info("Delete Cycle - checking for consistency")
                delete_obsolete_database_items('Machines', inventory, db_session, RESOURCE, 'name', poll_time=new_poll_time)
                delete_cycle = False

            logging.info("Completed machine poller cycle")
            last_poll_time = new_poll_time
            del condor_session
            db_session.close()
            cycle_count = cycle_count + 1
            if cycle_count > config.delete_cycle_interval:
                delete_cycle = True
                cycle_count = 0
            time.sleep(config.sleep_interval_machine)

    except Exception as exc:
        logging.exception("Machine poller while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()

def command_poller():
    multiprocessing.current_process().name = "Command Poller"
    condor_host = socket.gethostname()
    # database setup
    Base = automap_base()
    db_engine = create_engine(
        'mysql://%s:%s@%s:%s/%s' % (
            config.db_user,
            config.db_password,
            config.db_host,
            str(config.db_port),
            config.db_name
            )
        )
    Base.prepare(db_engine, reflect=True)
    Resource = Base.classes.condor_machines
    session = Session(db_engine)

    try:
        while True:
            logging.info("Beginning command consumer cycle")
            try:
                condor_session = htcondor.Collector()
            except Exception as exc:
                fail_count += 1
                logging.exception("Failed to locate condor daemon, failures=%s, sleeping...:" % fail_count)
                logging.error(exc)
                time.sleep(config.sleep_interval_command)
                continue

            fail_count = 0

            db_session = Session(db_engine)
            master_type = htcondor.AdTypes.Master
            startd_type = htcondor.AdTypes.Startd

            # Query database for machines to be retired.
            abort_cycle = False
            uncommitted_updates = False
            for resource in db_session.query(Resource).filter(Resource.condor_host == condor_host, Resource.retire_request_time > Resource.retired_time):
                logging.info("Retiring machine %s" % resource.name)
                try:
                    condor_classad = condor_session.query(master_type, 'Name=="%s"' % resource.name.split("@")[1])[0]
                    master_result = htcondor.send_command(condor_classad, htcondor.DaemonCommands.DaemonsOffPeaceful)

                    resource.retired_time = int(time.time())
                    db_session.merge(resource)
                    uncommitted_updates = True
                except Exception as exc:
                    logging.exception("Failed to retire machine, aborting cycle...")
                    logging.error(exc)
                    abort_cycle = True
                    break

            if abort_cycle:
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_command)
                continue

            if uncommitted_updates:
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit retire machine, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    db_session.close()
                    time.sleep(config.sleep_interval_command)
                    continue

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
                except Exception as exc:
                    logging.exception("Failed to retrieve machine classads, aborting cycle...")
                    logging.error(exc)
                    abort_cycle = True
                    break

            if abort_cycle:
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_command)
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
            db_session.close()
            time.sleep(config.sleep_interval_command)

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()


def cleanup_poller():
    multiprocessing.current_process().name = "Cleanup Poller"
    condor_host = socket.gethostname()
    fail_count = 0
    Base = automap_base()
    db_engine = create_engine(
        'mysql://%s:%s@%s:%s/%s' % (
            config.db_user,
            config.db_password,
            config.db_host,
            str(config.db_port),
            config.db_name
            )
        )
    Base.prepare(db_engine, reflect=True)
    session = Session(db_engine)
    #setup database objects
    Resource = Base.classes.condor_machines
    archResource = Base.classes.archived_condor_machines

    try:
        while True:
            logging.info("Beginning machine cleanup cycle")
            # Setup condor classes and database connections
            # this stuff may be able to be moved outside the while loop, but i think its better to
            # re-mirror the database each time for the sake on consistency.
            try:
                condor_session = htcondor.Collector()
            except Exception as exc:
                fail_count += 1
                logging.error("Failed to locate condor daemon, Failed %s times:" % fail_count)
                logging.error(exc)
                logging.error("Sleeping until next cycle...")
                time.sleep(config.sleep_interval_cleanup)
                continue

            fail_count = 0

            db_session = Session(db_engine)

            # Retrieve all valid machine IDs from condor.
            try:
                condor_machine_list = condor_session.query()
            except Exception as exc:
                logging.exception("Failed to query condor machine list, aborting cycle...")
                logging.error(exc)
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_cleanup)
                continue

            condor_machine_ids = {}
            for ad in condor_machine_list:
                condor_machine_ids[dict(ad)['Name']] = True

            # From the DB, retrieve machines that whose condor_host is the hostname for this collector.
            try:
                db_machine_list = db_session.query(Resource).filter(Resource.condor_host == condor_host)
            except Exception as ex:
                logging.exception("Failed to query DB machine list, aborting cycle...")
                logging.error(exc)
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_cleanup)
                continue

            # Scan DB machine list for items to delete.
            abort_cycle = False
            uncommitted_updates = False
            for machine in db_machine_list:
                if machine.name not in condor_machine_ids:
                    logging.info("DB machine missing from condor, archiving and deleting machine %s.", machine.name)
                    machine_temp = copy.deepcopy(machine.__dict__)
                    machine_temp.pop('_sa_instance_state', 'default')

                    logging.debug(machine_temp.keys())
                    try:
                        db_session.merge(archResource(**machine_temp))
                        uncommitted_updates = True
                    except Exception as exc:
                        logging.exception("Failed to archive completed machine, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break

                    try:
                        db_session.delete(machine)
                        uncommitted_updates = True
                    except Exception as exc:
                        logging.exception("Failed to delete completed machine, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_cleanup)
                continue

            if uncommitted_updates:
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit achives and deletions, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    db_session.close()
                    time.sleep(config.sleep_interval_cleanup)
                    continue

            logging.info("Completed machine cleanup cycle")
            del condor_session
            db_session.close()
            time.sleep(config.sleep_interval_cleanup)

    except Exception as exc:
        logging.exception("Machine cleanup while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()


if __name__ == '__main__':
    config = Config(os.path.basename(sys.argv[0]))

    logging.basicConfig(
        filename=config.log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-14s - %(levelname)s - %(message)s')

    logging.info("**************************** starting cscollector *********************************")

    processes = {}
    process_ids = {
#        'cleanup':            cleanup_poller,
        'command':            command_poller,
        'machine':            machine_poller,
        }

    # Wait for keyboard input to exit
    try:
        while True:
            for process in sorted(process_ids):
                if process not in processes or not processes[process].is_alive():
                    if process in processes:
                        logging.error("%s process died, restarting...", process)
                        del(processes[process])
                    else:
                        logging.info("Restarting %s process", process)
                    processes[process] = Process(target=process_ids[process])
                    processes[process].start()
                    time.sleep(config.sleep_interval_main_short)
            time.sleep(config.sleep_interval_main_long)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process.name)
