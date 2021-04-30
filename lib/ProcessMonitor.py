import multiprocessing
from multiprocessing import Process
import logging
import time
import datetime
import subprocess
import psutil
import os
import sys

from cloudscheduler.lib.db_config import Config

class ProcessMonitor:
    config = None
    processes = {}
    process_ids = {}
    static_process_ids = {}
    dynamic_process_ids = {}
    logging = None
    log_file = None
    log_level = None

    def __init__(self, config_params, pool_size,  process_ids=None, config_file='/etc/cloudscheduler/cloudscheduler.yaml', log_file=None, log_level=None, log_key=None):
        self.config = Config(config_file, config_params, pool_size=pool_size)
        if log_file is None:
            if log_key is not None:
                self.log_file = self.config.__dict__[log_key]["log_file"]
            else:
                self.log_file = self.config.categories[os.path.basename(sys.argv[0])]["log_file"]
        else:
            self.log_file = log_file
        if log_level is None:
            if log_key is not None:
                self.log_level = self.config.__dict__[log_key]["log_level"]
            else:
                self.log_level = self.config.categories[os.path.basename(sys.argv[0])]["log_level"]
        else:
            self.log_level = log_level

        logging.basicConfig(
            filename=self.log_file,
            level=self.log_level,
            format='%(asctime)s - %(processName)-12s - %(process)d - %(levelname)s - %(message)s')
        self.logging = logging.getLogger()
        self.process_ids = process_ids
        for proc in process_ids:
            if isinstance(process_ids[proc], list):
                # add dynamic process
                function = process_ids[proc][0]
                select = process_ids[proc][1]
                self.config.db_open()
                rows=[]
                rc, msg = self.config.db_execute(select)
                for row in self.config.db_cursor:
                    rows.append(row)
                if rc == 0:
                    #process rows
                    for row in rows:
                        logging.debug("Parsing csv2_cloud row: %s" % row)
                        target_group = row["group_name"]
                        target_cloud = row["cloud_name"]
                        dyna_proc = {
                            "function": function,
                            "args": [target_group, target_cloud],
                            "process": None
                        }
                        self.dynamic_process_ids[proc + "-" + target_group + "-" + target_cloud] = dyna_proc
                else:
                    #something wrong with the select
                    self.logging.error("Failed to retrieve child targets from select statement:%s \n Error: %s" % (select, msg))
                self.config.db_close()
            else:
                # its a static process
                logging.debug("Adding static process: %s" % process_ids[proc])
                self.static_process_ids[proc] = process_ids[proc]
        

    def get_process_ids(self):
        return self.process_ids

    def add_process_id(self, process_id, function):
        self.process_ids[process_id] = function
        _init_cpu_sleep_time(process_id)
        return

    def del_process(self, process_id, dynamic=False):
        proc = self.processes[process_id]
        logging.info("Deleting process: %s" % process_id)
        if self.is_alive(proc):
            proc.join()
        del self.processes[process_id]
        if dynamic:
            self.dynamic_process_ids.pop(process_id)
        else:
            self.process_ids.pop(process_id)
            self.static_process_ids.pop(process_id)
        return

    def get_logging(self):
        return self.logging

    def get_config(self):
        return self.config

    def start_all(self):
        # start static_ids
        for process in self.static_process_ids:
            if process not in self.processes or not self.processes[process].is_alive():
                if process in self.processes:
                    logging.error("Restarting %s...", process)
                else:
                    logging.info("Starting %s...", process)
                self.processes[process] = Process(target=self.process_ids[process])
                self.processes[process].start()

        # start dynamic_ids
        for process in self.dynamic_process_ids:
            if process not in self.processes or not self.processes[process].is_alive():
                if process in self.processes:
                    logging.error("Restarting %s...", process)
                else:
                    logging.info("Starting %s...", process)
                # key here should be function-group-cloud
                self.processes[process] = Process(target=self.dynamic_process_ids[process]["function"], args = (self.dynamic_process_ids[process]["args"],))
                self.processes[process].start()

    def restart_process(self, process, dynamic=False):
        # Capture tail of log when process has to restart
        try:
            proc = subprocess.Popen(['tail', '-n', '50', self.config.categories[os.path.basename(sys.argv[0])]["log_file"]], stdout=subprocess.PIPE)
            lines = proc.stdout.readlines()
            timestamp = str(datetime.date.today())
            with open(''.join([self.log_file, '-crash-', timestamp]), 'wb') as f:
                for line in lines:
                    f.write(line)
        except Exception as ex:
            self.logging.exception(ex)
        if dynamic:
            self.processes[process] = Process(target=self.dynamic_process_ids[process]["function"], args = (self.dynamic_process_ids[process]["args"],))
            self.processes[process].start()
        else:
            self.processes[process] = Process(target=self.process_ids[process])
            self.processes[process].start()

    def is_alive(self, process):
        return self.processes[process].is_alive()

    def kill_join_all(self):
        for proc in self.processes:
            pro = self.processes[proc]
            try:
                pro.terminate()
                pro.join()
                self._cleanup_event_pids(proc)
            except:
                logging.error("failed to join process %s", pro.name)

    def join_all(self):
        for proc in self.processes:
            pro = self.processes[proc]
            try:
                pro.join()
            except:
                logging.error("failed to join process %s", pro.name)

    def check_processes(self, stop=False):
        if stop and len(self.process_ids) == 0:
            logging.info("Stop set and all children shut down, exiting...")
            exit(0)
        if stop:
            for proc in self.process_ids:
                if self.is_alive(proc):
                    logging.info("Stop set, terminating child: %s" % proc)
                    self.processes[proc].terminate()

        procs_to_remove = []
        # handle static processes
        for process in self.static_process_ids:
            if process not in self.processes or not self.is_alive(process):
                if stop:
                    # child proc is dead, and stop flag set, don't restart and remove proc id
                    procs_to_remove.append(process)
                    del self.processes[process]
                    continue
                if process in self.processes:
                    logging.error("%s process died, restarting...", process)
                    logging.debug("exit code: %s" , self.processes[process].exitcode)
#                    self.config.update_service_catalog(error="%s process died, exit code: %s" % (process, self.processes[process].exitcode))
                    self.config.update_service_catalog(host_id=self.config.local_host_id, error="%s process died, exit code: %s" % (process, self.processes[process].exitcode))
                    del self.processes[process]
                else:
                    self.logging.info("Restarting %s process", process)
                #self._cleanup_event_pids(process)
                self.restart_process(process)
                time.sleep(self.config.categories["ProcessMonitor"]["sleep_interval_main_short"])
            p = psutil.Process(self.processes[process].pid)
        # handle dynamic processes
        dynamic_procs = self.dynamic_process_ids.keys()
        dynamic_procs_set = set(dynamic_procs)
        for proc in self.process_ids:
            #check if its a list
            if isinstance(self.process_ids[proc], list):
                #TODO ADD STOP LOGIC
                # add dynamic process
                function = self.process_ids[proc][0]
                select = self.process_ids[proc][1]
                self.config.db_open()
                rows=[]
                rc, msg = self.config.db_execute(select)
                for row in self.config.db_cursor:
                    rows.append(row)
                if rc == 0:
                    #process rows
                    for row in rows:
                        target_group = row["group_name"]
                        target_cloud = row["cloud_name"]
                        # check if process already in our list, if it is check if it's alive
                        proc_key = proc + "-" + target_group + "-" + target_cloud
                        dynamic_procs_set.remove(proc_key)
                        if proc_key in self.processes:
                            #check if it's alive
                            if not self.is_alive(proc_key):
                                #restart it
                                logging.error("%s process died, restarting...", proc_key)
                                self.config.update_service_catalog(host_id=self.config.local_host_id, error="%s process died, exit code: %s" % (proc_key, self.processes[proc_key].exitcode))
                                self.restart_process(proc_key, dynamic=True)
                        else:
                            #else create a new thread
                            dyna_proc = {
                                "function": function,
                                "args": [target_group, target_cloud],
                                "process": None
                            }
                            self.dynamic_process_ids[proc + "-" + target_group + "-" + target_cloud] = dyna_proc
                else:
                    #something wrong with the select
                    self.logging.error("Failed to retrieve child targets from select statement: %s" % msg)

        #check for any dynamic processes that are no longer needed
        # anything left in dynamic_procs_set is no longer in the database
        for proc in dynamic_procs_set:
            #join it
            self.del_process(proc, dynamic=True)

        for proc in procs_to_remove:
            self.process_ids.pop(proc)


    def _cleanup_event_pids(self, pid):
        path = self.config.categories["ProcessMonitor"]["signal_registry"]
        event_dirs = os.walk(path)
        for epath in event_dirs:
            pid_path = epath[0] + "/" + pid
            if os.path.isfile(pid_path):
                os.unlink(pid_path)


def terminate(signal_num, frame):
    try:
        logging.info("Recieved signal %s, removing pid file." % signal_num)
        pid_file = frame.f_globals["PID_FILE"]
        os.unlink(pid_file)
    except Exception as exc:
        logging.debug("Failed to unlink pid file:")
        logging.debug(exc)

#Returns false if pid exists, true if pid is gone
def check_pid(pid_file):
    if os.path.exists(pid_file):
        #PID still exists, return false
        return False
    else:
        return True
