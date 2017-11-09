from multiprocessing import Process
import time
import htcondor
import json
import logging
import config

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


def cleanUp():
    while(True):
        # Setup condor classes and database connctions
        condor_s = htcondor.Schedd()
        condor_c = htcondor.Collector()
        Base = automap_base()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        session = Session(engine)
        #setup database objects
        Job = Base.classes.condor_jobs
        archJob = Base.classes.archived_condor_jobs
        Resource = Base.classes.condor_resources
        archResource = Base.classes.archived_condor_resources
        

        #Part 1 Clean up job ads
        condor_job_list = condor_s.query()
        db_job_list = session.query(Job)
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



        #Part 2 Clean up machine/resource ads
        condor_machine_list = condor_c.query()
        db_machine_list = session.query(Resource)

        condor_name_list = []
        for ad in condor_machine_list:
            ad_dict = dict(ad)
            condor_name_list.append(ad_dict['Name'])
        for machine in db_machine_list:
            if machine.Name not in condor_name_list:
                #machine is missing from condor, clean it up
                logging.info("Found machine missing from condor: %s, cleaning up." % machine.Name)
                machine_dict = machine.__dict__
                logging.info(machine_dict)
                session.delete(machine)
                del machine_dict['_sa_instance_state']
                new_arch_machine = archResource(**machine_dict)
                session.merge(new_arch_machine)


        session.commit()
        time.sleep(120) #sleep 2 mins, should probably add this as a config option




if __name__ == '__main__':
    
    logging.basicConfig(filename=config.cleaner_log_file,level=logging.DEBUG)
    processes = []

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


