from csv2_common import check_keys, requests, show_header, show_table
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
        elif 'vm-cores' in gvar['command_args'] and str(qs[_ix]['cores']) != gvar['command_args']['vm-cores']:
            del(qs[_ix])
        elif 'vm-disk' in gvar['command_args'] and str(qs[_ix]['disk']) != gvar['command_args']['vm-disk']:
            del(qs[_ix])
        elif 'vm-ephemeral-disk' in gvar['command_args'] and str(qs[_ix]['ephemeral_disk']) != gvar['command_args']['vm-ephemeral-disk']:
            del(qs[_ix])
        elif 'vm-foreign' in gvar['command_args'] and str(qs[_ix]['foreign_vm']) != gvar['command_args']['vm-foreign']:
            del(qs[_ix])
        elif 'vm-flavor' in gvar['command_args'] and qs[_ix]['flavor_name'] != gvar['command_args']['vm-flavor']:
            del(qs[_ix])
        elif 'vm-ram' in gvar['command_args'] and str(qs[_ix]['ram']) != gvar['command_args']['vm-ram']:
            del(qs[_ix])
        elif 'vm-status' in gvar['command_args'] and qs[_ix]['status'] != gvar['command_args']['vm-status']:
            del(qs[_ix])
        elif 'vm-swap' in gvar['command_args'] and str(qs[_ix]['swap']) != gvar['command_args']['vm-swap']:
            del(qs[_ix])

    return qs

def list(gvar):
    """
    List clouds for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-ok', '-vc', '-vd', '-ved', '-vF', '-vf', '-vk', '-vr', '-vS', '-vs'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/vm/list/::::')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    vm_list = _filter(gvar, response['vm_list'])

    # Print report.
    show_header(gvar, response)

    if gvar['command_args']['only-keys']:
        show_table(
            gvar,
            vm_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'vmid/VMID',
            ],
            title="VMs:",
            )
    else:
        show_table(
            gvar,
            vm_list,
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
            title="VMs:",
            )

