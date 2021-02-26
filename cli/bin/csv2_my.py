from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file, yaml_full_load
from subprocess import Popen, PIPE

import filecmp
import os

import csv2_defaults

KEY_MAP = {
    '-gn':   'default_group',
    '-un':   'username',
    '-upw':  'password',
    '-sfv':  'flag_show_foreign_global_vms',
    '-sgs':  'flag_global_status',
    '-sjta': 'flag_jobs_by_target_alias',
    '-sri':  'status_refresh_interval',
    '-ssd':  'flag_show_slot_detail',
    '-ssf':  'flag_show_slot_flavors',
    }

def settings(gvar):
    """
    Modify the specified user.
    """

    mandatory = []
    required = []
    optional = ['-CSEP', '-CSV', '-gn', '-H', '-h', '-NV', '-ok', '-r', '-s', '-sfv', '-sgs', '-sjta', '-sri', '-ssd', '-ssf', '-un', '-upw', '-V', '-VC', '-v','-x509', '-xA']


    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

#   if len(form_data) < 1:
#       print('Error: "%s my settings" requires at least one option to update.' % gvar['command_name'])
#       exit(1)

    # Create the user.
    response = requests(
        gvar,
        '/user/settings/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

    if response['response_code'] == 0 and 'user-password' in gvar['user_settings']:
        if 'server' not in gvar['command_args']:
            gvar['command_args']['server'] = gvar['pid_defaults']['server']

        # If the user in defaults is changing their password, update it locally for them.
        with open(os.path.expanduser('~/.csv2/{}/settings.yaml').format(gvar['command_args']['server'])) as settings_file:
            saved_user = yaml_full_load(settings_file)['server-user']
        if gvar['user_settings']['server-user'] == saved_user:
            gvar['user_settings']['server-password'] = gvar['user_settings']['user-password']
            del gvar['user_settings']['user-password']
            csv2_defaults.set(gvar)

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['user_list'],
        [
            'username/Username,k',
            'cert_cn/Cert Common Name',
            'default_group/Default Group',
            'flag_show_foreign_global_vms/Foreign VMs/Status',
            'flag_global_status/Global Switch/Status',
            'flag_jobs_by_target_alias/Jobs by Target Alias/Status',
            'status_refresh_interval/Refresh Interval/Status',
            'flag_show_slot_detail/Slot Detail/Status',
            'flag_show_slot_flavors/Slot Flavors/Status',
            ],
        title="Settings",
        )

