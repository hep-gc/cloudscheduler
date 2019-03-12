import multiprocessing
from multiprocessing import Process
import logging
import time
import sys
import os
import requests

from cloudscheduler.web_frontend.cloudscheduler.csv2.view_utils import qt

from cloudscheduler.lib.db_config import *
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor
from cloudscheduler.lib.schema import view_cloud_status
from cloudscheduler.lib.schema import view_job_status
from cloudscheduler.lib.schema import view_cloud_status_slot_detail

from cloudscheduler.lib.poller_functions import start_cycle, wait_cycle

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy.ext.automap import automap_base



def timeseries_data_transfer():

    multiprocessing.current_process().name = "Time Series Poller"

    # Variable setup goes here for presistant data like cycle times and configuration
    # You will need to define new poll times for whatever you decide to call this file in csv2_configuration
    # A new row will also need to be added to csv2_system_status to track any crashes/errors that occur in this file
    # once that new row is added you will need to replace "N/A" with the name of the column for
    # "orange_count_row" in ProccessMonitor initialization in __main__
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    while True:
        try:
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            #DO ALL THE THINGS
            config.db_open()
            db_session = config.db_session
            
            STATUS = config.db_map.classes.csv2_system_status
            statuses = db_session.query(STATUS)

            # Query db for cloud status and job status view
            cloud_status = db_session.query(view_cloud_status)
            column_list = [item["name"] for item in cloud_status.column_descriptions]
            job_status = db_session.query(view_job_status)
            """
            slot_list = db_session.query(view_cloud_status_slot_detail)
            slot_column_list = [
                "group_name",
                "cloud_name",
                "slot_tag",
                "slot_id",
                "slot_type",
                "slot_count",
                "core_count"
            ]
            """
            
            job_column_list = [
                "jobs",
                "jobs_idle",
                "jobs_running",
                "jobs_completed",
                "jobs_held",
                "jobs_other"
            ]
            groups = []
            service_status_list = [
                'csv2_main_status',
                'mariadb_status',
                'csv2_openstack_status',
                'csv2_jobs_status',
                'csv2_machines_status',
                'csv2_status_status',
                'csv2_status_error_count',
                'condor_status',
                'csv2_timeseries_status',
                'load',
                'ram_used',
                'swap_used',
                'disk_used'
            ]
            
            # Points to add to influxdb db
            data_points = []
            ts = int(time.time())

            # HTTP request args
            params = {'db': 'csv2_timeseries','precision': 's'}
            url_string = 'http://localhost:8086/write'
            
            # Parse serivce status data into line protocol for influxdb
            for status in statuses:
                status_dict = vars(status)
                for column in status_dict:
                    if(column in service_status_list):
                        new_point = "{0} value={1} {2}".format(column, status_dict[column], ts)
                        data_points.append(new_point)
            
            # Parse cloud data into line protocol for influxdb
            for line in cloud_status:
                column = 2
                group = line[0]
                if group not in groups and group != '' or None:
                    groups.append(group)
                cloud = line[1]
                for data in line[2:]:
                    if data == -1 or data is None:
                        column += 1
                        continue
                    if group == '' or None:
                        new_point = "{0},cloud={1} value={2}i {3}".format(column_list[column], cloud, data, ts)
                    else:
                        new_point = "{0},cloud={1},group={2} value={3}i {4}".format(column_list[column], cloud, group, data, ts)
                    #new_point = "{0},cloud={1},group={2} value={3}i {4}".format(column_list[column], cloud, group, data, ts)
                    data_points.append(new_point)
                    column += 1

            # Parse job data into line protocol for influxdb
            for line in job_status:
                column = 0
                group = line[0]
                for data in line[1:]:
                    if data == -1 or data is None:
                        column += 1
                        continue
                    new_point = "{0},group={1} value={2}i {3}".format(job_column_list[column], group, data, ts)
                    data_points.append(new_point)
                    column += 1
            """
            # slot data
            if slot_list:
                for line in slot_list:
                    column = 2
                    group = line[0]
                    cloud = line[1]
                    for data in line[2:]:
                        if data == -1 or data is None:
                            column += 1
                            continue
                        new_point = "{0},cloud={1},group={2} value={3}i {4}".format(slot_column_list[column], cloud, group, data, ts)
                        data_points.append(new_point)
                        column += 1
            """

            # Collect totals
            for group in groups:
                # get cloud status per group
                s = select([view_cloud_status]).where(view_cloud_status.c.group_name == group)
                cloud_status_list = qt(config.db_connection.execute(s))
                # calculate the totals for all rows
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
                        'slot_idle_core_count'
                    ]
                })

                cloud_total_list = cloud_status_list_totals[0]
                try:
                    groupname = cloud_total_list['group_name']
                except Exception as exc:
                    # dictionary is empty and we got a key error
                    logging.error("Unable to get a cloud_total_list for %s skipping..." % group)
                for measurement in list(cloud_total_list.keys())[1:]:
                    if cloud_total_list[measurement] == -1 or cloud_total_list[measurement] is None:
                        continue
                    new_point = "{0}{4},group={1} value={2}i {3}".format(measurement, group, cloud_total_list[measurement], ts, '_total')
                    data_points.append(new_point)

             
            # get slot type counts
            s = select([view_cloud_status_slot_detail])
            slot_list = qt(config.db_connection.execute(s))
            if slot_list:
                slot_cores_list = qt(slot_list, keys={
                'primary': ['group_name', 'cloud_name', 'slot_type'],
                'sum': [
                       'slot_count'
                       ]
                })
                #logging.info(slot_list)
                #logging.info(slot_cores_list)
                """core_count_list = []
                
                for num_cores in slot_cores_list:
                    count = 0
                    for slot in slot_list:
                        if slot['group_name'] == num_cores['group_name'] and slot['cloud_name'] == num_cores['cloud_name'] and slot['slot_type'] == num_cores['slot_type']:
                            count += 1                
                    core_count_list.append(count)
                #logging.info(core_count_list)
                cnt = 0
                """
                for num_cores in slot_cores_list:
                    new_point = "{0}{5},cloud={1},group={2} value={3}i {4}".format(num_cores['slot_type'], num_cores['cloud_name'], num_cores['group_name'], num_cores['slot_count'], ts, "core") 
                    #cnt += 1
                    #print(new_point)
                    #logging.info(new_point)
                    data_points.append(new_point)

            
            data_points = "\n".join(data_points)
           
            # POST HTTP request to influxdb
            try:
                r = requests.post(url_string, params=params, data=data_points)
                # Check response status code
                r.raise_for_status()
                
            except Exception as exc:
                logging.error("HTTP POST request failed to InfluxDB...")
                logging.error(exc)
                logging.error(r.headers)
                break
                
            config.db_close()
            del db_session
            
            

            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_status)


        except Exception as exc:
            logging.error("Error during general operations:")
            logging.error(exc)
            logging.error("Exiting...")
            exit(1)

    return None


if __name__ == '__main__':

    process_ids = {
        'timeseries data transfer': timeseries_data_transfer,
    }
    
    procMon = ProcessMonitor(file_name=os.path.basename(sys.argv[0]), pool_size=3, orange_count_row='csv2_timeseries_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()

    logging.info("**************************** starting timeseries data poller *********************************")

    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        while True:
            procMon.check_processes()
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.join_all()
