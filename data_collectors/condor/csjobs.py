import multiprocessing
from multiprocessing import Process
import time
import copy
import logging
import re
import os
import sys
import gc

from cloudscheduler.lib.attribute_mapper import map_attributes
#from cloudscheduler.lib.csv2_config import Config
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    build_inventory_for_condor, \
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
        if key == "group_name":
            continue
        if key not in key_list or isinstance(dict_to_trim[key], classad._classad.Value):
            keys_to_trim.append(key)
    for key in keys_to_trim:
        dict_to_trim.pop(key, None)
    return dict_to_trim

def build_user_group_dict(db_list):
    user_group_dict = {}
    for entry in db_list:
        if user_group_dict.get(entry.username):
            user_group_dict[entry.username].append(entry.group_name)
        else:
            user_group_dict[entry.username] = [entry.group_name]
    return user_group_dict

def job_poller():
    multiprocessing.current_process().name = "Job Poller"
    job_attributes = ["TargetClouds", "JobStatus", "RequestMemory", "GlobalJobId", "HoldReason",
                      "RequestDisk", "RequestCpus", "RequestScratch", "RequestSwap", "Requirements",
                      "JobPrio", "ClusterId", "ProcId", "User", "VMInstanceType", "VMNetwork",
                      "VMImage", "VMKeepAlive", "VMMaximumPrice", "VMUserData", "VMJobPerCore",
                      "EnteredCurrentStatus", "QDate"]
    # Not in the list that seem to be always returned:
    # FileSystemDomian, MyType, ServerTime, TargetType
    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    fail_count = 0
    inventory = {}
    #delete_interval = config.delete_interval
    delete_cycle = True
    cycle_count = 0
    condor_inventory_built = False

    #Base = automap_base()
    #db_engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
    #    "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    #Base.prepare(db_engine, reflect=True)
    config = Config(os.path.basename(sys.argv[0]))

    JOB = config.db_map.classes.condor_jobs
    USER_GROUPS = config.db_map.classes.csv2_user_groups
    CLOUDS = config.db_map.classes.csv2_group_resources

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, JOB, 'global_job_id', debug_hash=(config.log_level<20))
        while True:
            #
            # Setup - initialize condor and database objects and build user-group list
            #
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            try:
                condor_session = htcondor.Schedd()
            except Exception as exc:
                fail_count += 1
                logging.exception("Failed to locate condor daemon, failures=%s, sleeping...:" % fail_count)
                logging.error(exc)
                time.sleep(config.sleep_interval_job)
                continue

            fail_count = 0

            config.db_open()
            db_session = config.db_session
        
            if not condor_inventory_built:
                build_inventory_for_condor(inventory, db_session, CLOUDS)
                condor_inventory_built = True

            db_user_grps = db_session.query(USER_GROUPS)
            if db_user_grps:
                user_group_dict = build_user_group_dict(list(db_user_grps))
            else:
                user_group_dict = {}

            # Retrieve jobs.
            
            logging.debug("getting job list from condor")
            try:
                job_list = condor_session.xquery(
                    projection=job_attributes
                    )
            except Exception as exc:
                # Due to some unknown issues with condor we've changed this to a hard reboot of the poller
                # instead of simpyl handling the error and trying again
                logging.error("Failed to get jobs from condor queue, aborting job poller")
                logging.error(exc)
                del condor_session
                config.db_close()
                del db_session
                exit(1)



            # Process job data & insert/update jobs in Database
            abort_cycle = False
            uncommitted_updates = 0
            for job_ad in job_list:
                job_dict = dict(job_ad)
                if "Requirements" in job_dict:
                    job_dict['Requirements'] = str(job_dict['Requirements'])
                    # Parse group_name out of requirements
                    try:
                        pattern = '(group_name is ")(.*?)(")'
                        grp_name = re.search(pattern, job_dict['Requirements'])
                        job_dict['group_name'] = grp_name.group(2)
                    except Exception as exc:
                        logging.error("No group name found in requirements expression... setting default.")
                        job_dict['group_name'] = config.default_job_group
                else:
                    logging.info("No requirements attribute found, likely not a csv2 job.. assigning default job group.")
                    job_dict['group_name'] = config.default_job_group

                job_dict = trim_keys(job_dict, job_attributes)
                job_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=job_dict)
                logging.debug(job_dict)
                if unmapped:
                    logging.error("attribute mapper found unmapped variables:")
                    logging.error(unmapped)

                # Check if this item has changed relative to the local cache, skip it if it's unchanged
                if test_and_set_inventory_item_hash(inventory, job_dict["group_name"], "-", job_dict["global_job_id"], job_dict, new_poll_time, debug_hash=(config.log_level<20)):
                    continue

                logging.info("Adding job %s", job_dict["global_job_id"])
                new_job = JOB(**job_dict)
                try:
                    db_session.merge(new_job)
                    uncommitted_updates += 1
                except Exception as exc:
                    logging.exception("Failed to merge job entry, aborting cycle...")
                    logging.error(exc)
                    abort_cycle = True
                    break

            if abort_cycle:
                del condor_session
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_job)
                continue

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Job updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.exception("Failed to commit new jobs, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_job)
                    continue

            if delete_cycle:
                # Check for deletes
                delete_obsolete_database_items('Jobs', inventory, db_session, JOB, 'global_job_id', poll_time=new_poll_time)
                delete_cycle = False

            del condor_session
            del job_list
            config.db_close()
            del db_session
            cycle_count = cycle_count + 1
            if cycle_count >= config.delete_cycle_interval:
                delete_cycle = True
                cycle_count = 0
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_job)

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        config.db_close()
        del db_session

def command_poller():
    multiprocessing.current_process().name = "Command Poller"
    #Make database engine
    #Base = automap_base()
    #db_engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
    #    "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
    #Base.prepare(db_engine, reflect=True)

    config = Config(os.path.basename(sys.argv[0]))
    Job = config.db_map.classes.condor_jobs

    try:
        while True:
            logging.info("Beginning command consumer cycle")
            try:
                condor_session = htcondor.Schedd()
            except Exception as exc:
                fail_count += 1
                logging.exception("Failed to locate condor daemon, failures=%s, sleeping...:" % fail_count)
                logging.error(exc)
                time.sleep(config.sleep_interval_command)
                continue

            fail_count = 0

            config.db_open()
            db_session = config.db_session

            #Query database for any entries that have a command flag
            abort_cycle = False
            uncommitted_updates = False
            for job in db_session.query(Job).filter(Job.hold_job_reason != None):
                logging.info("Holding job %s, reason=%s" % (job.global_job_id, job.hold_job_reason))
                local_job_id = job.global_job_id.split('#')[1]
                try:
                    condor_session.edit([local_job_id,], "JobStatus", "5")
                    condor_session.edit([local_job_id,], "HoldReason", '"%s"' % job.hold_job_reason)

                    job.job_status = 5
                    job.hold_job_reason = None
                    db_session.merge(job)
                    uncommitted_updates = True
                except Exception as exc:
                    logging.exception("Failed to hold job, rebooting command poller...")
                    logging.error(exc)
                    exit(1)

            if abort_cycle:
                del condor_session
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_command)
                continue

            if uncommitted_updates:
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit job changes, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_command)
                    continue

            logging.info("Completed command consumer cycle")
            del condor_session
            config.db_close()
            del db_session
            time.sleep(config.sleep_interval_command)

    except Exception as exc:
        logging.exception("Job poller while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()


if __name__ == '__main__':
    config = Config(os.path.basename(sys.argv[0]))

    logging.basicConfig(
        filename=config.log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-12s - %(levelname)s - %(message)s')

    logging.info("**************************** starting csjobs *********************************")

    processes = {}
    process_ids = {
        'command':            command_poller,
        'job':                job_poller,
        }

    # Wait for keyboard input to exit
    try:
        while True:
            for process in process_ids:
                if process not in processes or not processes[process].is_alive():
                    if process in processes:
                        logging.error("%s process died, restarting...", process)
                        del processes[process]
                    else:
                        logging.info("Restarting %s process", process)
                    processes[process] = Process(target=process_ids[process])
                    processes[process].start()
                    time.sleep(config.sleep_interval_main_short)
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process.name)
