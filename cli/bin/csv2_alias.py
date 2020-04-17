from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-an':  'alias_name',
    '-cn':  'cloud_name',
    '-co':  'cloud_option',
    '-g':   'group',
    }

COMMAS_TO_NL = str.maketrans(',','\n')


def add(gvar):
    """
    Add a cloud to the active group.
    """

    mandatory = ['-an', '-cn']
    required = []
    optional = ['-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    # Create the cloud.
    response = requests(
        gvar,
        '/alias/add/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def list(gvar):
    """
    List aliases for the active group.
    """

    mandatory = []
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-H', '-h', '-ok', '-r', '-s', '-V', '-VC', '-NV', '-w', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/alias/list/')
    
    if response['message']:
        print(response['message'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['alias_list'],
        [
            'group_name/Group,k',
            'alias_name/Alias,k',
            'clouds/Clouds'
            ],
        title="Aliases",
        )

    show_table(
        gvar,
        response['cloud_list'],
        [
            'group_name/Group,k',
            'cloud_name/Alias,k',
            ],
        title="Clouds",
        optional=True,
        )

def update(gvar):
    """
    Modify an alias in the active group.
    """

    mandatory = ['-an', '-cn']
    required = []
    optional = ['-co', '-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    if len(form_data) < 2:
        print('Error: "%s alias update" requires at least one option to modify.' % gvar['command_name'])
        exit(1)

    # Update the alias.
    response = requests(
        gvar,
        '/alias/update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

