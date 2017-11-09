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
                condor_resources = condor_c.query(ad_type=ad_type, constraint='EnteredCurrentStatus>=%d || JobStart>=%d' % (last_poll_time, last_poll_time), projection=resource_attributes)

            for resource in condor_resources:
                r_dict = dict(resource)
                if "Start" in r_dict:
                    r_dict["Start"] = str(r_dict["Start"])
                r_dict = trim_keys( r_dict, resource_attributes)
                new_resource = Resource(**r_dict)
                logging.info("Adding new or updating resource: %s" % r_dict["Name"])
                session.merge(new_resource)
            logging.info("Commiting database session")
            session.commit()


            last_poll_time = new_poll_time
            logging.info("Last poll time: %s, commencing sleep interval" % last_poll_time)
            time.sleep(sleep_interval)

        except Exception as e:
            logging.error(e)
            logging.error("Error connecting to condor or database...")
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return False



#Should support condor_off and condor_advertise

#condor_advertise - query database for all adds that need to condor_advertise
#

def collector_command_consumer():
    sleep_interval = config.command_sleep_interval
    
    while(True):
        try:
            # database setup
            Base = automap_base()
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            Resource = Base.classes.condor_resources
            session = Session(engine)

            condor_c = htcondor.Collector()
            startd_type = htcondor.AdTypes.Startd
            master_type = htcondor.AdTypes.Master

            # use htcondor class's send_command function to send condor_off -peaceful to Startd and Master
            # order matters here, we need to issue the command to Startd first then Master
            # We will need the class ad for the machine found by using ad = Collector.locate(...)
            # then do htcondor.send_command(ad=ad, dc=htcondor.DaemonCommands.DaemonsOffPeaceful, target="-daemon Startd")
            # htcondor.send_command(ad=ad, dc=htcondor.DaemonCommands.DaemonsOffPeaceful, target="-daemon Master")
            # may not need the target

            #first query for any commands to execute

            #query for condor_off commands
            #   get classads
            for resource in session.query(Resource).filter(Resource.condor_off==1):
                condor_ad = condor_c.query(ad_type=startd_type, constraint="Name==%s" % resource.Name)
                logging.info("Found entry: %s flagged for condor_off." % resource.Name)
                startd_result = htcondor.send_command(ad=condor_ad, dc=htcondor.DaemonCommands.DaemonsOffPeaceful, target="-daemon Startd")
                logging.info("Startd daemon condor_off status: %s" % startd_result)
                # Now turn off master daemon
                condor_ad = condor_c.query(ad_type=master_type, constraint="Name==%s" % resource.Name)
                master_result = htcondor.send_command(ad=condor_ad, dc=htcondor.DaemonCommands.DaemonsOffPeaceful, target="-daemon Master")
                #update database entry for condor off if the previous command was a success
                logging.info("Master daemon condor_off status: %s" % master_result)
                #flag should be removed and cleanup can be left to another thread?
                updated_resource = Resource(Name=resource.Name, condor_off=0)
                session.merge(updated_resource)


            #query for condor_advertise commands
            ad_list = []
            for resource in session.query(Resource).filter(Resource.condor_advertise==1):
                # get relevent classad objects from htcondor and compile a list for condor_advertise
                logging.info("Ad found in database flagged for condor_advertise: %s" resource.Name)
                ad = condor_c.query(ad_type=master_type, constraint="Name==%s" % resource.Name)
                ad_list.append(ad)
                updated_resource = Resource(Name=resource.Name, condor_advertise=0)
                session.merge(updated_resource)

            #execute condor_advertise on retrieved classads
            advertise_result = condor_c.advertise(ad_list, command=INVALIDATE_MASTER_ADS)
            logging.info("condor_advertise result: %s" % advertise_result)

            session.commit() #commit all updates

        except Exception as e:
            logging.error("Failure connecting to database or executing condor command...")
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


