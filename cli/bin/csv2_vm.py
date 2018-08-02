from csv2_common import check_keys, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-cn':  'cloud_name',
    '-g':   'group',
    '-vh':  'hostname',
    '-vo':  'vm_option',
    '-vS':  'poller_status',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def _filter(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    for _ix in range(len(qs)-1, -1, -1):
        if 'vm-cores' in gvar['command_args'] and str(qs[_ix]['cores']) != gvar['command_args']['vm-cores']:
            del(qs[_ix])
        elif 'vm-disk' in gvar['command_args'] and str(qs[_ix]['disk']) != gvar['command_args']['vm-disk']:
            del(qs[_ix])
        elif 'vm-flavor' in gvar['command_args'] and qs[_ix]['flavor_name'] != gvar['command_args']['vm-flavor']:
            del(qs[_ix])
        elif 'vm-foreign' in gvar['command_args'] and qs[_ix]['foreign_vm'] != gvar['command_args']['vm-foreign']:
            del(qs[_ix])
        elif 'vm-ram' in gvar['command_args'] and str(qs[_ix]['ram']) != gvar['command_args']['vm-ram']:
            del(qs[_ix])
        elif 'vm-swap' in gvar['command_args'] and str(qs[_ix]['swap']) != gvar['command_args']['vm-swap']:
            del(qs[_ix])

    return qs

def _selector(gvar):
    """
    Internal function to return a valid selector value based on the user paramaters.
    """

    selector = ['', '', '']
    if 'cloud-name' in gvar['user_settings']:
        selector[0] = gvar['user_settings']['cloud-name']
    if 'vm-status' in gvar['user_settings']:
        selector[1] = gvar['user_settings']['vm-status']
    if 'vm-hostname' in gvar['user_settings']:
        selector[2] = gvar['user_settings']['vm-hostname']

    return '::'.join(selector)


def list(gvar):
    """
    List VMs for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-H', '-h', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-vc', '-vd', '-vF', '-vf', '-vh', '-vr', '-vS', '-vs', '-xA'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/vm/list/%s' % _selector(gvar))
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    vm_list = _filter(gvar, response['vm_list'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        vm_list,
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'hostname/Hostname,k',
            'vmid/VMID',
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
            'foreign_vm/Foreign',
            'cores/cores',
            'disk/Disk (GBs)',
            'ram/Ram (MBs)',
            'swap/Swap (GBs)',
            'poller_status/Poller Status',
            'manual_control/Manual_Control',
        ],
        title="VMs:",
        )

def update(gvar):
    """
    Modify a VM in the active group.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-vo'],
        [],
        ['-cn', '-g', '-H', '-h', '-s', '-vh', '-vS', '-xA'],
        key_map=KEY_MAP)

    if len(form_data) < 2:
        print('Error: "%s vm update" requires at least one option to modify.' % gvar['command_name'])
        exit(1)

    # Create the cloud.
    response = requests(
        gvar,
        '/vm/update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

