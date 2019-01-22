import multiprocessing
from multiprocessing import Process
import logging
import time
import sys
import os

from cloudscheduler.lib.db_config import *
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor

from cloudscheduler.lib.poller_functions import start_cycle, wait_cycle

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


def timeseries_data_transfer():

    multiprocessing.current_process().name = "Time Series Poller"

    # Variable setup goes here for presistant data like cycle times and configuration
    # You will need to define new poll times for whatever you decide to call this file in csv2_configuration
    # A new row will also need to be added to csv2_system_status to track any crashes/errors that occur in this file
    # once that new row is added you will need to replace "N/A" with the name of the column for
    # "orange_count_row" in ProccessMonitor initialization in __main__


    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))
    #config.db_open()
    #db_session = config.db_session

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]


    while True:
        try:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            #DO ALL THE THINGS





            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_status)


        except Exception as exc:
            logging.error("Error during general operations:")
            logging.error(exc)
            logging.error("Exiting...")
            exit(1)

    return None


if __name__ == '__main__':

    process_ids = {
        'timeseries data transfer': timeseries_data_transfer,
    }

    procMon = ProcessMonitor(file_name=os.path.basename(sys.argv[0]), pool_size=3, orange_count_row='N/A', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()

    logging.info("**************************** starting timeseries data poller *********************************")

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        while True:
            procMon.check_processes()
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.join_all()
