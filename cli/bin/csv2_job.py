from csv2_common import check_keys, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-cn':  'cloud_name',
    '-g':   'group',
    '-vc':  'cores_ctl',
    '-vk':  'keyname',
    '-vr':  'ram_ctl',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def _filter(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    for _ix in range(len(qs)-1, -1, -1):
        if 'cloud-name' in gvar['command_args'] and qs[_ix]['cloud_name'] != gvar['command_args']['cloud-name']:
            del(qs[_ix])
        elif 'job-target-clouds' in gvar['command_args'] and qs[_ix]['target_clouds'] != gvar['command_args']['job-target-clouds']:
            del(qs[_ix])
        elif 'job-status' in gvar['command_args'] and str(qs[_ix]['job_status']) != gvar['command_args']['job-status']:
            del(qs[_ix])
        elif 'job-request-cpus' in gvar['command_args'] and str(qs[_ix]['job_request_cpus']) != gvar['command_args']['job-request-cpus']:
            del(qs[_ix])
        elif 'job-request-ram' in gvar['command_args'] and str(qs[_ix]['job_request_ram']) != gvar['command_args']['job-request-ram']:
            del(qs[_ix])
        elif 'job-request-disk' in gvar['command_args'] and str(qs[_ix]['job_request_disk']) != gvar['command_args']['job-request-disk']:
            del(qs[_ix])
        elif 'job-request-ephemeral-disk' in gvar['command_args'] and str(qs[_ix]['job_request_ephemeral_disk']) != gvar['command_args']['job-request-ephemeral-disk']:
            del(qs[_ix])
        elif 'job-request-swap' in gvar['command_args'] and str(qs[_ix]['job_request_swap']) != gvar['command_args']['job-request-swap']:
            del(qs[_ix])
        elif 'job-requirements' in gvar['command_args'] and qs[_ix]['job_requirements'] != gvar['command_args']['job-requirements']:
            del(qs[_ix])
        elif 'job-priority' in gvar['command_args'] and str(qs[_ix]['job_priority']) != gvar['command_args']['job-priority']:
            del(qs[_ix])
        elif 'job-user' in gvar['command_args'] and qs[_ix]['job_user'] != gvar['command_args']['job-user']:
            del(qs[_ix])
        elif 'job-image' in gvar['command_args'] and qs[_ix]['job_image'] != gvar['command_args']['job-image']:
            del(qs[_ix])
        elif 'job-hold' in gvar['command_args'] and str(qs[_ix]['job_hold']) != gvar['command_args']['job-hold']:
            del(qs[_ix])

    return qs

def list(gvar):
    """
    List clouds for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        [],
        [],
        ['-cn', '-g', '-ok', '-vc', '-vco', '-vd', '-vF', '-vf', '-vk', '-vr', '-vS', '-vs', '-vt', '-r', '-V', '-VC', '-NV', '-s', '-xA', '-h', '-H'])

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
            'target_clouds/Target Clouds',
            'cloud_name/Cloud',
            'instance_type/Instance Type',
            'request_cpus/Requested CPUs',
            'request_ram/Requested RAM {MBs}',
            'request_disk/Requested Disk {GBs}',
            'request_scratch/Requested Scratch (GBs)',
            'request_swap/Requested Swap (GBs)',
            'job_per_core/Jobs per Core',
            'image/Image',
            'network/Network',
            'job_priority/Priority',
            'job_status/Status Code',
            'js_idle/Idle',
            'js_running/Running',
            'js_completed/Completed',
            'js_held/Held',
            'js_other/Other',
            'keep_alive/Keep Alive (seconds)',
            'max_price/Max Spot Price',
            'entered_current_status/State Change Date',
            'q_date/Queued Date',
            'hold_job/Hold Job',
        ],
        title="Jobs",
        )

