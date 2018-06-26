import multiprocessing
from multiprocessing import Process
import time
import logging
import socket
import re

import job_config as config
from attribute_mapper.attribute_mapper import map_attributes

import htcondor
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
        if key not in key_list:
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

def job_producer():
    multiprocessing.current_process().name = "Poller"

    sleep_interval = config.collection_interval
    job_attributes = ["TargetClouds", "JobStatus", "RequestMemory", "GlobalJobId",
                      "RequestDisk", "RequestCpus", "RequestScratch", "RequestSwap", "Requirements",
                      "JobPrio", "ClusterId", "ProcId", "User", "VMInstanceType", "VMNetwork",
                      "VMImage", "VMKeepAlive", "VMMaximumPrice", "VMUserData", "VMJobPerCore",
                      "EnteredCurrentStatus", "QDate"]
    # Not in the list that seem to be always returned:
    # FileSystemDomian, MyType, ServerTime, TargetType
    last_poll_time = 0
    fail_count = 0
    while True:
        try:
            #
            # Setup - initialize condor and database objects and build user-group list
            #
            try:
                condor_s = htcondor.Schedd()
            except Exception as exc:
                fail_count = fail_count + 1
                logging.error("Unable to locate condor daemon, Failed %s times:" % fail_count)
                logging.error(exc)
                logging.error("Sleeping until next cycle...")
                time.sleep(sleep_interval)
                continue

            fail_count = 0

            Base = automap_base()
            engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
                "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            Job = Base.classes.condor_jobs
            User_Groups = Base.classes.csv2_user_groups
            session = Session(engine)

            db_user_grps = session.query(User_Groups)
            if db_user_grps:
                user_group_dict = build_user_group_dict(list(db_user_grps))
            else:
                user_group_dict = {}

            new_poll_time = time.time()

            #
            # Part 1 - Get new jobs
            #
            if last_poll_time == 0:
                #first poll since starting up, get everything
                job_list = condor_s.query(attr_list=job_attributes)
            else:
                #regular polling cycle: Get all new jobs
                # constraint='JobStatus=?=1 && QDate>=' + last_poll_time, attr_list=job_attributes
                job_list = condor_s.query(
                    constraint='QDate>=%d' % last_poll_time,
                    attr_list=job_attributes)

            #Process job data & Insert/update jobs in Database
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

                # Else there is no requirements and is likely not a job submitted for csv2
                # Set the default job group and continue
                else:
                    logging.info("No requirements attribute found, likely not a csv2 job.. assigning default job group.")
                    job_dict['group_name'] = config.default_job_group

                job_dict = trim_keys(job_dict, job_attributes)
                job_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=job_dict)
                if unmapped is not None:
                    logging.error("attribute mapper found unmapped variables:")
                    logging.error(unmapped)

                logging.info("Adding job %s", job_dict["global_job_id"])
                new_job = Job(**job_dict)
                try:
                    session.merge(new_job)
                except Exception as exc:
                    logging.error("Unable to merge job:")
                    logging.error(exc)
                    logging.error("Skipping for this cycle...")
            try:        
                session.commit()
            except Exception as exc:
                logging.error("Unable to commit database session")
                logging.error(exc)
                logging.error("Aborting cycle...")
                time.sleep(sleep_interval)
                continue


            session = Session(engine)
            #
            # Part 2 - Detect any job status changes
            #
            if last_poll_time != 0:
                # get all jobs who've had status changes since last poll excluding
                # brand new jobs since they would have been updated above
                status_changed_job_list = condor_s.query(
                    constraint='EnteredCurrentStatus>=%d && QDate<=%d' % (last_poll_time, last_poll_time),
                    attr_list=job_attributes)

                for job_ad in status_changed_job_list:
                    job_dict = dict(job_ad)
                    if "Requirements" in job_dict:
                        job_dict['Requirements'] = str(job_dict['Requirements'])
                    job_dict = trim_keys(job_dict, job_attributes)
                    job_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=job_dict)
                    if unmapped is not None:
                        logging.error("attribute mapper found unmapped variables:")
                        logging.error(unmapped)
                            
                    new_job = Job(**job_dict)
                    try:
                        session.merge(new_job)
                    except Exception as exc:
                        logging.error("Unable to merge updated job ads:")
                        logging.error(exc)
                        logging.error("setting new_poll_time to last_poll_time to repeat cycle")
                        new_poll_time = last_poll_time
                try:        
                    session.commit()
                    last_poll_time = new_poll_time
                except Exception as exc:
                    logging.error("Unable to commit database session")
                    logging.error(exc)
                    logging.error("Aborting cycle...")

            time.sleep(sleep_interval)

        except Exception as exc:
            logging.error(exc)
            logging.error("Failure contacting condor...")
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return


def job_command_consumer():
    multiprocessing.current_process().name = "Cmd Consumer"
    sleep_interval = config.command_sleep_interval

    while True:
        try:
            #Make database engine
            Base = automap_base()
            engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
                "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            Job = Base.classes.condor_jobs
            session = Session(engine)
            #Query database for any entries that have a command flag
            for job in session.query(Job).filter(Job.hold_job == 1):
                #execute condor hold on the jobs returned
                logging.info("Holding %s", job.global_job_id)
                try:
                    s = htcondor.Schedd()
                    local_job_id = job.global_job_id.split('#')[1]
                    s.edit([local_job_id,], "JobStatus", "5")
                    # update job so that it is held, need to finalize encoding here.
                    job.job_status = 5
                    # Null/0 normal, 1 means needs to be held, 2 means job has been held
                    job.hold_job = 2
                    session.merge(job)
                except:
                    logging.error("Failed to hold job %s", job.global_job_id)
                    continue
            #commit updates enteries
            try:        
                session.commit()
            except Exception as exc:
                logging.error("Unable to commit database session")
                logging.error(exc)
                logging.error("Aborting cycle...")

            logging.debug("No more jobs to hold, begining sleep interval...")
            time.sleep(sleep_interval)

        except Exception as exc:
            logging.error("Failure connecting to database or executing condor command,"
                          " begining sleep interval...")
            logging.error(exc)
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return

def cleanUp():
    multiprocessing.current_process().name = "Cleanup"
    fail_count = 0 
    while True:
        # Setup condor classes and database connctions
        # this stuff may be able to be moved outside the while loop, but i think its
        # better to re-mirror the database each time for the sake on consistency.
        try:
            condor_s = htcondor.Schedd()
        except Exception as exc:
            fail_count = fail_count + 1
            logging.error("Unable to locate condor daemon, Failed %s times:" % fail_count)
            logging.error(exc)
            logging.error("Sleeping until next cycle...")
            time.sleep(config.cleanup_sleep_interval)
            continue
        fail_count = 0
        Base = automap_base()
        local_hostname = socket.gethostname()
        engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        session = Session(engine)
        #setup database objects
        Job = Base.classes.condor_jobs
        archJob = Base.classes.archived_condor_jobs

        # Clean up job ads
        try:
            condor_job_list = condor_s.query()
        except Exception as exc:
            logging.error(exc)
            logging.error("Unable to query condor job list, aborting cycle...")
            logging.error("Sleeping until next cycle...")
            time.sleep(config.cleanup_sleep_interval)
            continue

        # this query asks for only jobs that contain the local hostname as part of their JobID
        db_job_list = session.query(Job).filter(Job.global_job_id.like("%" + local_hostname+ "%"))
        # loop through the condor data and make a list of GlobalJobId
        # then loop through db list checking if they are in the aforementioned list

        condor_name_list = []
        for ad in condor_job_list:
            ad_dict = dict(ad)
            condor_name_list.append(ad_dict['GlobalJobId'])
        for job in db_job_list:
            if job.global_job_id not in condor_name_list:
                #job is missing from condor, clean it up
                logging.info("Found Job missing from condor: %s, cleaning up.", job.global_job_id)
                job_dict = job.__dict__
                logging.info(job_dict)
                session.delete(job)
                # metadata not relevent to the job ad, must trim to init with kwargs
                job_dict.pop('_sa_instance_state', None)
                new_arch_job = archJob(**job_dict)
                try:
                    session.merge(new_arch_job)
                except Exception as exc:
                    logging.error("Unable to merge deleted job add, skipping for this cycle")

        try:        
            session.commit()
        except Exception as exc:
            logging.error("Unable to commit database session")
            logging.error(exc)
            logging.error("Aborting cycle...")
        time.sleep(config.cleanup_sleep_interval)

if __name__ == '__main__':
    logging.basicConfig(
        filename=config.log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-12s - %(levelname)s - %(message)s')
    processes = []
    # job polling proccess
    p_job_producer = Process(target=job_producer)
    processes.append(p_job_producer)
    # command executer proccess
    #p_command_consumer = Process(target=job_command_consumer)
    #processes.append(p_command_consumer)
    # cleanUp proccess
    p_cleanup = Process(target=cleanUp)
    processes.append(p_cleanup)

    # Wait for keyboard input to exit
    try:
        for process in processes:
            process.start()
        while True:
            for process in processes:
                if not process.is_alive():
                    logging.error("%s process died!", process.name)
                    logging.error("Restarting %s process...", process.name)
                    process.start()
                time.sleep(1)
            time.sleep(10)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process.name)
