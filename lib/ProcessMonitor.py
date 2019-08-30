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
    process_ids = {}
    orange_count_row = None
    previous_orange_count = 0
    current_orange_count = 0
    logging = None

    def __init__(self, config_params, pool_size, orange_count_row, process_ids=None):
        self.config = Config('/etc/cloudscheduler/cloudscheduler.yaml', config_params, pool_size=pool_size, refreshable=True)
        self.logging = logging.getLogger()
        logging.basicConfig(
            filename=self.config.log_file,
            level=self.config.log_level,
            format='%(asctime)s - %(processName)-12s - %(levelname)s - %(message)s')
        self.orange_count_row = orange_count_row
        self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, orange_count_row, 1, 0)
        self.process_ids = process_ids

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
            proc = subprocess.Popen(['tail', '-n', '50', self.config[os.path.basename(sys.argv[0])]["log_file"], stdout=subprocess.PIPE)
            lines = proc.stdout.readlines()
            timestamp = str(datetime.date.today())
            with open(''.join([self.config[os.path.basename(sys.argv[0])]["log_file"], '-crash-', timestamp]), 'wb') as f:
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
                time.sleep(self.config["ProcessMonitor"]["sleep_interval_main_short"])
            p = psutil.Process(self.processes[process].pid)
        if orange:
            self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, self.orange_count_row, self.previous_orange_count, self.current_orange_count+2)
        else:
            self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, self.orange_count_row, self.previous_orange_count, self.current_orange_count-1)


    def _cleanup_event_pids(self, pid):
        path = self.config["ProcessMonitor"]["signal_registry"]
        event_dirs = os.walk(path)
        for epath in event_dirs:
            pid_path = epath[0] + "/" + pid
            if os.path.isfile(pid_path):
                os.unlink(pid_path)
