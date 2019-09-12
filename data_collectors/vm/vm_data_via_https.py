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

def vm_data_poller():
    multiprocessing.current_process().name = "StartD error poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]), pool_size=4, refreshable=True)
    VMS = config.db_map.classes.csv2_vms
    checkpoint = 0

    try:
        while True:
            logging.debug("Beginning StartD error poller cycle")
            config.refresh()

            config.db_open()

            ssl_access_log_size = os.stat(config.categories['vm_data_via_https.py']['ssl_access_log']).st_size
            if checkpoint > ssl_access_log_size:
                checkpoint = 0


            with open(config.categories['vm_data_via_https.py']['ssl_access_log']) as fd:
                fd.seek(checkpoint)
                ssl_access_log =fd.read()

            ssl_access_log_size = len(ssl_access_log)

            apel_updates = []
            vms_in_error = {}
            for line in ssl_access_log.split('\n'):
                if '/CERT/' in line or '/STARTD/' in line:
                    ignore, ignore, ignore, hostname, type, errors = line.split('/', 5)
                    errors, ignore = errors.split(' ',1)
                    vms_in_error[hostname] = {'type': type, 'errors': errors[:VMS.htcondor_startd_errors.property.columns[0].type.length]}

                elif '/APEL_ACCOUNTING=' in line:
                    group_name = None
                    cloud_name = None
                    key_values = []

                    ignore, ignore, ignore, hostname, apel_accounting = line.split('/', 4)
                    for key_val in apel_accounting[17:].split(','):
                        key, val = key_val.split(':', 1)
                        if val and val != '':
                            if key == 'group_name':
                                group_name = val
                            elif key == 'cloud_name':
                                cloud_name = val
                            else:
                                key_values.append('%s=%s' % (key, val))

                    if group_name and cloud_name and len(key_values) > 0:
                        apel_updates.append('update apel_accounting set %s where group_name=%s and cloud_name=%s and hostname="%s";' % (','.join(key_values), group_name, cloud_name, hostname))

            updates = 0
            if len(vms_in_error) > 0:
                for hostname in sorted(vms_in_error):
                      if vms_in_error[hostname]['type'] == 'CERT':
                          config.db_session.execute('update csv2_vms set htcondor_startd_errors="%s",htcondor_startd_time=unix_timestamp(),retire=retire+1,updater="%s" where hostname="%s"' % (vms_in_error[hostname]['errors'], str(get_frame_info() + ":r+"), hostname))
                          updates += 1
                      elif vms_in_error[hostname]['type'] == 'STARTD':
                          config.db_session.execute('update csv2_vms set htcondor_startd_errors="%s",htcondor_startd_time=unix_timestamp() where hostname="%s"' % (vms_in_error[hostname]['errors'], hostname))
                          updates += 1

            for apel_update in apel_updates:
                try:
                    config.db_session.execute(apel_update)
                    updates += 1
                except Exception as ex:
                    logging.error('%s failed - %s' % (apel_update, ex))
                
            if updates > 0:
                config.db_session.commit()

            config.db_close()
            checkpoint += ssl_access_log_size

            logging.debug("Completed StartD error poller cycle")
            config.db_close()
            time.sleep(config.categories['vm_data_via_https.py']['sleep_interval'])

    except Exception as exc:
        logging.exception("StartD error poller, while loop exception, process terminating...")
        logging.error(exc)
        del condor_session
        db_session.close()


if __name__ == '__main__':

    process_ids = {
        'vm_data':   vm_data_poller,
    }

    procMon = ProcessMonitor(config_params=[os.path.basename(sys.argv[0]), "general", 'ProcessMonitor'], pool_size=4, orange_count_row='csv2_jobs_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    logging.info("**************************** starting VM data monitor - Running %s *********************************" % version)

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


