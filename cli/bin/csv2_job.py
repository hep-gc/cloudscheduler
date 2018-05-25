from csv2_common import check_keys, requests, show_header, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-ca':  'authurl',
    '-cpw': 'password',
    '-cn':  'cloud_name',
    '-cp':  'project',
    '-cr':  'region',
    '-ct':  'cloud_type',
    '-cu':  'username',
    '-cP':  'project_domain_name',
    '-cU':  'user_domain_name',
    '-g':   'group',
    '-ga':  'cacertificate',
    '-vc':  'cores_ctl',
    '-vk':  'keyname',
    '-vr':  'ram_ctl',
    '-yn':  'yaml_name',
    '-ye':  'enabled',
    '-ymt': 'mime_type',
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
    check_keys(gvar, [], [], ['-cn', '-g', '-ok', '-vc', '-vco', '-vd', '-ved', '-vF', '-vf', '-vk', '-vr', '-vS', '-vs', '-vt'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/job/list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    job_list = _filter(gvar, response['job_list'])

    # Print report.
    show_header(gvar, response)

    if gvar['command_args']['only-keys']:
        show_table(
            gvar,
            job_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'vmid/VMID',
            ],
            )
    else:
        show_table(
            gvar,
            job_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'vmid/VMID',
                'hostname/Hostname',
                'auth_url/Authorization URL',
                'project/Project',
                'status/Status',
                'flavor_id/Flavor ID',
                'task/Task',
                'power_status/Power Status',
                'terminate/Terminate',
                'terminate_time/Terminate Time',
                'status_changed_time/Status Change Time',
                'last_updated/Last Updated',
                'flavor_name/Flavor',
                'condor_slots/Condor Slots',
                'condor_off/Condor Off',
                'foreign_vm/Foreign',
                'cores/cores',
                'disk/Disk (GBs)',
                'ephemeral_disk/Ephemeral Disk (GBs)',
                'ram/Ram (MBs)',
                'swap/Swap (GBs)',
                'poller_status/Poller Status',
            ],
            )

