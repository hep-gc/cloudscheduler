import time
import logging


#The intention of this library file is to provide an API for csv2 processes to register for watchdog coverage
# and allow the ProcessMonitor to use the watchdog to detect threads in a stalled state and restart them
# providing automatic recovery when a request to an external API causes a process to stall or become a zombie

def watchdog_register_process(config, pid, host_id):
    update_dict = {
        "pid": pid,
        "host_id": host_id,
        "last_heartbeat": time.time()
    }
    logging.debug("Registering %s" % pid)
    rc, msg = config.db_merge('csv2_watchdog', update_dict)
    config.db_commit()
    return 0

def watchdog_remove_process(config, pid, host_id):
    where = "pid='%s' and host_id='%s'" % (pid, host_id)
    logging.debug("Removing %s" % pid)
    config.db_delete('csv2_watchdog', where=where)
    config.db_commit()
    return 0

def watchdog_check_process(config, pid, host_id):
    where = "pid='%s' and host_id='%s'" % (pid, host_id)
    rc, msg, rows = config.db_query('csv2_watchdog', where=where)
    if rc !=0:
        # query error
        logging.error("Query error: %s" % msg)
        #returning false will restart the process, which we may or may not want to do if there is database errors
        return False
    try:
        row = rows[0]
    except Exception as exc:
        #no process registered
        logging.info("%s not found to be registered" % pid)
        return False

    current_time = time.time()
    # if last heartbeat is over an hour old return false and restart the process
    hbeat_diff = current_time - row["last_heartbeat"]
    logging.debug("Heartbeat differential: %s" % hbeat_diff)
    if (hbeat_diff > 3600):
        watchdog_send_warning(config, pid, host_id)
        logging.info("PID: %s found to be stuck" % pid)
        return False
    return True

def watchdog_send_warning(config, pid, host_id):
    return 0

def watchdog_send_heartbeat(config, pid, host_id):
    update_dict = {
        "pid": pid,
        "host_id": host_id,
        "last_heartbeat": time.time()
    }
    config.db_update('csv2_watchdog', update_dict)
    config.db_commit()
    logging.debug("watchdog updated for: %s" % pid)
    return 0


def watchdog_cleanup(config):
    #clean out all entries that havent been updated in 24 hrs
    where = "last_heartbeat <= %s" % (time.time() - (3600 * 24))
    rc, msg = config.db_delete('csv2_watchdog', where=where)
    config.db_commit()
