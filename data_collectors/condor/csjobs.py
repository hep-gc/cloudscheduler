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
from cloudscheduler.lib.db_config import Config
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
        if key == "group_name":
            continue
        if key not in key_list or isinstance(dict_to_trim[key], classad._classad.Value):
            keys_to_trim.append(key)
    for key in keys_to_trim:
        dict_to_trim.pop(key, None)
    return dict_to_trim

def job_poller():
    multiprocessing.current_process().name = "Job Poller"
    job_attributes = ["TargetClouds", "JobStatus", "RequestMemory", "GlobalJobId", "HoldReason",
                      "RequestDisk", "RequestCpus", "RequestScratch", "RequestSwap", "Requirements",
                      "JobPrio", "ClusterId", "ProcId", "User", "VMInstanceType", "VMNetwork",
                      "VMImage", "VMKeepAlive", "VMMaximumPrice", "VMUserData", "VMJobPerCore",
                      "EnteredCurrentStatus", "QDate", "HoldReasonCode", "HoldReasonSubCode", "LastRemoteHost" ]
    # Not in the list that seem to be always returned:
    # FileSystemDomian, MyType, ServerTime, TargetType
    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    fail_count = 0
    inventory = {}
    delete_cycle = True
    cycle_count = 0
    condor_inventory_built = False
    uncommitted_updates = 0

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    if config.default_job_group is None:
        config.default_job_group = ""

    JOB = config.db_map.classes.condor_jobs
    CLOUDS = config.db_map.classes.csv2_group_resources
    GROUPS = config.db_map.classes.csv2_groups

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, JOB, 'global_job_id', debug_hash=(config.log_level<20))
        while True:
            #
            # Setup - initialize condor and database objects and build user-group list
            #
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                condor_hosts_set.add(group.condor_central_manager)

            uncommitted_updates = 0
            for condor_host in condor_hosts_set:
                logging.info("Polling condor host: %s" % condor_host)
                try:
                    coll = htcondor.Collector(condor_host)
                    scheddAd = coll.locate(htcondor.DaemonTypes.Schedd, condor_host)
                    condor_session = htcondor.Schedd(scheddAd)

                except Exception as exc:
                    logging.exception("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.debug(exc)
                    continue


                if not condor_inventory_built:
                    build_inventory_for_condor(inventory, db_session, CLOUDS)
                    condor_inventory_built = True

                # Retrieve jobs.
                
                logging.debug("getting job list from condor")
                try:
                    job_list = condor_session.xquery(
                        projection=job_attributes
                        )
                except Exception as exc:
                    logging.error("Failed to get jobs from condor scheddd object, aborting poll on host: %s" % condor_host)
                    logging.error(exc)
                    continue

                # Process job data & insert/update jobs in Database
                abort_cycle = False
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
                    break

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
        config.db_close()
        del db_session

def command_poller():
    multiprocessing.current_process().name = "Command Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))
    Job = config.db_map.classes.condor_jobs
    GROUPS = config.db_map.classes.csv2_groups

    try:
        while True:
            logging.info("Beginning command consumer cycle")
            config.db_open()
            db_session = config.db_session
            groups = db_session.query(GROUPS)
            condor_hosts_set = set() # use a set here so we dont re-query same host if multiple groups have same host
            for group in groups:
                condor_hosts_set.add(group.condor_central_manager)

            uncommitted_updates = 0
            for condor_host in condor_hosts_set: 
                try:
                    coll = htcondor.Collector(condor_host)
                    scheddAd = coll.locate(htcondor.DaemonTypes.Schedd, condor_host)
                    condor_session = htcondor.Schedd(scheddAd)
                except Exception as exc:
                    logging.warning("Failed to locate condor daemon, skipping: %s" % condor_host)
                    logging.debug(exc)
                    continue

                #Query database for any entries that have a command flag
                abort_cycle = False
                for job in db_session.query(Job).filter(Job.hold_job_reason != None):
                    logging.info("Holding job %s, reason=%s" % (job.global_job_id, job.hold_job_reason))
                    local_job_id = job.global_job_id.split('#')[1]
                    try:
                        condor_session.edit([local_job_id,], "JobStatus", "5")
                        condor_session.edit([local_job_id,], "HoldReason", '"%s"' % job.hold_job_reason)

                        job.job_status = 5
                        job.hold_job_reason = None
                        db_session.merge(job)
                        uncommitted_updates = uncommitted_updates + 1

                        if uncommitted_updates >= config.batch_commit_size:
                            try:
                                db_session.commit()
                                uncommitted_updates = 0
                            except Exception as exc:
                                logging.exception("Failed to commit batch of job changes, aborting cycle...")
                                logging.error(exc)
                                abort_cycle = True
                                break

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

            if uncommitted_updates > 0:
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
            config.db_close()
            del db_session
            time.sleep(config.sleep_interval_command)

    except Exception as exc:
        logging.exception("Job poller while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()


if __name__ == '__main__':
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

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

    previous_count, current_count = set_orange_count(logging, config, 'csv2_jobs_error_count', 1, 0)

    # Wait for keyboard input to exit
    try:
        while True:
            orange = False
            for process in process_ids:
                if process not in processes or not processes[process].is_alive():
                    if process in processes:
                        orange = True
                        logging.error("%s process died, restarting...", process)
                        del processes[process]
                    else:
                        logging.info("Restarting %s process", process)
                    processes[process] = Process(target=process_ids[process])
                    processes[process].start()
                    time.sleep(config.sleep_interval_main_short)

            if orange:
                previous_count, current_count = set_orange_count(logging, config, 'csv2_jobs_error_count', previous_count, current_count+1)
            else:
                previous_count, current_count = set_orange_count(logging, config, 'csv2_jobs_error_count', previous_count, current_count-1)
               
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
