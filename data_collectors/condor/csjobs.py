import multiprocessing
from multiprocessing import Process
import time
import logging
import socket

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
    job_attributes = ["GroupName", "TargetClouds", "JobStatus", "RequestMemory", "GlobalJobId",
                      "RequestDisk", "RequestCpus", "RequestScratch", "RequestSwap", "Requirements",
                      "JobPrio", "ClusterId", "ProcId", "User", "VMInstanceType", "VMNetwork",
                      "VMImage", "VMKeepAlive", "VMMaximumPrice", "VMUserData", "VMJobPerCore",
                      "EnteredCurrentStatus", "QDate"]
    # Not in the list that seem to be always returned:
    # FileSystemDomian, MyType, ServerTime, TargetType
    last_poll_time = 0
    while True:
        try:
            #
            # Setup - initialize condor and database objects and build user-group list
            #
            condor_s = htcondor.Schedd()
            Base = automap_base()
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
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
                #
                # check if there is a group_name
                # if not, try and assign one, if default is ambiguos ignore ad
                # if a group is found update job ad in condor before adding to database
                #
                logging.info("Checking group name...")
                job_user = job_dict["User"].split("@")[0]
                if job_dict.get("GroupName") is not None and user_group_dict.get(job_user) is not None:
                    # if there is a grp name check that it is a valid one.
                    # This looks confusing but it's just saying if the job group
                    # name is not in any of the user's groups
                    if not any(str(job_dict["GroupName"]) in grp for grp in user_group_dict.get(job_user)):
                        logging.info("Job ad: %s has invalid group_name, ignoring...",
                                     job_dict["GlobalJobId"])
                        # Invalid group name
                        # IGNORE
                        continue

                else:
                    # else if there is no group name try to assign one
                    # can also get here if the user_group list is empty
                    job_user = job_dict["User"].split("@")[0]
                    if not user_group_dict.get(job_user):
                        # User not registered to any groups
                        logging.info("User: %s not registered to any groups or unable "
                                     "to retrieve user groups, ignoring...", job_user)
                        continue
                    logging.info("Job ad: %s has no group_name, attemping to resolve...",
                                 job_dict["GlobalJobId"])

                    if len(user_group_dict[job_user]) == 1:
                        job_dict["GroupName"] = user_group_dict[job_user][0]
                        #UPDATE CLASSAD
                        cluster = job_dict["ClusterId"]
                        proc = job_dict["ProcId"]
                        expr = str(cluster) + "." + str(proc)
                        condor_s.edit([expr], "GroupName", str(user_group_dict[job_user][0]))
                    else:
                        #AMBIGUOUS GROUP NAME, IGNORE
                        logging.info("Could not automatically resolve group_name for: %s,"
                                     " ignoring... ", job_dict["GlobalJobId"])
                        continue

                job_dict = trim_keys(job_dict, job_attributes)
                job_dict = map_attributes(src="condor", dest="csv2", attr_dict=job_dict)

                logging.info("Adding job %s", job_dict["global_job_id"])
                new_job = Job(**job_dict)
                session.merge(new_job)
            session.commit()


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
                    job_dict = map_attributes(src="condor", dest="csv2", attr_dict=job_dict)
                    new_job = Job(**job_dict)
                    session.merge(new_job)
                session.commit()

            last_poll_time = new_poll_time

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
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
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
            session.commit()

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
    while True:
        # Setup condor classes and database connctions
        # this stuff may be able to be moved outside the while loop, but i think its
        # better to re-mirror the database each time for the sake on consistency.
        condor_s = htcondor.Schedd()
        Base = automap_base()
        local_hostname = socket.gethostname()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        session = Session(engine)
        #setup database objects
        Job = Base.classes.condor_jobs
        archJob = Base.classes.archived_condor_jobs

        # Clean up job ads
        condor_job_list = condor_s.query()
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
                session.merge(new_arch_job)

        session.commit()
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
