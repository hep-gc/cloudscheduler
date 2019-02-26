from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

import csv2_defaults

KEY_MAP = {
    '-gn':   'default_group',
    '-upw':  'password',
    '-sgs':  'flag_global_status',
    '-sri':  'status_refresh_interval',
    }

def settings(gvar):
    """
    Modify the specified user.
    """

    mandatory = []
    required = []
    optional = ['-gn', '-H', '-h', '-s', '-sgs', '-sri', '-upw', '-xA']

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

        gvar['user_settings']['server-password'] = gvar['user_settings']['user-password']
        del gvar['user_settings']['user-password']
        csv2_defaults.set(gvar)

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['user_list'],
        [
            'username/Group,k',
            'cert_cn/Cert Common Name',
            'default_group/Default Group',
            'flag_global_status/Global Switch/Status',
            'status_refresh_interval/Refresh Interval/Status',
            ],
        title="Settings",
        )

