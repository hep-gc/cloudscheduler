from multiprocessing import Process
import time
import htcondor
import json
import logging
import config
import socket

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

def job_producer():

    sleep_interval = config.job_collection_interval
    job_attributes = ["JobStatus", "RequestMemory", "GlobalJobId", "RequestDisk", "Requirements", "JobPrio", "Cmd", 
                      "ClusterId", "User", "VMInstanceType", "Iwd", "VMType", "VMNetwork", "VMName", "VMLoc", "VMAMI", 
                      "VMKeepAlive", "VMHighPriority", "VMMaximumPrice", "VMUserData", "VMAMIConfig",
                      "CSMyProxyCredsName", "CSMyProxyServer", "CSMyProxyServerPort", "x509userproxysubject", 
                      "x509userproxy", "SUBMIT_x509userproxy", "VMJobPerCore", "EnteredCurrentStatus", "QDate"]
    # Thus far the attributes from this list that are available in my tests are: ClusterId, RequestDisk, User, 
    # Requirements, JobStatus, JobPrio, RequestMemory, Iwd, Cmd, GlobalJobId
    # Not in the list that seem to be returned always: FileSystemDomian, MyType, ServerTime, TargetType, 
    last_poll_time = 0
    while(True):
        try:
            job_dict_list = []

            condor_s = htcondor.Schedd()
            new_poll_time = time.time()

            #
            # Part 1 - Get new jobs
            #
            if(last_poll_time == 0):
                #first poll since starting up, get everything
                job_list = condor_s.query(attr_list=job_attributes)
            else:
                #regular polling cycle: Get all new jobs
                    ## constraint='JobStatus=?=1 && QDate>=' + last_poll_time, attr_list=job_attributes
                job_list = condor_s.query(constraint='QDate>=%d' % last_poll_time, attr_list=job_attributes)
            

            #Process job data & Insert/update jobs in Database
            Base = automap_base()
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            Job = Base.classes.condor_jobs
            session = Session(engine)
            for job_ad in job_list:
                job_dict = dict(job_ad)
                if "Requirements" in job_dict:
                    job_dict['Requirements'] = str(job_dict['Requirements'])
                job_dict = trim_keys(job_dict, job_attributes)
                logging.info("Adding job %s" % job_dict["GlobalJobId"])
                new_job = Job(**job_dict)
                session.merge(new_job)
            session.commit()


            session = Session(engine)
            #   
            # Part 2 - Detect any job status changes
            #
            if(last_poll_time != 0):
                # get all jobs who've had status changes since last poll excluding brand new jobs since they would have been updated above
                status_changed_job_list = condor_s.query(constraint='EnteredCurrentStatus>=%d && QDate<=%d' % (last_poll_time, last_poll_time), attr_list=job_attributes)

                for job_ad in status_changed_job_list:
                    job_dict = dict(job_ad)
                    if "Requirements" in job_dict:
                        job_dict['Requirements'] = str(job_dict['Requirements'])
                    job_dict = trim_keys(job_dict, job_attributes)
                    new_job = Job(**job_dict)
                    session.merge(new_job)
                session.commit()

            
            last_poll_time = new_poll_time

            time.sleep(sleep_interval)

        except Exception as e:
            logging.error(e)
            logging.error("Failure contacting condor...")
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return


def job_command_consumer(testrun=False):
    sleep_interval = config.command_sleep_interval
    
    while(True):
        try:
            #Make database engine
            Base = automap_base()
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            Job = Base.classes.condor_jobs
            session = Session(engine)
            #Query database for any entries that have a command flag
            for job in session.query(Job).filter(Job.hold_job==1):
                #execute condor hold on the jobs returned
                logging.info("Holding %s" % job.GlobalJobId)
                try:
                    s = htcondor.Schedd()
                    local_job_id = job.GlobalJobId.split('#')[1]
                    s.edit([local_job_id,], "JobStatus", "5")
                    #update job so that it is held, need to finalize encoding here.
                    job.JobStatus=5
                    job.hold_job=2 # Null/0 normal, 1 means needs to be held, 2 means job has been held
                    session.merge(job)
                except:
                    logging.error("Failed to hold job %s" % job.GlobalJobId)
                    continue
            #commit updates enteries
            session.commit()

            logging.debug("No more jobs to hold, begining sleep interval...")
            time.sleep(sleep_interval)

        except Exception as e:
            logging.error("Failure connecting to database or executing condor command, begining sleep interval...")
            logging.error(e)
            if(testrun):
                return False
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return

def cleanUp():
    while(True):
        # Setup condor classes and database connctions
        # this stuff may be able to be moved outside the while loop, but i think its better to re-mirror the
        # database each time for the sake on consistency.
        condor_s = htcondor.Schedd()
        Base = automap_base()
        local_hostname = socket.gethostname()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        session = Session(engine)
        #setup database objects
        Job = Base.classes.condor_jobs
        archJob = Base.classes.archived_condor_jobs
        

        # Clean up job ads
        condor_job_list = condor_s.query()
        # this query asks for only jobs that contain the local hostname as part of their JobID
        db_job_list = session.query(Job).filter(Job.GlobalJobId.like("%" + local_hostname+ "%"))
        #loop through the condor data and make a list of GlobalJobId
        #then loop through db list checking if they are in the aforementioned list
        condor_name_list = []
        for ad in condor_job_list:
            ad_dict = dict(ad)
            condor_name_list.append(ad_dict['GlobalJobId'])
        for job in db_job_list:
            if job.GlobalJobId not in condor_name_list:
                #job is missing from condor, clean it up
                logging.info("Found Job missing from condor: %s, cleaning up." % job.GlobalJobId)
                job_dict = job.__dict__
                logging.info(job_dict)
                session.delete(job)
                job_dict.pop('_sa_instance_state', None) # metadata not relevent to the job ad, must trim to init with kwargs
                new_arch_job = archJob(**job_dict)
                session.merge(new_arch_job)


        session.commit()
        time.sleep(config.cleanup_sleep_interval) #sleep 2 mins, should probably add this as a config option
        

if __name__ == '__main__':
    
    logging.basicConfig(filename=config.job_log_file,level=logging.DEBUG)
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
        while(True):
            for process in processes:
                if not process.is_alive():
                    logging.error("%s process died!" % process.name)
                    logging.error("Restarting %s process...")
                    process.start()
                time.sleep(1)
            time.sleep(10)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s" % process.name)


