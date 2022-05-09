#!/usr/bin/env python3

# Generate a public status page for cloudscheduler
import os

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloudscheduler_web.settings")

import sys
sys.path.insert(0, '/opt/cloudscheduler/web_frontend/cloudscheduler')

import django
from django.conf import settings

from django.shortcuts import render
from django.http.request import HttpRequest

from cloudscheduler.lib.view_utils import qt, qt_filter_get
from datetime import datetime
import psutil

min=60; MIN_REFRESH_INT=5*min # Enforce length of time between page generations
INT_STORE = "/var/local/cloudscheduler/public_last_update.txt" # Where last generation is stored


def generate_static_page(config, dest=None, interval_override=False):
        """
        Generate a static public page as an html file (dest).
        If interval_override is set, html page will be generated.
        Otherwise, page will be generated IFF a sufficient amount
        of time has elapsed and no error has occured during page
        generation.
        """

        if dest == None: dest = '/opt/cloudscheduler/public/index.html'

        # Check that file exists
        if not os.path.exists(INT_STORE): interval_override = True
        
        # Check that at minimum refresh interval has elapsed
        ts = datetime.now().strftime("%s")
        if not interval_override:
                with open(INT_STORE, 'r') as file:
                        if (int(file.read()) + MIN_REFRESH_INT) > int(ts):
                                return 1

        # Get list of public groups
        config.refresh()
        rc, msg, public_groups = config.db_query("csv2_groups", where="public_visibility=1")
        assert(rc==0)

        public_groups = [group['group_name'] for group in public_groups]
        
        with open(dest, "wb") as file:
                try:     html = status(config, public_groups).content
                except:  html = "<pre>Failed to generate public page.</pre>"
                finally: file.write(html)

        with open(INT_STORE, 'w') as file:
                file.write(ts)

        return 0

def status(config, public_groups, group_name=None):
    """
    This function generates a the status of a given groups operations
    VM status, job status, and machine status should all be available for a given group on this page
    """

    # *Assume that database is already open by this point

    GROUP_ALIASES = {'group_name': {"mygroups": public_groups }}
    
    # get cloud status per group
    
    rc, msg, _cloud_status_list = config.db_query("view_cloud_status")
    cloud_status_list = qt(_cloud_status_list, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    rc, msg, _job_cores_list = config.db_query("view_condor_jobs_group_defaults_applied")
    job_cores_list = qt(_job_cores_list, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    if len(cloud_status_list) < 1:
        cloud_total_list = []
        cloud_status_list_totals = []

    else:
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
                'VMs_quota',
                'VMs_native_foreign', 
                'slot_count',
                'slot_core_count',
                'slot_idle_core_count',
                'volume_gigs_max',
                'volume_gigs_used'
                ]
            })

        cloud_total_list = cloud_status_list_totals[0]

        # calculate the group view totals for all rows
        cloud_status_global_totals = qt(cloud_status_list, keys={
            'primary': [],
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
                'VMs_quota',
                'VMs_native_foreign',
                'slot_count',
                'slot_core_count',
                'slot_idle_core_count',
                'volume_gigs_max',
                'volume_gigs_used'
                ]
            })

        global_total_list = cloud_status_global_totals[0]

        cloud_status_list_totals_xref = {}
        for ix in range(len(cloud_status_list_totals)):
            cloud_status_list_totals_xref[cloud_status_list_totals[ix]['group_name']] = ix
            cloud_status_list_totals[ix]['cloud_name'] = ''
            cloud_status_list_totals[ix]['display'] = 9
            cloud_status_list_totals[ix]['tag'] = '_total'

        current_group = ''
        cloud_count = 0
        # Loop through the cloud_status_list and insert the totals row after each group of clouds:
        for index, cloud in enumerate(cloud_status_list):
            cloud['tag'] = ''
            if current_group == cloud['group_name']:
                if 'display' not in cloud:
                    cloud['display'] = 0
            else:
                cloud['display'] = 1
                if current_group != '':
                    ix = cloud_status_list_totals_xref[current_group]
                    cloud_status_list.insert(index, cloud_status_list_totals[ix].copy())

                current_group = cloud['group_name']

        if current_group != '':
            ix = cloud_status_list_totals_xref[current_group]
            cloud_status_list.append(cloud_status_list_totals[ix].copy())

        # Append the global totals list to the main status list:
        global_total_list['group_name'] = ''
        global_total_list['cloud_name'] = ''
        global_total_list['display'] = 99
        global_total_list['tag'] = '_total'

        cloud_status_list.append(global_total_list.copy())

    for row in job_cores_list:
        if not row.get('target_alias'):
            row['target_alias'] = 'None'
    job_cores_list_totals = qt(job_cores_list, keys={
        'primary': [
            'group_name',
            'target_alias',
            'request_cpus',
        ],
        'sum': [
            'js_idle',
            'js_running',
            'js_completed',
            'js_held',
            'js_other'
        ]
    })

    job_totals_list = job_cores_list_totals

    '''
    view_cloud_status_flavor_slot_detail
    view_cloud_status_flavor_slot_detail_summary
    view_cloud_status_flavor_slot_summary
    view_cloud_status_slot_detail
    view_cloud_status_slot_detail_summary
    view_cloud_status_slot_summary
    '''

    # Get slot type counts

    rc, msg, _flavor_slot_detail = config.db_query("view_cloud_status_flavor_slot_detail")
    flavor_slot_detail = qt(_flavor_slot_detail, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    rc, msg, _flavor_slot_detail_summary = config.db_query("view_cloud_status_flavor_slot_detail_summary")
    flavor_slot_detail_summary = qt(_flavor_slot_detail_summary, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    rc, msg, _flavor_slot_summary = config.db_query("view_cloud_status_flavor_slot_summary")
    flavor_slot_summary = qt(_flavor_slot_summary, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    rc, msg, _slot_detail = config.db_query("view_cloud_status_slot_detail")
    slot_detail = qt(_slot_detail, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    rc, msg, _slot_detail_summary = config.db_query("view_cloud_status_slot_detail_summary")
    slot_detail_summary = qt(_slot_detail_summary, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    rc, msg, _slot_summary = config.db_query("view_cloud_status_slot_summary")
    slot_summary = qt(_slot_summary, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))


    '''
    # Calculate the group totals:
    slot_detail_total_list = qt(slot_detail_list, keys={
        'primary': ['group_name','slot_type', 'slot_id'],
        'sum': [
            'slot_count',
            'core_count'
            ]
        })
    # Calculate the global totals:
    slot_detail_global_total_list = qt(slot_detail_list, keys={
        'primary': ['slot_type', 'slot_id'],
        'sum': [
            'slot_count',
            'core_count'
            ]
        })
    # Append the totals to the main list:
    for slot in slot_detail_total_list:
        slot['cloud_name']=''
        slot_detail_list.append(slot.copy())
    # Append the GLOBAL totals to the main list:
    for slot in slot_detail_global_total_list:
        slot['group_name']=''
        slot['cloud_name']=''
        slot_detail_list.append(slot.copy())
    # Generate the slot detail values, grouping and summing slots by type.
    #slot_detail = gen_slot_detail(slot_list)
    #slot_detail_total = gen_slot_detail(slot_total_list)
    # get slot summary
    if active_user.flag_global_status:
        s = select([view_cloud_status_slot_summary])
        slot_summary_list = qt(config.db_connection.execute(s), filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))
    else:
        s = select([view_cloud_status_slot_summary]).where(view_cloud_status_slot_summary.c.group_name == active_user.active_group)
        slot_summary_list = qt(config.db_connection.execute(s))
    # Calculate the group totals:
    slot_summary_total_list = qt(slot_summary_list, keys={
        'primary': ['group_name', 'flavor'],
        'sum': [
            'VMs',
            'Active_CPUs',
            'Idle_CPUs',
            'Idle_Percent'
            ]
        })
    # Calculate the GLOBAL totals:
    slot_summary_global_total_list = qt(slot_summary_list, keys={
        'primary': ['flavor'],
        'sum': [
            'VMs',
            'Active_CPUs',
            'Idle_CPUs',
    # Append the group totals to the main list:
    for slot in slot_summary_total_list:
        slot['cloud_name']=''
        slot_summary_list.append(slot.copy())
    # Append the GLOBAL totals to the main list:
    for slot in slot_summary_global_total_list:
        slot['group_name']=''        
        slot['cloud_name']=''
        slot_summary_list.append(slot.copy())
    '''
    # get job status per group
    table = "view_job_status_by_target_alias"
    rc, msg, _job_status_list = config.db_query(table)
    job_status_list = qt(_job_status_list, filter=qt_filter_get(['group_name'], ["mygroups"], aliases=GROUP_ALIASES, and_or='or'))

    # Get GSI configuration variables.
    gsi_config = config.get_config_by_category('GSI')

    rc, msg, service_status = config.db_query("view_service_status")

    # Determine the system load, RAM and disk usage
    system_list = {}

    system_list["load"] = round(100*( os.getloadavg()[0] / os.cpu_count() ),1)

    system_list["ram"] = psutil.virtual_memory().percent
    system_list["ram_size"] = round(psutil.virtual_memory().total/1000000000 , 1)
    system_list["ram_used"] = round(psutil.virtual_memory().used/1000000000 , 1)

    system_list["swap"] = psutil.swap_memory().percent
    system_list["swap_size"] = round(psutil.swap_memory().total/1000000000 , 1)
    system_list["swap_used"] = round(psutil.swap_memory().used/1000000000 , 1)

    system_list["disk"] = round(100*(psutil.disk_usage('/').used / psutil.disk_usage('/').total),1)
    system_list["disk_size"] = round(psutil.disk_usage('/').total/1000000000 , 1)
    system_list["disk_used"] = round(psutil.disk_usage('/').used/1000000000 , 1)

    # add current time for app credential expiry to determine how many days left
    for cloud in cloud_status_list:
        if cloud.get("app_credentials_expiry"):
            cloud["current_time"] = time.time()
    
    context = {
            # 'active_user': None,
            # 'active_group': None,
            'user_groups': public_groups,
            'cloud_status_list': cloud_status_list,
            'cloud_total_list': cloud_total_list,
            'cloud_status_list_totals': cloud_status_list_totals,
            'gsi_config': gsi_config['GSI'],
            #'global_total_list': global_total_list,
            'process_monitor_pause': config.categories['ProcessMonitor']['pause'],
            'job_status_list': job_status_list,
            'job_totals_list': job_totals_list,
            'service_status': service_status,
            'system_list' : system_list,
            #'slot_detail_list' : slot_detail_list,
            #'slot_detail_total_list': slot_detail_total_list,
            #'slot_summary_list' : slot_summary_list,
            #'slot_summary_total_list': slot_summary_total_list,           
            #'slot_detail': slot_detail,
            #'slot_detail_total': slot_detail_total,
            'flavor_slot_detail': flavor_slot_detail,
            'flavor_slot_detail_summary': flavor_slot_detail_summary,
            'flavor_slot_summary': flavor_slot_summary,
            'slot_detail': slot_detail,
            'slot_detail_summary': slot_detail_summary,
            'slot_summary': slot_summary,
            'response_code': 0,
            'message': None,
            'is_superuser': True,
            'global_flag': True,
            'jobs_by_target_alias_flag': True,
            'foreign_global_vms_flag': True,
            'slot_detail_flag': True,
            'slot_flavor_flag': True,
            'status_refresh_interval': 0,
            'version': config.get_version(),
            'last_update' : datetime.now().strftime("%b %d, %Y at %H:%M:%S")
        }

    return render(HttpRequest(), 'csv2/public_status.html', context)

if __name__ == "__main__":
        django.setup()
        config = settings.CSV2_CONFIG
        config.db_open()
        config.refresh()
        generate_static_page(config)
        config.db_close()
