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
			
			# Query db for cloud status and job status view
			cloud_status = db_session.query(view_cloud_status)
			column_list = [item["name"] for item in cloud_status.column_descriptions]
			job_status = db_session.query(view_job_status)
			job_column_list = ["jobs","jobs_idle","jobs_running","jobs_completed","jobs_held","jobs_other"]
			groups = []
			
			# Points to add to influxdb db
			data_points = []
			ts = int(time.time())

			# HTTP request args
			params = {'db': 'csv2_timeseries','precision': 's'}
			url_string = 'http://localhost:8086/write'
			
			# Parse cloud data into line protocol for influxdb
			for line in cloud_status:
				column = 2
				group = line[0]
				if( not (group in groups)):
					groups.append(group)
				cloud = line[1]
				for data in line[2:]:
					if data == -1 or data is None:
						column += 1
						continue
					new_point = "{0},cloud={1},group={2} value={3}i {4}".format(column_list[column], cloud, group, data, ts)
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

			# Collect totals
			for group in groups:
				# get cloud status per group
				s = select([view_cloud_status]).where(view_cloud_status.c.group_name == group)
				#cloud_status = db_session.select([view_cloud_status]).where(view_cloud_status.c.group_name == group)
				#console.log(cloud_status);
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
				group = cloud_total_list['group_name']
				for measurement in list(cloud_total_list.keys())[1:]:
					if cloud_total_list[measurement] == -1 or cloud_total_list[measurement] is None:
						continue
					new_point = "{0}{4},group={1} value={2}i {3}".format(measurement, group, cloud_total_list[measurement], ts, '_total')
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
