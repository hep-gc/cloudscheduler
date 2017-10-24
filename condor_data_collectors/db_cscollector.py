from multiprocessing import Process
import time
import htcondor
import json
import config
import logging

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

def resources_producer(testrun=False, testfile=None):
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", "Activity", "VMType", "MycurrentTime", "EnteredCurrentState", "Start", "RemoteOwner", "SlotType", "TotalSlots"] 

    sleep_interval = config.machine_collection_interval
    last_poll_time = 0
    while(True):
        try:
            # Initialize condor and database objects
            Base = automap_base()
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            Resource = Base.classes.condor_resources
            session = Session(engine)

            condor_c = htcondor.Collector()
            ad_type = htcondor.AdTypes.Startd
            new_poll_time = time.time()
            ## This conditional shouldn't be needed but is here anyways incase there are any null "EnteredCurrentStatus" fields
            if last_poll_time == 0: 
                condor_resources = condor_c.query(ad_type=ad_type, constraint=True, projection=resource_attributes)
            else:
                condor_resources = condor_c.query(ad_type=ad_type, constraint='EnteredCurrentStatus>=%d' % last_poll_time, projection=resource_attributes)

            for resource in condor_resources:
                r_dict = dict(resource)
                if "Start" in r_dict:
                    r_dict["Start"] = str(r_dict["Start"])
                r_dict = trim_keys( r_dict, resource_attributes)
                new_resource = Resource(**r_dict)
                logging.info("Adding new resource: %s" % r_dict["Name"])
                session.merge(new_resource)
            session.commit()


            last_poll_time = new_poll_time
            time.sleep(sleep_interval)

        except Exception as e:
            logging.error(e)
            logging.error("Error connecting to condor or database...")
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return False

''' Implementation may not be needed in database version

#Should support condor_off and condor_advertise

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

'''

if __name__ == '__main__':

    logging.basicConfig(filename=config.collector_log_file,level=logging.DEBUG)
    processes = []

    p_resource_producer = Process(target=resources_producer)
    #p_command_consumer = Process(target=collector_command_consumer)
    processes.append(p_resource_producer)
    #processes.append(p_command_consumer)
   

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


