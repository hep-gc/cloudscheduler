from csv2_common import check_keys, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-g':   'group',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def _filter(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    for _ix in range(len(qs)-1, -1, -1):
        if 'job-id' in gvar['command_args'] and qs[_ix]['global_job_id'] != gvar['command_args']['job-id']:
            del(qs[_ix])
        elif 'job-target-alias' in gvar['command_args'] and qs[_ix]['target_alias'] != gvar['command_args']['job-target-alias']:
            del(qs[_ix])
        elif 'job-status' in gvar['command_args'] and str(qs[_ix]['job_status']) != gvar['command_args']['job-status']:
            del(qs[_ix])
        elif 'job-request-cpus' in gvar['command_args'] and str(qs[_ix]['request_cpus']) != gvar['command_args']['job-request-cpus']:
            del(qs[_ix])
        elif 'job-request-ram' in gvar['command_args'] and str(qs[_ix]['request_ram']) != gvar['command_args']['job-request-ram']:
            del(qs[_ix])
        elif 'job-request-disk' in gvar['command_args'] and str(qs[_ix]['request_disk']) != gvar['command_args']['job-request-disk']:
            del(qs[_ix])
        elif 'job-request-swap' in gvar['command_args'] and str(qs[_ix]['request_swap']) != gvar['command_args']['job-request-swap']:
            del(qs[_ix])
        elif 'job-requirements' in gvar['command_args'] and qs[_ix]['requirements'] != gvar['command_args']['job-requirements']:
            del(qs[_ix])
        elif 'job-priority' in gvar['command_args'] and str(qs[_ix]['job_priority']) != gvar['command_args']['job-priority']:
            del(qs[_ix])
        elif 'job-user' in gvar['command_args'] and qs[_ix]['user'] != gvar['command_args']['job-user']:
            del(qs[_ix])
        elif 'job-image' in gvar['command_args'] and qs[_ix]['image'] != gvar['command_args']['job-image']:
            del(qs[_ix])
        elif 'job-hold' in gvar['command_args'] and str(qs[_ix]['js_held']) != gvar['command_args']['job-hold']:
            del(qs[_ix])

    return qs

def list(gvar):
    """
    List clouds for the active group.
    """

    mandatory = []
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-H', '-h', '-jh', '-jI', '-ji', '-jp', '-jR', '-jrc', '-jrd', '-jrr', '-jrs', '-jS', '-jta', '-ju', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        mandatory,
        required,
        optional)

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/job/list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    job_list = _filter(gvar, response['job_list'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        job_list,
        [
            'group_name/Group,k',
            'global_job_id/Job ID,k',
            'cluster_id/Cluster ID',
            'proc_id/Process ID',
            'user/User',
            'user_data/User Data',
            'requirements/Requirements',
            'target_alias/Target Alias',
            'cloud_name/Cloud',
            'instance_type/Instance Type',
            'request_cpus/CPUs/Requested',
            'request_ram/RAM {MBs}/Requested',
            'request_disk/Disk {GBs}/Requested',
            'request_swap/Swap (GBs)/Requested',
            'job_per_core/Jobs per Core',
            'image/Image',
            'network/Network',
            'job_priority/Priority/Job',
            'job_status/Status Code/Job',
            'js_idle/Idle/Job Status Flags',
            'js_running/Running/Job Status Flags',
            'js_completed/Completed/Job Status Flags',
            'js_held/Held/Job Status Flags',
            'js_other/Other/Job Status Flags',
            'keep_alive/Keep Alive (seconds)',
            'max_price/Max Spot Price',
            'entered_current_status/State Change Date',
            'q_date/Queued Date',
            'held_reason/Held Job Reason',
        ],
        title="Jobs",
        )

