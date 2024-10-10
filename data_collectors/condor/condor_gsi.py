from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, terminate, check_pid
from cloudscheduler.lib.poller_functions import \
    start_cycle, \
    wait_cycle
from cloudscheduler.lib.rpc_client import RPC

import multiprocessing
from subprocess import Popen, PIPE
import time
import logging
import os
import re
import signal
import socket
import sys

import sqlalchemy.exc

def condor_gsi_poller():
    multiprocessing.current_process().name = "Condor GSI Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), 'AMQP', 'ProcessMonitor'], refreshable=True, pool_size=6, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    config.db_open()

    try:
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            condor_dict = get_condor_dict(config, logging)

            for condor in sorted(condor_dict):
                condor_rpc = RPC(config.categories['AMQP']['host'], config.categories['AMQP']['port'], config.categories['AMQP']['queue_prefix_htc'] +"_" + condor, "csv2_htc_" + condor)
                condor_cert = condor_rpc.call({'command': 'query_condor_cert'})

                if condor_cert:
                    try:
                        for group in sorted(condor_dict[condor]):
                            config.db_session.execute('update csv2_groups set %s,htcondor_gsi_eol=%d where group_name="%s";' % (if_null(condor_cert['subject'], col='htcondor_gsi_dn'), condor_cert['eol'], group))
                        config.db_session.commit()

                        if condor_cert['subject']:
                            logging.info('Condor host: "%s", %s group(s) (%s) GSI updated.' % (condor, len(condor_dict[condor]), condor_dict[condor]))
                        else:
                            logging.info('Condor host: "%s", %s group(s) (%s) GSI (not configured) updated.' % (condor, len(condor_dict[condor]), condor_dict[condor]))

                    except Exception as ex:
                        config.db_session.rollback()

                        if condor_cert['subject']:
                            logging.error('Condor host: "%s", %s group(s) (%s) GSI update failed, exception: %s' % (condor, len(condor_dict[condor]), condor_dict[condor], ex))
                        else:
                            logging.error('Condor host: "%s", %s group(s) (%s) GSI (not configured) update failed, exception: %s' % (condor, len(condor_dict[condor]), condor_dict[condor], ex))

                else:
                    logging.warning('Condor host: "%s", request timed out.' % condor)

            config.db_session.rollback()

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break

            wait_cycle(cycle_start_time, poll_time_history, config.categories['condor_gsi.py']['sleep_interval_condor_gsi'], config)

    except Exception as exc:
        logging.exception("Condor GSI while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def get_condor_dict(config, logging):
    condor_dict = {}
    group_list = config.db_connection.execute('select group_name,htcondor_fqdn from csv2_groups;')
    for group in group_list:
        try:
            condor_ip = socket.gethostbyname(group['htcondor_fqdn'])
            if group['htcondor_fqdn'] not in condor_dict:
                condor_dict[group['htcondor_fqdn']] = []

            condor_dict[group['htcondor_fqdn']].append(group['group_name'])

        except:
            logging.debug('Ignoring invalid condor host "%s".' % group['htcondor_fqdn'])

    return condor_dict

def if_null(val, col=None):
    if col:
        if val:
            return '%s="%s"' % (col, val)
        else:
            return '%s=NULL' % col

    else:
        if val:
            return val
        else:
            return 'NULL'

def worker_gsi_poller():
    multiprocessing.current_process().name = "Worker GSI Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), 'AMQP', 'ProcessMonitor'], refreshable=True, pool_size=6, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        while True:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)

            config.db_open()

            condor_dict = get_condor_dict(config, logging)

            deleted = []
            condor_list = config.db_connection.execute('select htcondor_fqdn from condor_worker_gsi;')
            for condor in condor_list:
                if condor['htcondor_fqdn'] not in condor_dict:
                    config.db_session.execute('delete from condor_worker_gsi where htcondor_fqdn="%s";' % condor['htcondor_fqdn'])
                    deleted.append(condor['htcondor_fqdn'])

                if len(deleted) > 0:
                    config.db_session.commit()
                    logging.info('The following obsolete HTCondor worker certs have been deleted from condor_worker_gsi: %s' % deleted)

            for condor in sorted(condor_dict):
                condor_rpc = RPC(config.categories['AMQP']['host'], config.categories['AMQP']['port'], config.categories['AMQP']['queue_prefix_htc'] +"_" + condor, "csv2_htc_" + condor)
                worker_cert = condor_rpc.call({'command': 'query_condor_worker_cert'})

                if worker_cert:
                    try:
                        config.db_session.execute('insert into condor_worker_gsi values("%s", "%s", %d, "%s", "%s");' % (condor, if_null(worker_cert['subject']), worker_cert['eol'], if_null(worker_cert['cert']), if_null(worker_cert['key'])))
                        config.db_session.commit()

                        if worker_cert['subject']:
                            logging.info('Condor host: "%s", condor_worker_gsi inserted.' % condor)
                        else:
                            logging.info('Condor host: "%s", condor_worker_gsi (not configured) inserted.' % condor)

                    except Exception as ex:
                        if not (isinstance(ex, sqlalchemy.exc.IntegrityError) and str(ex.orig)[1:-1].split(',')[0] == '1062'):
                            logging.warning('Condor host: "%s", condor_worker_gsi insert failed, exception: %s' % (condor, ex))

                        try:
                            config.db_session.execute('update condor_worker_gsi set %s,worker_eol=%d,%s,%s where htcondor_fqdn="%s";' % (
                                if_null(worker_cert['subject'], col='worker_dn'),
                                worker_cert['eol'],
                                if_null(worker_cert['cert'], col='worker_cert'),
                                if_null(worker_cert['key'], col='worker_key'),
                                condor))
                            config.db_session.commit()

                            if worker_cert['subject']:
                                logging.info('Condor host: "%s", condor_worker_gsi updated.' % condor)
                            else:
                                logging.info('Condor host: "%s", condor_worker_gsi (not configured) updated.' % condor)

                        except Exception as ex:
                            config.db_session.rollback()

                            if worker_cert['subject']:
                                logging.error('Condor host: "%s", condor_worker_gsi update failed, exception: %s' % (condor, ex))
                            else:
                                logging.error('Condor host: "%s", condor_worker_gsi (not configured) update failed, exception: %s' % (condor, ex))

                else:
                    logging.warning('Condor host: "%s", request timed out.' % condor)

            config.db_close()
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break

            wait_cycle(cycle_start_time, poll_time_history, config.categories['condor_gsi.py']['sleep_interval_worker_gsi'], config)

    except Exception as exc:
        logging.exception("Worker GSI while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

if __name__ == '__main__':

    process_ids = {
        'condor_gsi':    condor_gsi_poller,
        'worker_gsi':    worker_gsi_poller,
    }

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]

    procMon = ProcessMonitor(config_params=db_category_list, pool_size=4, process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))

    logging.info("**************************** starting condor_gsi - Running %s *********************************" % version)

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        signal.signal(signal.SIGTERM, terminate)
        while True:
            config.refresh()
            stop = check_pid(PID_FILE)
            procMon.check_processes(stop=stop)
            if stop:
                break
            time.sleep(config.categories['ProcessMonitor']['sleep_interval_main_long'])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")
    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()
    exit(0)
