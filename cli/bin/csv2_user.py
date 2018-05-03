from csv2_common import requests, show_table

import json

def add(gvar):
    """
    Add a csv2 user.
    """

    # Check for mandatory arguments.
    _missing = []
    if 'target-user' not in gvar['user_settings']:
        _missing.append('-U|--target-user')

    if 'target-password' not in gvar['user_settings']:
        _missing.append('-P|--target-password')

    if 'target-common-name' not in gvar['user_settings']:
        _missing.append('-C|--target-common-name')

    if _missing:
        print('Error: "csv2 user add" requires the following parameters: %s' % _missing)
        exit(1)

    # If a target password prompt was requested (-P .), prompt for password.
    if gvar['user_settings']['target-password'] == '.':
        gvar['user_settings']['target-password'] = getpass('Enter target password: ')

    # Create the user.
    response = requests(
        gvar,
        '/user/create/',
        form_data = {
            'username': gvar['user_settings']['target-user'],
            'password1': gvar['user_settings']['target-password'],
            'password2': gvar['user_settings']['target-password'],
            'common_name': gvar['user_settings']['target-common-name'],
            'is_superuser': gvar['user_settings']['super-user'],
            }
        )
    
    if response['message']:
        print(response['message'])

def delete(gvar):
    """
    Delete a csv2 user.
    """

    # Check for mandatory arguments.
    _missing = []
    if 'target-user' not in gvar['user_settings']:
        _missing.append('-U|--target-user')

    if _missing:
        print('Error: "csv2 user delete" requires the following parameters: %s' % _missing)
        exit(1)

    # Retrieve Cookie/CSRF and check that the target user exists.
    response = requests(gvar, '/user/list/')
    _user_found = False
    for row in response['user_list']:
      if row['pk'] == gvar['user_settings']['target-user']:
        _user_found = True
        break
    
    if not _user_found:
        print('Error: "csv2 user delete" cannot delete "%s", user doesn\'t exist.' % gvar['user_settings']['target-user'])
        exit(1)

    # Confirm user delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete user "%s"? (yes|..)' % gvar['user_settings']['target-user'])
        _reply = input()
        if _reply != 'yes':
          print('csv2 user delete "%s" cancelled.' % gvar['user_settings']['target-user'])
          exit(0)

    # Delete the user.
    response = requests(
        gvar,
        '/user/delete/',
        form_data = {
            'username': gvar['user_settings']['target-user'],
            }
        )
    
    if response['message']:
        print(response['message'])

def list(gvar):
    """
    List csv2 users.
    """

    response = requests(gvar, '/user/list/')
    show_table(
        gvar,
        response['user_list'],
        [
            'pk/User',
            'cert_cn/Common Name',
            'password/Passsword',
            'is_superuser/Superuser',
            'join_date/Created',
            'active_group/Group',
        ],
        )

if __name__ == "__main__":
    main(sys.argv)
