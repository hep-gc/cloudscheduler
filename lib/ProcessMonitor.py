import multiprocessing
from multiprocessing import Process
import logging
import time
import datetime
import subprocess
import psutil

from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.poller_functions import set_orange_count

class ProcessMonitor:
    config = None
    processes = {}
    p_cpu_times = {}
    process_ids = {}
    orange_count_row = None
    previous_orange_count = 0
    current_orange_count = 0
    logging = None

    def __init__(self, config_params, pool_size, orange_count_row, process_ids=None):
        self.config = Config('/etc/cloudscheduler/cloudscheduler.yaml', config_params, pool_size=pool_size)
        self.logging = logging.getLogger()
        logging.basicConfig(
            filename=self.config.log_file,
            level=self.config.log_level,
            format='%(asctime)s - %(processName)-12s - %(levelname)s - %(message)s')
        self.orange_count_row = orange_count_row
        self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, orange_count_row, 1, 0)
        self.process_ids = process_ids
        self._init_cpu_sleep_time()

    def get_process_ids(self):
        return self.process_ids

    def add_process_id(self, process_id, function):
        self.process_ids[process_id] = function
        _init_cpu_sleep_time(process_id)
        return

    def del_process(self, process_id):
        proc = self.processes[process_id]
        if self.is_alive(proc):
            proc.join()
        del self.processes[process_id]
        self.process_ids.pop(process_id)
        self.p_cpu_times.pop(process_id)
        return

    def get_logging(self):
        return self.logging

    def get_config(self):
        return self.config

    def start_all(self):
        for process in self.process_ids:
            if process not in self.processes or not self.processes[process].is_alive():
                if process in self.processes:
                    logging.error("Restarting %s...", process)
                else:
                    logging.info("Starting %s...", process)
                self.processes[process] = Process(target=self.process_ids[process])
                self.processes[process].start()

    def restart_process(self, process):
        # Capture tail of log when process has to restart
        try:
            proc = subprocess.Popen(['tail', '-n', '50', self.config.log_file], stdout=subprocess.PIPE)
            lines = proc.stdout.readlines()
            timestamp = str(datetime.date.today())
            with open(''.join([self.config.log_file, '-crash-', timestamp]), 'wb') as f:
                for line in lines:
                    f.write(line)
        except Exception as ex:
            self.logging.exception(ex)
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

    def check_processes(self):
        orange = False
        for process in self.process_ids:
            if process not in self.processes or not self.is_alive(process):
                if process in self.processes:
                    orange = True
                    logging.error("%s process died, restarting...", process)
                    logging.debug("exit code: %s" , self.processes[process].exitcode)
                    del self.processes[process]
                else:
                    self.logging.info("Restarting %s process", process)
                #self._cleanup_event_pids(process)
                self.restart_process(process)
                time.sleep(self.config.sleep_interval_main_short)
            p = psutil.Process(self.processes[process].pid)
            if self.p_cpu_times[process][1] is None:
                self.p_cpu_times[process][1] = p.cpu_times()[0]
            else:
                if p.cpu_times()[0] == self.p_cpu_times[process][1]:
                    # time hasn't changed since last check, lets count up
                    self.p_cpu_times[process][2] += self.config.sleep_interval_main_long
                else:
                    # process had some cpu time, must be running, reset timeout count
                    self.p_cpu_times[process][2] = 0
                    self.p_cpu_times[process][1] = p.cpu_times()[0]
                if self.p_cpu_times[process][2] > self.p_cpu_times[process][0]:
                    self.logging.info("Process non-responsive - restarting %s process", process)
                    self.p_cpu_times[process][2] = 0
                    orange = True
                    del self.processes[process]
                    self.restart_process(process)
                    time.sleep(self.config.sleep_interval_main_short)
        if orange:
            self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, self.orange_count_row, self.previous_orange_count, self.current_orange_count+2)
        else:
            self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, self.orange_count_row, self.previous_orange_count, self.current_orange_count-1)


    def _cleanup_event_pids(self, pid):
        path = self.config.signal_registry
        event_dirs = os.walk(path)
        for epath in event_dirs:
            pid_path = epath[0] + "/" + pid
            if os.path.isfile(pid_path):
                os.unlink(pid_path)

    # initializes sleep times for all current pids for the purpose of determining a reasonable length of time to decide if a process is deadlocked
    # a good estimate is 5 times the regular sleep time as the sleep time will grow if the system is under heavy load, we'll decide that something
    # has gone wrong if a process hasnt had cpu time in 5 * sleep_interval
    #
    # If passed a pid it will only add that one instead of calculating for all proccesses
    def _init_cpu_sleep_time(self, pid=None):
        if pid is None:
            for process in self.process_ids:
                self.logging.debug(process)
                self.p_cpu_times[process] = [20 * getattr(self.config, "sleep_interval_" + process, 180) , None, 0] #I've updated this to a 20 times the interval since the sleep window is flexible when under load. If the base cycle time is short this timeout is far too small
        else:
            # its possible that we dont have a configuration value for whatever new process is getting added, so we'll make the default 30 mins
            self.p_cpu_times[pid] = [10 * getattr(self.config, "sleep_interval_" + pid, 180), None, 0]

