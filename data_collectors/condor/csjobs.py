import multiprocessing
from multiprocessing import Process
import time
import copy
import logging
import socket
import re
import os
import sys

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.csv2_config import Config

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
    key_list.append("group_name")
    for key in dict_to_trim:
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
    last_poll_time = 0
    fail_count = 0

    Base = automap_base()
    engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Job = Base.classes.condor_jobs
    User_Groups = Base.classes.csv2_user_groups

    try:
        while True:
            #
            # Setup - initialize condor and database objects and build user-group list
            #
            logging.info("Beginning job poller cycle")
            try:
                condor_session = htcondor.Schedd()
            except Exception as exc:
                fail_count += 1
                logging.exception("Failed to locate condor daemon, failures=%s, sleeping...:" % fail_count)
                logging.error(exc)
                time.sleep(config.sleep_interval_job)
                continue

            fail_count = 0

            db_session = Session(engine)
            new_poll_time = int(time.time())

            db_user_grps = db_session.query(User_Groups)
            if db_user_grps:
                user_group_dict = build_user_group_dict(list(db_user_grps))
            else:
                user_group_dict = {}

            # Retrieve jobs.
            if last_poll_time == 0:
                # First poll since starting up, get everything
                job_list = condor_session.query(
                    attr_list=job_attributes
                    )
            else:
                # Regular polling cycle, get updated jobs.
                job_list = condor_session.query(
                    constraint='EnteredCurrentStatus>=%d' % last_poll_time,
                    attr_list=job_attributes
                    )

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

                logging.info("Adding job %s", job_dict["global_job_id"])
                new_job = Job(**job_dict)
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
                db_session.close()
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
                    db_session.close()
                    time.sleep(config.sleep_interval_job)
                    continue

            logging.info("Completed job poller cycle")
            last_poll_time = new_poll_time
            del condor_session
            db_session.close()
            time.sleep(config.sleep_interval_job)

    except Exception as exc:
        logging.exception("Command consumer while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()

def command_poller():
    multiprocessing.current_process().name = "Command Poller"
    #Make database engine
    Base = automap_base()
    engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Job = Base.classes.condor_jobs

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

            db_session = Session(engine)

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
                    logging.exception("Failed to hold job, aborting cycle...")
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
                    logging.exception("Failed to commit job changes, aborting cycle...")
                    logging.error(exc)
                    del condor_session
                    db_session.close()
                    time.sleep(config.sleep_interval_command)
                    continue

            logging.info("Completed command consumer cycle")
            del condor_session
            db_session.close()
            time.sleep(config.sleep_interval_command)

    except Exception as exc:
        logging.exception("Job poller while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()

def cleanup_poller():
    multiprocessing.current_process().name = "Cleanup Poller"
    fail_count = 0

    Base = automap_base()
    local_hostname = socket.gethostname()
    engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    #setup database objects
    Job = Base.classes.condor_jobs
    archJob = Base.classes.archived_condor_jobs
    logging.info("entering main cleanup loop")

    try:
        while True:
            logging.info("Beginning job cleanup cycle")
            # Setup condor classes and database connctions
            # this stuff may be able to be moved outside the while loop, but i think its
            # better to re-mirror the database each time for the sake on consistency.
            logging.info("query schedd")
            try:
                condor_session = htcondor.Schedd()
            except Exception as exc:
                fail_count += 1
                logging.exception("Failed to locate condor daemon, failures=%s, sleeping...:" % fail_count)
                logging.error(exc)
                time.sleep(config.sleep_interval_cleanup)
                continue

            fail_count = 0

            db_session = Session(engine)

            # Retrieve all valid job IDs from condor.
            try:
                condor_job_list = condor_session.xquery()
            except Exception as exc:
                logging.exception("Failed to query condor job list, aborting cycle...")
                logging.error(exc)
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_cleanup)
                continue

            condor_job_ids = {}
            for ad in condor_job_list:
                condor_job_ids[dict(ad)['GlobalJobId']] = True

            # From the DB, retrieve jobs that contain the local hostname as part of their JobID
            try:
                db_job_list = db_session.query(Job).filter(Job.global_job_id.like("%" + local_hostname + "%"))
            except Exception as ex:
                logging.exception("Failed to query DB job list, aborting cycle...")
                logging.error(exc)
                del condor_session
                db_session.close()
                time.sleep(config.sleep_interval_cleanup)
                continue

            # Scan DB job list for items to delete.
            abort_cycle = False
            uncommitted_updates = False
            for job in db_job_list:
                if job.global_job_id not in condor_job_ids:
                    logging.info("DB job missing from condor, archiving and deleting job %s.", job.global_job_id)
                    job_temp = copy.deepcopy(job.__dict__)
                    job_temp.pop('_sa_instance_state', 'default')
                    
                    logging.debug(job_temp.keys())
                    try:
                        db_session.merge(archJob(**job_temp))
                        uncommitted_updates = True
                    except Exception as exc:
                        logging.exception("Failed to archive completed job, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break

                    try:
                        db_session.delete(job)
                        uncommitted_updates = True
                    except Exception as exc:
                        logging.exception("Failed to delete completed job, aborting cycle...")
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

            logging.info("Completed job cleanup cycle")
            del condor_session
            db_session.close()
            time.sleep(config.sleep_interval_cleanup)

    except Exception as exc:
        logging.exception("Job cleanup while loop exception, process terminating...")
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
        'cleanup':            cleanup_poller,
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
