import multiprocessing
from multiprocessing import Process
import time
import logging
import re
import os
import sys

from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor

def startd_poller():
    multiprocessing.current_process().name = "StartD error poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]), pool_size=4, refreshable=True)
    VMS = config.db_map.classes.csv2_vms
    checkpoint = 0

    try:
        while True:
            logging.debug("Beginning StartD error poller cycle")
            config.refresh()

            config.db_open()

            ssl_access_log_size = os.stat(config.categories['startd_errors.py']['ssl_access_log']).st_size
            if checkpoint > ssl_access_log_size:
                checkpoint = 0


            with open(config.categories['startd_errors.py']['ssl_access_log']) as fd:
                fd.seek(checkpoint)
                ssl_access_log =fd.read()

            ssl_access_log_size = len(ssl_access_log)

            vms_in_error = {}
            for line in ssl_access_log.split('\n'):
                if '/CERT/' in line or '/STARTD/' in line:
                    ignore, ignore, ignore, hostname, type, errors = line.split('/', 5)
                    errors, ignore = errors.split(' ',1)
                    vms_in_error[hostname] = {'type': type, 'errors': errors[:VMS.htcondor_startd_errors.property.columns[0].type.length]}

            if len(vms_in_error) > 0:
                for hostname in sorted(vms_in_error):
                      if vms_in_error[hostname]['type'] == 'CERT':
                          config.db_session.execute('update csv2_vms set htcondor_startd_errors="%s",htcondor_startd_time=unix_timestamp(),retire=retire+1,updater="%s" where hostname="%s"' % (vms_in_error[hostname]['errors'], str(get_frame_info() + ":r+"), hostname))
                      elif vms_in_error[hostname]['type'] == 'STARTD':
                          config.db_session.execute('update csv2_vms set htcondor_startd_errors="%s",htcondor_startd_time=unix_timestamp() where hostname="%s"' % (vms_in_error[hostname]['errors'], hostname))

                config.db_session.commit()

            config.db_close()
            checkpoint += ssl_access_log_size

            logging.debug("Completed StartD error poller cycle")
            config.db_close()
            time.sleep(config.categories['startd_errors.py']['sleep_interval'])

    except Exception as exc:
        logging.exception("StartD error poller, while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()


if __name__ == '__main__':

    process_ids = {
        'startd':   startd_poller,
    }

    procMon = ProcessMonitor(config_params=[os.path.basename(sys.argv[0]), "general", 'ProcessMonitor'], pool_size=4, orange_count_row='csv2_jobs_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    logging.info("**************************** starting startd error monitor - Running %s *********************************" % version)

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        while True:
            procMon.check_processes()
            time.sleep(config.categories['ProcessMonitor']['sleep_interval_main_long'])
            
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()


