from csv2_common import _check_keys, _requests, _show_table

import json

KEY_MAP = {
    '-ca': 'authurl',
    '-ck': 'password',
    '-cn': 'cloud_name',
    '-cp': 'project',
    '-cr': 'region',
    '-ct': 'cloud_type',
    '-cu': 'username',
    '-cP': 'project_domain_name',
    '-cU': 'user_domain_name',
    '-g':  'group',
    '-ga': 'cacertificate',
    '-vc': 'cores_ctl',
    '-vk': 'keyname',
    '-vr': 'ram_ctl',
    }

def __filter_by_cloud_name(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    if 'cloud-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['cloud_name'] != gvar['command_args']['cloud-name']:
                del(qs[_ix])

    return qs

def __request(gvar, request):
    """
    Internal function to make a server request. If the user specified a group on the command
    line, the server's active group will be changed before the query is made.
    """

    # Perform group change and then list clouds.
    if 'group' in gvar['command_args']:
        response = _requests(gvar, '/cloud/prepare/')

        return _requests(gvar,
            request,
            form_data = {
                'group': gvar['user_settings']['group'],
                }
          )

    # List clouds for the currently active group..
    else:
        return _requests(gvar, request)

def _add(gvar):
    """
    Add a cloud to the active group.
    """

    # Check for missing arguments or help required.
    form_data = _check_keys(
        gvar,
        ['-ca', '-ck', '-cn', '-cp', '-cr', '-ct', '-cu'],
        [],
        ['-cP', '-cU', '-g', '-ga', '-vc', '-vk', '-vr'],
        key_map=KEY_MAP)

    form_data['action'] = 'add'

    # Retrieve Cookie/CSRF.
    response = _requests(gvar, '/cloud/prepare/')

    # Create the cloud.
    response = _requests(
        gvar,
        '/cloud/modify/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def _delete(gvar):
    """
    Delete a cloud from the active group.
    """

    # Check for missing arguments or help required.
    _check_keys(gvar, ['-cn'], [], ['-g'])

    # Check that the target cloud exists.
    response = __request(gvar, '/cloud/list/')
    _found = False
    for row in json.loads(response['cloud_list']):
      if row['cloud_name'] == gvar['user_settings']['cloud-name']:
        _found = True
        break
   
    if not _found:
        print('Error: "csv2 cloud delete" cannot delete "%s", cloud doesn\'t exist in group "%s".' % (gvar['user_settings']['cloud-name'], response['active_group']))
        exit(1)

    # Confirm cloud delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete cloud "%s" in group "%s"? (yes|..)' % (gvar['user_settings']['cloud-name'], response['active_group']))
        _reply = input()
        if _reply != 'yes':
          print('csv2 cloud delete "%s" cancelled.' % gvar['user_settings']['cloud-name'])
          exit(0)

    # Retrieve Cookie/CSRF.
    response = _requests(gvar, '/cloud/prepare/')

    # Delete the cloud.
    response = _requests(
        gvar,
        '/cloud/modify/',
        form_data = {
            'action': 'delete',
            'cloud_name': gvar['user_settings']['cloud-name']
            }
        )
    
    if response['message']:
        print(response['message'])

def _list(gvar):
    """
    List clouds for the active group.
    """

    # Check for missing arguments or help required.
    _check_keys(gvar, [], [], ['-ok'])

    # Retrieve data (possibly after changing the group).
    response = __request(gvar, '/group/list/')

    # Filter response as requested (or not).
    group_list = __filter_by_cloud_name(gvar, json.loads(response['group_list']))

    # Print report
    print('Active User: %s, Active Group: %s, User\'s Groups: %s' % (response['active_user'], response['active_group'], response['user_groups']))
    if gvar['command_args']['only-keys']:
        _show_table(
            gvar,
            group_list,
            [
                'group_name/Group',
            ],
            )
    else:
        _show_table(
            gvar,
            group_list,
            [
                'group_name/Group',
                'condor_central_manager/Central Manager',
                'yaml_name/YAML Name',
            ],
            )

def _modify(gvar):
    """
    Modify a cloud in the active group.
    """

    # Check for missing arguments or help required.
    form_data = _check_keys(
        gvar,
        ['-cn'],
        [],
        ['-ca', '-ck', '-cP', '-cp', '-cr', '-ct', '-cU', '-cu', '-g', '-ga', '-vc', '-vk', '-vr'],
        key_map=KEY_MAP)

    if len(form_data) < 2:
        print('Error: "csv2 cloud modify" requires at least one option to modify.')
        exit(1)

    form_data['action'] = 'modify'

    # Retrieve Cookie/CSRF.
    response = _requests(gvar, '/cloud/prepare/')

    # Create the cloud.
    response = _requests(
        gvar,
        '/cloud/modify/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def _status(gvar):
    """
    List cloud status for the active group.
    """

    # Check for missing arguments or help required.
    _check_keys(gvar, [], [], ['-cn', '-g', '-ok'])

    # Retrieve data (possibly after changing the group).
    response = __request(gvar, '/cloud/status/')

    # Filter response as requested (or not).
    status_list = __filter_by_cloud_name(gvar, json.loads(response['status_list']))

    # Print report
    print('Active User: %s, Active Group: %s, User\'s Groups: %s' % (response['active_user'], response['active_group'], response['user_groups']))
    if gvar['command_args']['only-keys']:
        _show_table(
            gvar,
            status_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
            ],
            )
    else:
        _show_table(
            gvar,
            status_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'VMs',
                'VMs_running/VMs_running',
                'VMs_retiring/VMs_retiring',
                'VMs_in_error/VMs in Error',
                'VMs_other/VMs_other',
                'Foreign_VMs/Foreign VMs',
                'Jobs',
                'Jobs_s0/Jobstat 0',
                'Jobs_s1/Jobstat 1',
                'Jobs_s2/Jobstat 2',
                'Jobs_s3/Jobstat 3',
                'Jobs_s4/Jobstat 4',
                'Jobs_s5/Jobstat 5',
                'Jobs_s6/Jobstat 6',
            ],
            )

