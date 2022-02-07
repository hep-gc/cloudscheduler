import multiprocessing
from multiprocessing import Process
import logging
import time
import sys
import os
import requests
import signal
import psutil

from cloudscheduler.lib.view_utils import qt
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, terminate, check_pid

from cloudscheduler.lib.poller_functions import start_cycle, wait_cycle


def _cast_int(variable):
    if variable is None:
        return 0
    else:
        return int(variable)

def timeseries_data_transfer():

    multiprocessing.current_process().name = "Time Series Poller"

    # Variable setup goes here for presistant data like cycle times and configuration
    # You will need to define new poll times for whatever you decide to call this file in csv2_configuration
    # A new row will also need to be added to csv2_system_status to track any crashes/errors that occur in this file
    # once that new row is added you will need to replace "N/A" with the name of the column for
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), "ProcessMonitor"], signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])


    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    while True:
        try:
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            #DO ALL THE THINGS
            config.db_open()
            config.refresh()
            
            rc, msg, statuses = config.db_query("view_service_status")

            # Query mariadb for cloud status and job status view
            rc, msg, cloud_status = config.db_query("view_cloud_status")
            # This column list used to be generated via a sqlalchemy object, we may need to make a more specific database query to do the trick here
            # but for now we'll just take they keys of the resultant dictionary as the column names
            if len(cloud_status) > 0:
                column_list = list(cloud_status[0].keys())
            else:
                column_list = []
            rc, msg, job_status = config.db_query("view_job_status")
            
            job_column_list = [
                'jobs',
                'jobs_idle',
                'jobs_running',
                'jobs_completed',
                'jobs_held',
                'jobs_other',
                'jobs_foreign',
                'jobs_htcondor_status',
            ]
            service_status_list = [
                'csv2_main_status',
                'csv2_openstack_status',
                'csv2_jobs_status',
                'csv2_machines_status',
                'csv2_status_status',
                'csv2_status_error_count',
                'csv2_timeseries_status',
                'csv2_ec2_status', 
                'csv2_glint_status', 
                'csv2_watch_status', 
                'csv2_startd_errors_status', 
                'rabbitmq_server_status',
                'mariadb_status',
                'condor_status',
                'load',
                'ram_used',
                'swap_used',
                'disk_used'
            ]

            # Points to add to influxdb db. Will be in Line Protocol, seperated by \n
            # InfluxDB Line Protocol: <measurement>,<tag-key>=<tag-value> <field-key>=<field-value> unix-timestamp
            # Ex. vms_starting,group=csv2_group,cloud=sheep value=1 timestamp
            data_points = []
            ts = int(time.time())
            groups = []
            # HTTP request args for influxdb
            # Specifying database and timestamp precision
            params = {'db': 'csv2_timeseries','precision': 's'}
            url_string = 'http://localhost:8086/write'
            
            # Parse service status data into line protocol for influxdb
            '''
            for status in statuses:
                status_dict = vars(status)
                for column in status_dict:
                    if(column in service_status_list):
                        new_point = "{0} value={1} {2}".format(column, status_dict[column], ts)
                        data_points.append(new_point)
            '''
            for status in statuses:
                new_point = "{0} value={1} {2}".format(status["alias"], status["plotable_state"], ts)
                data_points.append(new_point)
    
            # Parse service resources data into line protocol for influxdb
            load = round(100*( os.getloadavg()[0] / os.cpu_count() ),1)
            new_point_load = "{0} value={1} {2}".format("load", load, ts)
            data_points.append(new_point_load)

            ram_used = round(psutil.virtual_memory().used/1000000000 , 1)
            new_point_ram = "{0} value={1} {2}".format("ram_used", ram_used, ts)
            data_points.append(new_point_ram)

            swap_used = round(psutil.swap_memory().used/1000000000 , 1)
            new_point_swap = "{0} value={1} {2}".format("swap_used", swap_used, ts)
            data_points.append(new_point_swap)

            disk_used = round(psutil.disk_usage('/').used/1000000000 , 1)
            new_point_disk = "{0} value={1} {2}".format("disk_used", disk_used, ts)
            data_points.append(new_point_disk)
            
            # Parse cloud status data into line protocol for influxdb
            for line in cloud_status:
                group = line["group_name"]
                if group not in groups and group != '' or None:
                    groups.append(group)
                cloud = line["cloud_name"]
                for key in line:
                    if key == "cloud_name" or key == "group_name":
                        continue
                    if line[key] == -1 or line[key] is None:
                        continue
                    if group == '' or None:
                        new_point = "{0},cloud={1} value={2}i {3}".format(key, cloud, int(data), ts)
                    else:
                        new_point = "{0},cloud={1},group={2} value={3}i {4}".format(key, cloud, group, int(line[key]), ts)

                    data_points.append(new_point)

            # Parse job status data into line protocol for influxdb
            for line in job_status:
                group = line["group_name"]

                for key in line:
                    #this is a dirty way to do it but we dont want to plot the following fields, everything else should get a trace
                    if key == "group_name" or key == "htcondor_fqdn" or key == "state" or key == "condor_days_left" or key == "worker_days_left" or key == "error_message":
                        continue
                    if key == "Jobs":
                        trace_name = "jobs"
                    else:
                        trace_name = "jobs_" + key
                        trace_name = trace_name.lower()
                    new_point = "{0}{4},group={1} value={2}i {3}".format(trace_name, group, _cast_int(line[key]), ts, '_total')
                    data_points.append(new_point)

            # Parse job status data on group alias
            rc, msg, job_status_alias = config.db_query("view_job_status_by_target_alias")
            for line in job_status_alias:
                group = line["group_name"]
                alias = line["target_alias"]
                if alias is None:
                    alias = "None"

                for key in line:
                    #this is a dirty way to do it but we dont want to plot the following fields, everything else should get a trace
                    if key == "group_name" or key == "target_alias" or key == "htcondor_fqdn" or key == "state" or key == "condor_days_left" or key == "worker_days_left" or key == "error_message":
                        continue
                    if key == "Jobs":
                        trace_name = "jobs"
                    else:
                        trace_name = "jobs_" + key
                        trace_name = trace_name.lower()
                    new_point = "{0},cloud={4},group={1} value={2}i {3}".format(trace_name, group, _cast_int(line[key]), ts, alias)
                    data_points.append(new_point)

            # Collect group totals
            for group in groups:
                # Get cloud status per group
                where_clause = "group_name='%s'" % group
                rc, msg, cloud_status_list = config.db_query("view_cloud_status", where=where_clause)
                # Calculate the totals for all rows
                cloud_status_list_totals = qt(cloud_status_list, keys={
                    'primary': ['group_name'],
                    'sum': [
                        'VMs',
                        'VMs_starting',
                        'VMs_unregistered',
                        'VMs_idle',
                        'VMs_running',
                        'VMs_retiring',
                        'VMs_manual',
                        'VMs_in_error',
                        'Foreign_VMs',
                        'VMs_native_foreign',
                        'cores_limit',
                        'cores_foreign',
                        'cores_idle',
                        'cores_native',
                        'cores_native_foreign',
                        'cores_quota',
                        'ram_quota',
                        'ram_foreign',
                        'ram_idle',
                        'ram_native',
                        'ram_native_foreign',
                        'slot_count',
                        'slot_core_count',
                        'slot_idle_core_count',
                        'volume_gigs_max',
                        'volume_gigs_used'
                    ]
                })
                cloud_total_list = cloud_status_list_totals[0]
                
                try:
                    groupname = cloud_total_list['group_name']
                except Exception as exc:
                    # Dictionary is empty and we got a key error
                    logging.error("Unable to get a cloud_total_list for %s skipping..." % group)
                for measurement in list(cloud_total_list.keys())[1:]:
                    if cloud_total_list[measurement] == -1 or cloud_total_list[measurement] is None:
                        continue
                    new_point = "{0}{4},group={1} value={2}i {3}".format(measurement, group, int(cloud_total_list[measurement]), ts, '_total')
                    data_points.append(new_point)

            # Get slot type counts details
            try:
                rc, msg, slot_list = config.db_query("view_cloud_status_slot_detail")
                if slot_list:
                    slot_cores_list = qt(slot_list, keys={
                        'primary': ['group_name', 'cloud_name', 'slot_type'],
                        'sum': [
                            'slot_count'
                        ]
                    })
                    for num_cores in slot_cores_list:
                        new_point = "{0}{5},cloud={1},group={2} value={3}i {4}".format(num_cores['slot_type'], num_cores['cloud_name'], num_cores['group_name'], int(num_cores['slot_count']), ts, "core") 
                        data_points.append(new_point)
            except Exception as exc:
                logging.error("Unable to get slot core type counts... skipping...")
                logging.error(exc)
            
            # Get job core details for job status
            rc, msg, job_details_list = config.db_query("view_condor_jobs_group_defaults_applied")
            if job_details_list:
                job_details_list_totals = qt(job_details_list, keys={
                    'primary': ['group_name', 'request_cpus'],
                    'sum': [
                        'js_idle',
                        'js_running',
                        'js_completed',
                        'js_held',
                        'js_other'
                        ]
                    })
                try:
                    for job_cores in job_details_list_totals:
                        cnt = 0
                        for job_state in job_cores.keys():
                            if cnt < 2 or job_cores[job_state] == 0:
                                cnt += 1
                                continue
                            new_point = "{0}{1}{2}{3}{7},group={4} value={5}i {6}".format(job_column_list[cnt-1], "_", job_cores['request_cpus'], "core", job_cores['group_name'], int(job_cores[job_state]), ts, '_total') 
                            data_points.append(new_point)
                            cnt += 1
                except Exception as exc:
                    logging.error("Unable to process job core details... skipping... %s " % exc)

            # Get job core details for job status on group alias
            rc, msg, job_details_list_alias = config.db_query("view_condor_jobs_group_defaults_applied")
            if job_details_list_alias:
                for job in job_details_list_alias:
                    if not job.get('target_alias'):
                        job['target_alias'] = 'None'
                job_details_list_alias_totals = qt(job_details_list_alias, keys={
                    'primary': ['group_name', 'target_alias', 'request_cpus'],
                    'sum': [
                        'js_idle',
                        'js_running',
                        'js_completed',
                        'js_held',
                        'js_other'
                    ]
                })
                try:
                    for job_cores in job_details_list_alias_totals:
                        cnt = 0
                        for job_state in job_cores.keys():
                            if cnt < 3 or job_cores[job_state] == 0:
                                cnt += 1
                                continue
                            new_point = "{0}{1}{2}{3},cloud={7},group={4} value={5}i {6}".format(job_column_list[cnt-2], "_", job_cores['request_cpus'], "core", job_cores['group_name'], int(job_cores[job_state]), ts, job_cores['target_alias'])
                            data_points.append(new_point)
                            cnt += 1
                except Exception as exc:
                    logging.error("Unable to process job core alias details... skipping... %s " % exc)
                    
            data_points = "\n".join(data_points)

            # POST HTTP request to influxdb
            try:
                r = requests.post(url_string, params=params, data=data_points)
                # Check response status code
                r.raise_for_status()
                
            except Exception as exc:
                logging.error("HTTP POST request failed to InfluxDB...")
                logging.exception(exc)
                logging.error(r.headers)
                
            config.db_close()
            
            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            wait_cycle(cycle_start_time, poll_time_history, config.categories["timeseriesPoller.py"]["sleep_interval_status"], config)


        except Exception as exc:
            logging.error("Error during general operations:")
            logging.exception(exc)
            logging.error("Exiting...")
            exit(1)

    return None


if __name__ == '__main__':

    process_ids = {
        'timeseries data transfer': timeseries_data_transfer,
    }
    
    procMon = ProcessMonitor(config_params=[os.path.basename(sys.argv[0]), "ProcessMonitor"], pool_size=3, process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()

    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))

    logging.info("**************************** starting timeseries data poller *********************************")

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        signal.signal(signal.SIGTERM, terminate)
        while True:
            config.refresh()
            config.update_service_catalog()
            stop = check_pid(PID_FILE)
            procMon.check_processes(stop=stop)
            time.sleep(config.categories["ProcessMonitor"]["sleep_interval_main_long"])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.join_all()
