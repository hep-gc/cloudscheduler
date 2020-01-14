from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-gn':   'group_name',
    '-go':   'group_option',
    '-SU':   'is_superuser',
    '-ucn':  'cert_cn',
    '-un':   'username',
    '-upw':  'password',
    }

def _filter_by_user(gvar, qs):
    """
    Internal function to filter a query set by the specified user name.
    """

    if 'username' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['username'] != gvar['command_args']['username']:
                del(qs[_ix])

    return qs

def add(gvar):
    """
    Add a user.
    """

    mandatory = ['-un', '-upw']
    required = []
    optional = ['-g', '-gn', '-H', '-h', '-SU', '-s', '-ucn', '-v', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    # Create the user.
    response = requests(
        gvar,
        '/user/add/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def delete(gvar):
    """
    Delete a user.
    """

    mandatory = ['-un']
    required = []
    optional = ['-g', '-H', '-h', '-s', '-v', '-v', '-x509', '-xA', '-Y']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Check that the target user exists.
    response = requests(gvar, '/user/list/')
    _found = False
    for row in response['user_list']:
      if row['username'] == gvar['user_settings']['username']:
        _found = True
        break
   
    if not _found:
        print('Error: "%s user delete" cannot delete "%s", user doesn\'t exist.' % (gvar['command_name'], gvar['user_settings']['username']))
        exit(1)

    # Confirm user delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete user "%s"? (yes|..)' % gvar['user_settings']['username'])
        _reply = input()
        if _reply != 'yes':
          print('%s user delete "%s" cancelled.' % (gvar['command_name'], gvar['user_settings']['username']))
          exit(0)

    # Delete the user.
    response = requests(
        gvar,
        '/user/delete/',
        form_data = {
            'username': gvar['user_settings']['username']
            }
        )
    
    if response['message']:
        print(response['message'])

def list(gvar):
    """
    List users.
    """

    mandatory = []
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-H', '-h', '-NV', '-ok', '-r', '-s', '-un', '-V', '-VC', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Retrieve data (possibly after changing the user).
    response = requests(gvar, '/user/list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    user_list = _filter_by_user(gvar, response['user_list'])

    # Print report
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        user_list,
        [
            'username/Username,k',
            'cert_cn/Common Name',
            'active_group/Active Group',
            'user_groups/User Groups',
            'available_groups/Not In Groups',
            'is_superuser/Super User',
            'join_date/Joined',
        ],
        title="Users",
        )

def update(gvar):
    """
    Modify the specified user.
    """

    mandatory = ['-un']
    required = []
    optional = ['-g', '-gn', '-go', '-H', '-h', '-SU', '-s', '-ucn', '-upw', '-v', '-x509', '-xA']

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
        print('Error: "%s user update" requires at least one option to update.' % gvar['command_name'])
        exit(1)

    # Create the user.
    response = requests(
        gvar,
        '/user/update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

