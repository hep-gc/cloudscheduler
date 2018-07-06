import multiprocessing
from multiprocessing import Process
import time
import logging
import socket

import collector_config as config
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

def resources_producer():
    multiprocessing.current_process().name = "Machine Poller"
    resource_attributes = ["Name", "Machine", "JobId", "GlobalJobId", "MyAddress", "State", \
                           "Activity", "VMType", "MyCurrentTime", "EnteredCurrentState", \
                           "Start", "RemoteOwner", "SlotType", "TotalSlots", "group_name", "flavor"]

    sleep_interval = config.collection_interval
    last_poll_time = 0
    condor_host = socket.gethostname()
    fail_count = 0
    # Initialize database objects
    Base = automap_base()
    engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Resource = Base.classes.condor_machines
    session = Session(engine)

    while True:
        try:
            try:
                condor_c = htcondor.Collector()
            except Exception as exc:
                fail_count = fail_count + 1
                logging.error("Unable to locate condor daemon, Failed %s times:" % fail_count)
                logging.error(exc)
                logging.error("Sleeping until next cycle...")
                time.sleep(config.sleep_interval)
                continue

            fail_count = 0

            ad_type = htcondor.AdTypes.Startd
            new_poll_time = time.time()

            condor_resources = condor_c.query(
                ad_type=ad_type,
                constraint=True,
                projection=resource_attributes)

            for resource in condor_resources:
                try:
                    r_dict = dict(resource)
                    if "Start" in r_dict:
                        r_dict["Start"] = str(r_dict["Start"])
                    r_dict = trim_keys(r_dict, resource_attributes)
                    r_dict, unmapped = map_attributes(src="condor", dest="csv2", attr_dict=r_dict)
                    if unmapped:
                        logging.error("Unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)
                    r_dict["condor_host"] = condor_host
                    r_dict["hostname"] = condor_host.split(".")[0]
                    new_resource = Resource(**r_dict)
                    logging.info("Adding new or updating resource: %s", r_dict["name"])
                    session.merge(new_resource)
                except Exception as exc:
                    logging.error("Error constructing machine dictionary for %s continuing with next resource." % resource)
                    logging.error(type(exc).__name__ + "type error occurred")
                    logging.error(exc)

            logging.info("Committing database session")

            try:        
                session.commit()
                last_poll_time = new_poll_time
            except Exception as exc:
                logging.error("Unable to commit database session")
                logging.error(exc)
                logging.error("Aborting cycle...")

            logging.info("Last poll time: %10s, commencing sleep interval", last_poll_time)
            time.sleep(sleep_interval)

        except Exception as exc:
            logging.error(type(exc).__name__ + "type error occured on:")
            logging.error(exc)
            logging.error("Error connecting to condor or database commencing sleep interval")
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return False



#Should support condor_off and condor_advertise

#condor_advertise - query database for all adds that need to condor_advertise
#

def collector_command_consumer():
    multiprocessing.current_process().name = "Cmd Consumer"
    sleep_interval = config.command_sleep_interval
    condor_host = socket.gethostname()
    # database setup
    Base = automap_base()
    engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host+ ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Resource = Base.classes.condor_machines
    session = Session(engine)

    while True:
        try:
            condor_c = htcondor.Collector()
            startd_type = htcondor.AdTypes.Startd
            master_type = htcondor.AdTypes.Master

            # use htcondor class's send_command function to send condor_off -peaceful to Startd and
            # Master, order matters here, we need to issue the command to Startd first then Master
            # We will need the class ad for the machine found by using ad = Collector.locate(...)
            # then do:
            # htcondor.send_command(
            #     ad=ad,
            #     dc=htcondor.DaemonCommands.DaemonsOffPeaceful,
            #     target="-daemon Startd")
            # htcondor.send_command(
            #     ad=ad,
            #     dc=htcondor.DaemonCommands.DaemonsOffPeaceful,
            #     target="-daemon Master")
            # may not need the target

            #first query for any commands to execute

            #query for condor_off commands
            #   get classads
            logging.info("Querying database for condor commands")
            for resource in session.query(Resource).filter(Resource.condor_host == condor_host, Resource.condor_off == 1):
                try:
                    logging.info("Command received: Querying condor for relevant job (%s)" % resource.name)
                    #condor_ad = condor_c.query(ad_type=startd_type, constraint='Name=="%s"' % resource.name)[0]
                    
                    # May not be Needed, master should shut them all down
                    #startd_result = htcondor.send_command(
                    #    condor_ad,
                    #    htcondor.DaemonCommands.DaemonsOffPeaceful)
                    #logging.info("Startd daemon condor_off status: %s", startd_result)
                    # Now turn off master daemon
                    condor_ad = condor_c.query(
                        master_type,
                        'Name=="%s"' % resource.name.split("@")[1])[0]
                    logging.info("Found entry: %s flagged for condor_off.", resource.name)
                    master_result = htcondor.send_command(
                        condor_ad,
                        htcondor.DaemonCommands.DaemonsOffPeaceful)
                    #update database entry for condor off if the previous command was a success
                    logging.info("Master daemon condor_off status: %s", master_result)
                    #flag should be removed and cleanup can be left to another thread?
                    updated_resource = Resource(name=resource.name, condor_off=2)
                    session.merge(updated_resource)
                except Exception as exc:
                    logging.error(exc)
                    logging.error("Problem processing %s... skipping", resource.name)
                    continue

            #query for condor_advertise commands
            master_list = []
            startd_list = []
            for resource in session.query(Resource).filter(Resource.condor_host == condor_host, Resource.condor_advertise == 1):
                # get relevant classad objects from htcondor and compile a list for condor_advertise
                logging.info("Ad found in database flagged for condor_advertise: %s", resource.name)
                # This is actually a little premature as we haven't executed the advertise yet
                # There should be some logic to make sure the advertise runs before we remove the flag
                updated_resource = Resource(name=resource.name, condor_advertise=2)
                try:
                    session.merge(updated_resource)
                    ad = condor_c.query(master_type, 'Name=="%s"' % resource.name.split("@")[1])[0]
                    master_list.append(ad)

                    ad = condor_c.query(startd_type, 'Name=="%s"' % resource.name)[0]
                    startd_list.append(ad)
                except Exception as exc:
                    logging.error("Unable to merge database session")
                    logging.error(exc)
                    logging.error("Aborting cycle...")
                    master_list = startd_list = None
                    break

            #execute condor_advertise on retrieved classads
            if startd_list or master_list:
                startd_advertise_result = condor_c.advertise(startd_list, "INVALIDATE_STARTD_ADS")
                master_advertise_result = condor_c.advertise(master_list, "INVALIDATE_MASTER_ADS")
                logging.info("condor_advertise result for startd ads: %s", startd_advertise_result)
                logging.info("condor_advertise result for master ads: %s", master_advertise_result)

            try:        
                session.commit()
            except Exception as exc:
                logging.error("Unable to commit database session")
                logging.error(exc)
                logging.error("Aborting cycle...")

        except Exception as exc:
            logging.error("Failure connecting to database or executing condor command...")
            logging.error(type(exc).__name__)
            logging.error(exc)
            time.sleep(sleep_interval)

        except(SystemExit, KeyboardInterrupt):
            return False

        logging.info("Command cycle finished... sleeping")
        time.sleep(sleep_interval)

def cleanUp():
    multiprocessing.current_process().name = "Cleanup"
    condor_host = socket.gethostname()
    fail_count = 0
    Base = automap_base()
    engine = create_engine("mysql+pymysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    session = Session(engine)
    #setup database objects
    Resource = Base.classes.condor_machines
    archResource = Base.classes.archived_condor_machines

    while True:
        try:
            logging.info("Commencing cleanup cycle...")
            # Setup condor classes and database connections
            # this stuff may be able to be moved outside the while loop, but i think its better to
            # re-mirror the database each time for the sake on consistency.
            try:
                condor_c = htcondor.Collector()
            except Exception as exc:
                fail_count += 1
                logging.error("Unable to locate condor daemon, Failed %s times:" % fail_count)
                logging.error(exc)
                logging.error("Sleeping until next cycle...")
                time.sleep(config.sleep_interval)
                continue

            fail_count = 0

            # Clean up machine/resource ads
            try:
                condor_machine_list = condor_c.query()
            except Exception as exc:
                logging.error(exc)
                logging.error("Failed to execute job query... aborting cycle")
                logging.error("Sleeping until next cycle...")
                time.sleep(config.sleep_interval)
                continue
            #this query asks for only resources containing reported by this collector (host)
            db_machine_list = session.query(Resource).filter(Resource.condor_host == condor_host)


            # if a machine is found in the db but not condor we need to check if it was flagged
            # for shutdown, in that case we need to update the the entry in the vm table who was
            # running the job such that we can also destroy the VM, if there is no recovery
            # process with a vm with a dead condor thread we can forgo the retire/shutdown check
            # and just mark them all for termination

            condor_name_list = []
            for ad in condor_machine_list:
                ad_dict = dict(ad)
                condor_name_list.append(ad_dict['Name'])
            for machine in db_machine_list:
                try:
                    if machine.name not in condor_name_list:
                        #machine is missing from condor, clean it up
                        logging.info("Found machine missing from condor: %s, cleaning up.", machine.name)

                        machine_dict = machine.__dict__
                        logging.info(machine_dict)
                        session.delete(machine)
                        # Archive a copy for accounting history
                        del machine_dict['_sa_instance_state']
                        new_arch_machine = archResource(**machine_dict)
                        session.merge(new_arch_machine)
                except Exception as exc:
                    logging.error("Error attempting to delete %s... skipping", machine.name)
                    logging.error(exc)

            try:        
                session.commit()
            except Exception as exc:
                logging.error("Unable to commit database session")
                logging.error(exc)
                logging.error("Aborting cycle...")
            logging.info("Cleanup cycle finished sleeping...")
            time.sleep(config.cleanup_sleep_interval)
        except Exception as exc:
            logging.error(exc)
            logging.error("Error during database automapping or during general execution")
            logging.error("Aborting cycle...")
            logging.info("Cleanup cycle finished sleeping...")
            time.sleep(config.cleanup_sleep_interval)


if __name__ == '__main__':

    logging.basicConfig(
        filename=config.log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-14s - %(levelname)s - %(message)s')
    processes = []

    # Condor Data Poller proccess
    p_resource_producer = Process(target=resources_producer)
    processes.append(p_resource_producer)
    # Command executer proccess
    p_command_consumer = Process(target=collector_command_consumer)
    processes.append(p_command_consumer)
    # Database cleanup proccess
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
            logging.error("failed to join process %s", process.name)
