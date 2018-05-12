from csv2_common import check_keys, requests, show_header, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-gn':   'group_name',
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

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-ucn', '-un', '-upw'],
        [],
        ['-gn'],
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

    # Check for missing arguments or help required.
    check_keys(gvar, ['-un'], [], [])

    # Check that the target user exists.
    response = requests(gvar, '/user/list/')
    _found = False
    for row in response['user_list']:
      if row['username'] == gvar['user_settings']['username']:
        _found = True
        break
   
    if not _found:
        print('Error: "csv2 user delete" cannot delete "%s", user doesn\'t exist.' % gvar['user_settings']['username'])
        exit(1)

    # Confirm user delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete user "%s"? (yes|..)' % gvar['user_settings']['username'])
        _reply = input()
        if _reply != 'yes':
          print('csv2 user delete "%s" cancelled.' % gvar['user_settings']['username'])
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

def group_add(gvar):
    """
    Add a group to the specified user.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-gn', '-un'],
        [],
        [],
        key_map=KEY_MAP)

    # Create the user.
    response = requests(
        gvar,
        '/user/group_add/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def group_delete(gvar):
    """
    Delete a group from the specified user.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-gn', '-un'],
        [],
        [],
        key_map=KEY_MAP)

    # Check that the target user exists.
    response = requests(gvar, '/user/list/')
    _found = False
    for row in response['user_list']:
      if row['username'] == gvar['user_settings']['username']:
        _found = True
        break
   
    if not _found:
        print('Error: "csv2 user delete" cannot delete "%s", user doesn\'t exist.' % gvar['user_settings']['username'])
        exit(1)

    # Confirm user delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete user::group "%s::%s"? (yes|..)' % (gvar['user_settings']['username'], gvar['user_settings']['group-name']))
        _reply = input()
        if _reply != 'yes':
          print('csv2 user::group delete "%s::%s" cancelled.' % (gvar['user_settings']['username'], gvar['user_settings']['group-name']))
          exit(0)

    # Delete the user/group.
    response = requests(
        gvar,
        '/user/group_delete/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def list(gvar):
    """
    List users.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-un', '-ok'])

    # Retrieve data (possibly after changing the user).
    response = requests(gvar, '/user/list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    user_list = _filter_by_user(gvar, response['user_list'])

    # Print report
    show_header(gvar, response)

    if gvar['command_args']['only-keys']:
        show_table(
            gvar,
            user_list,
            [
                'username/Username',
            ],
            )
    else:
        show_table(
            gvar,
            user_list,
            [
                'username/Username',
                'cert_cn/Common Name',
                'active_group/Active Group',
                'user_groups/User Groups',
                'available_groups/Not In Groups',
                'is_superuser/Super User',
                'join_date/Joined',
            ],
            )

def update(gvar):
    """
    Modify the specified user.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-un'],
        [],
        ['-SU', '-ucn', '-upw'],
        key_map=KEY_MAP)

    if len(form_data) < 2:
        print('Error: "csv2 user update" requires at least one option to update.')
        exit(1)

    # Create the user.
    response = requests(
        gvar,
        '/user/update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

