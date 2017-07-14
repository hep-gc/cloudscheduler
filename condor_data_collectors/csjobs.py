from multiprocessing import Process
import time
import htcondor
import redis
import json
import logging
import config


def setup_redis_connection():
    r = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db, password=config.redis_password)
    return r

def job_producer():

    job_data_key = config.job_data_key
    sleep_interval = config.job_collection_interval
    job_attributes = ["JobStatus", "RequestMemory", "GlobalJobId", "RequestDisk", "Requirements", "JobPrio", "Cmd", "ClusterId", "User", "VMInstanceType", "Iwd", "VMType", "VMNetwork", "VMName", "VMLoc", "VMAMI", "VMKeepAlive", "VMHighPriority", "VMMaximumPrice", "VMUserData", "VMAMIConfig", "CSMyProxyCredsName", "CSMyProxyServer", "CSMyProxyServerPort", "x509userproxysubject", "x509userproxy", "SUBMIT_x509userproxy", "VMJobPerCore"]
    # Thus far the attributes from this list that are available in my tests are: ClusterId, RequestDisk, User, Requirements, JobStatus, JobPrio, RequestMemory, Iwd, Cmd, GlobalJobId
    # Not in the list that seem to be returned always: FileSystemDomian, MyType, ServerTime, TargetType, 
    while(True):
        try:
            job_dict_list = []

            condor_s = htcondor.Schedd()
            job_list = condor_s.query(attr_list=job_attributes) 

            for job_ad in job_list:
                job_dict = dict(job_ad)
                if "Requirements" in job_dict:
                    job_dict['Requirements'] = str(job_dict['Requirements'])
                job_dict_list.append(job_dict)
            
            job_list = json.dumps(job_dict_list)
            redis_con = setup_redis_connection()
            logging.info("Setting condor-jobs in redis...")
            redis_con.set(job_data_key, job_list)

            time.sleep(sleep_interval)

        except Exception as e:
            logging.error(e)
            logging.error("Failure contacting condor or redis..")
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return



def job_command_consumer():
    job_commands_key = config.job_commands_key
    sleep_interval = config.command_sleep_interval
    
    while(True):
        try:
            redis_con = setup_redis_connection()
            command_string = redis_con.lpop(job_commands_key)
            if command_string is not None:
                command_dict = json.loads(command_string)
                command = command_dict["command"]
                if command == "set_job_hold":
                    job_id = command_dict["job_id"]
                    #if you don't supply it in a list format it seems to update all jobs
                    logging.info("Holding %s" % job_id)
                    s = htcondor.Schedd()
                    s.edit([job_id,], "JobStatus", "5")
                

            else:
                logging.info("No command in redis list, begining sleep interval...")
                time.sleep(sleep_interval)

        except Exception as e:
            logging.error("Failure connecting to redis or executing condor command, begining sleep interval...")
            logging.error(e)
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return

        

if __name__ == '__main__':
    
    logging.basicConfig(filename=config.job_log_file,level=logging.DEBUG)
    processes = []

    p_job_producer = Process(target=job_producer)
    p_command_consumer = Process(target=job_command_consumer)
    processes.append(p_job_producer)
    processes.append(p_command_consumer)
   

    # Wait for keyboard input to exit
    try:
        for process in processes:
            process.start()
        while(True):
            for process in processes:
                if not process.is_alive():
                    log.error("%s process died!" % process.name)
                    log.error("Restarting %s process...")
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



