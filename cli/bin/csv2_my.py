from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

import csv2_defaults

KEY_MAP = {
    '-upw':  'password',
    }

def settings(gvar):
    """
    Modify the specified user.
    """

    mandatory = []
    required = []
    optional = ['-H', '-h', '-s', '-upw', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    if len(form_data) < 1:
        print('Error: "%s my settings" requires at least one option to update.' % gvar['command_name'])
        exit(1)

    # Create the user.
    response = requests(
        gvar,
        '/user/settings/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

    if 'server' not in gvar['command_args']:
        gvar['command_args']['server'] = gvar['server']

    gvar['user_settings']['server-password'] = gvar['user_settings']['user-password']
    del gvar['user_settings']['user-password']
    csv2_defaults.set(gvar)

