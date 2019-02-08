import multiprocessing
from multiprocessing import Process
import logging
import time

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

    def __init__(self, file_name, pool_size, orange_count_row, process_ids=None):
        self.config = Config('/etc/cloudscheduler/cloudscheduler.yaml', file_name, pool_size=pool_size)
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
        return

    def del_process(self, process_id):
        proc = self.processes[process_id]
        if self.is_alive(proc):
            proc.join()
        del self.processes[process_id]
        self.process_ids.pop(process_id)
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
        self.processes[process] = Process(target=self.process_ids[process])
        self.processes[process].start()

    def is_alive(self, process):
        return self.processes[process].is_alive()

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
                if process in self.processes
                    orange = True
                    logging.error("%s process died, restarting...", process)
                    del self.processes[process]
                else:
                    self.logging.info("Restarting %s process", process)
                self.restart_process(process)
                time.sleep(self.config.sleep_interval_main_short)
        if orange:
            self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, self.orange_count_row, self.previous_orange_count, self.current_orange_count+1)
        else:
            self.previous_orange_count, self.current_orange_count = set_orange_count(self.logging, self.config, self.orange_count_row, self.previous_orange_count, self.current_orange_count-1)
