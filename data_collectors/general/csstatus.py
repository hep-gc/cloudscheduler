import multiprocessing
from multiprocessing import Process
import logging
import time
import signal
import sys
import os
import psutil
from subprocess import Popen, PIPE


from cloudscheduler.lib.db_config import *
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, terminate, check_pid

from cloudscheduler.lib.poller_functions import \
    start_cycle, \
    wait_cycle

import htcondor
import classad
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

def _is_container():
    #check if in container to know if we need to treat mariadb differently
    path='/proc/self/cgroup'
    return (os.path.exists('/.dockerenv') or 
            os.path.isfile(path) and any('kubepods' in line for line in open(path))
           )

def _service_msg(service_name):
    # there is a special case where service_name is csv2_status and the following os command won't get rid of problem characters
    if service_name == "csv2-status":
        # handle it differently
        file = os.popen("service "+service_name+" status | grep 'Active'")
        status = file.read()
        return status.splitlines()[0][11:]
    elif service_name == "mariadb" and _is_container():
       config.db_open()
       code, msg = config.db_session_execute('do 0;', allow_no_rows=True) 
       config.db_close()
       logging.debug("%s, %s" % (code, msg))
       if code == 0:
           return "active (running in separate container)"
       else:
           return ("Stopped (unknown reason)\n Message from query: %s" %(msg))
    else:
        return os.popen("service "+service_name+" status | grep 'Active' | cut -c12-").read()


def status_poller():
    multiprocessing.current_process().name = "Status Poller"

    services = ["csv2-main", "csv2-openstack", "csv2-jobs", "csv2-machines", "csv2-condor-gsi", "csv2-status", "csv2-timeseries", "csv2-ec2", "csv2-htc-agent", "csv2-watch", "csv2-vm-data", "rabbitmq-server", "mariadb", "condor"]
    db_service_names = {
                        "csv2-main":        "csv2_main", 
                        "csv2-openstack":   "csv2_openstack", 
                        "csv2-jobs":        "csv2_jobs", 
                        "csv2-machines":    "csv2_machines", 
                        "csv2-condor-gsi":  "csv2_condor_gsi", 
                        "csv2-status":      "csv2_status", 
                        "csv2-timeseries":  "csv2_timeseries",
                        "csv2-ec2":         "csv2_ec2",
                        "csv2-htc-agent":   "csv2_htc_agent",
                        "csv2-watch":       "csv2_watch",
                        "csv2-vm-data":     "csv2_vm_data",
                        "rabbitmq-server":  "rabbitmq_server",
                        "mariadb":          "mariadb", 
                        "condor":           "condor"
                   }

    # Initialize database objects
    #Base = automap_base()
    #db_engine = create_engine(
    #    'mysql://%s:%s@%s:%s/%s' % (
    #        config.db_config['db_user'],
    #        config.db_config['db_password'],
    #        config.db_config['db_host'],
    #        str(config.db_config['db_port']),
    #        config.db_config['db_name']
    #        )
    #    )
    #Base.prepare(db_engine, reflect=True)
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]),"ProcessMonitor"], signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    STATUS = config.db_map.classes.csv2_system_status

    config.db_open()
    db_session = config.db_session

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        while True:
            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)

            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            # id will always be zero because we only ever want one row of these
            system_dict = {'id': 0}
            for service in services:
                system_dict[db_service_names[service] + "_msg"] = _service_msg(service)
                if "running" in system_dict[db_service_names[service] + "_msg"]:
                    system_dict[db_service_names[service] + "_status"] = 1
                else:
                    system_dict[db_service_names[service] + "_status"] = 0
                    logging.error("Found service %s is dead...", service)

            system_dict["load"] = round(100*( os.getloadavg()[0] / os.cpu_count() ),1)

            system_dict["ram"] = psutil.virtual_memory().percent
            system_dict["ram_size"] = round(psutil.virtual_memory().total/1000000000 , 1)
            system_dict["ram_used"] = round(psutil.virtual_memory().used/1000000000 , 1)

            system_dict["swap"] = psutil.swap_memory().percent
            system_dict["swap_size"] = round(psutil.swap_memory().total/1000000000 , 1)
            system_dict["swap_used"] = round(psutil.swap_memory().used/1000000000 , 1)


            system_dict["disk"] = round(100*(psutil.disk_usage('/').used / psutil.disk_usage('/').total),1)
            system_dict["disk_size"] = round(psutil.disk_usage('/').total/1000000000 , 1)
            system_dict["disk_used"] = round(psutil.disk_usage('/').used/1000000000 , 1)

            system_dict["last_updated"] = int(time.time())

            new_status = STATUS(**system_dict)
            try:
                db_session.merge(new_status)
                db_session.commit()
            except Exception as exc:
                logging.exception("Failed to merge and commit status update exiting")
                config.db_close()
                del db_session
                exit(1)

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            wait_cycle(cycle_start_time, poll_time_history, config.categories["csstatus.py"]["sleep_interval_status"], config)
    except Exception as exc:
        logging.exception("Problem during general execution:")
        logging.exception(exc)
        logging.error("Exiting..")
        config.db_close()
        del db_session
        exit(1)


if __name__ == '__main__':

    process_ids = {
        'status': status_poller,
    }

    procMon = ProcessMonitor(config_params=[os.path.basename(sys.argv[0]), "ProcessMonitor"], pool_size=8, process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()

    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))


    logging.info("**************************** starting csstatus *********************************")

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        signal.signal(signal.SIGTERM, terminate)
        while True:
            config.refresh()
            stop = check_pid(PID_FILE)
            procMon.check_processes(stop=stop)
            time.sleep(config.categories["ProcessMonitor"]["sleep_interval_main_long"])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.join_all()
