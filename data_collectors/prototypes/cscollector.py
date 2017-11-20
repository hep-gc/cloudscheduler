from multiprocessing import Process
import time
import htcondor
import redis
import json
import config
import logging

def setup_redis_connection():
    r = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db, password=config.redis_password)
    return r

def resources_producer(testrun=False, testfile=None):
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", "Activity", "VMType", "MycurrentTime", "EnteredCurrentState", "Start", "RemoteOwner", "SlotType", "TotalSlots"] 

    sleep_interval = config.machine_collection_interval
    collector_data_key = config.collector_data_key
    while(True):
        try:
            condor_resource_dict_list = []
            if not testrun:
                condor_c = htcondor.Collector()
                any_ad = htcondor.AdTypes.Any
                condor_resources = condor_c.query(ad_type=any_ad, constraint=True, projection=resource_attributes)
                for resource in condor_resources:
                    r_dict = dict(resource)
                    if "Start" in r_dict:
                        r_dict["Start"] = str(r_dict["Start"])
                    condor_resource_dict_list.append(r_dict)
                #logging.debug(condor_resource_dict_list)

            #For Unit Testing only:
            else:
                res_file = open(testfile, 'r')
                condor_string = res_file.read()[0:-1] #strip newline
                condor_resources = json.loads(condor_string)
                for resource in condor_resources:
                    r_dict = dict(resource)
                    if "Start" in r_dict:
                        r_dict["Start"] = str(r_dict["Start"])
                    condor_resource_dict_list.append(r_dict)

            condor_resources = json.dumps(condor_resource_dict_list)

            redis_con = setup_redis_connection()
            logging.error("Setting condor-resources in redis...")
            redis_con.set(collector_data_key, condor_resources)
            if(testrun):
                return True
            time.sleep(sleep_interval)

        except Exception as e:
            logging.error(e)
            logging.error("Error connecting to condor or redis...")
            if(testrun):
                return False
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return False


def collector_command_consumer(testrun=False):
    collector_commands_key = config.collector_commands_key
    sleep_interval = config.command_sleep_interval
    
    while(True):
        try:
            redis_con = setup_redis_connection()
            command_string = redis_con.lpop(collector_commands_key)


            if command_string is not None:
                command_dict = json.loads(command_string)
                #execute command
                # use htcondor class's send_command function to send condor_off -peaceful to Startd and Master
                # order matters here, we need to issue the command to Startd first then Master
                # We will need the class ad for the machine found by using ad = Collector.locate(...)
                # then do htcondor.send_command(ad=ad, dc=htcondor.DaemonCommands.DaemonsOffPeaceful, target="-daemon Startd")
                #  htcondor.send_command(ad=ad, dc=htcondor.DaemonCommands.DaemonsOffPeaceful, target="-daemon Master")
                # may not need the target

                #need to get machine identifier out of command
                machine_name = command_dict['machine_name'].encode('ascii','ignore')
                command = command_dict['command']
                if command == "condor_off":
                    condor_c = htcondor.Collector()
                    logging.info("getting machine ads for %s" % machine_name)
                    startd_ad = condor_c.locate(htcondor.DaemonTypes.Startd, machine_name)
                    logging.info("found startd.. locating master")
                    master_machine_name = machine_name.split("@")[1]
                    master_ad = condor_c.locate(htcondor.DaemonTypes.Master, master_machine_name)

                    logging.info("Ads found, issuing condor_off commands...")
                    htcondor.send_command(startd_ad, htcondor.DaemonCommands.SetPeacefulShutdown)
                    htcondor.send_command(master_ad, htcondor.DaemonCommands.SetPeacefulShutdown)
                    if(testrun):
                        return True

                else:
                    logging.error("Unrecognized command")
                    if(testrun):
                        return False

            else:
                logging.info("No command in redis list, begining sleep interval...")
                #only sleep if there was no command
                if(testrun):
                    return False
                time.sleep(sleep_interval)

        except Exception as e:
            logging.error("Failure connecting to redis or executing condor command...")
            logging.error(e)
            if(testrun):
                return False
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return False

        

if __name__ == '__main__':

    logging.basicConfig(filename=config.collector_log_file,level=logging.DEBUG)
    processes = []

    p_resource_producer = Process(target=resources_producer)
    p_command_consumer = Process(target=collector_command_consumer)
    processes.append(p_resource_producer)
    processes.append(p_command_consumer)
   

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


