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
    '-ga': 'cacertificate',
    '-vc': 'cores',
    '-vk': 'keyname',
    '-vr': 'ram',
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

def _create(gvar):
    """
    Create a cloud in the active group.
    """

    # Check for missing arguments or help required.
    form_data = _check_keys(
        gvar,
        'cloud create',
        ['-ca', '-ck', '-cn', '-cp', '-cr', '-ct', '-cu'],
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
    _check_keys(gvar, 'cloud delete', ['-cn'], ['-g', '-xA'])

    # Retrieve Cookie/CSRF and check that the target user exists.
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
    _check_keys(gvar, 'cloud list', [], ['-cn', '-g', '-ok', '-xA'])

    # Retrieve data (possibly after changing the group).
    response = __request(gvar, '/cloud/list/')

    # Filter response as requested (or not).
    cloud_list = __filter_by_cloud_name(gvar, json.loads(response['cloud_list']))

    # Print report
    print('Active User: %s, Active Group: %s, User\'s Groups: %s' % (response['active_user'], response['active_group'], response['user_groups']))
    if gvar['command_args']['only-keys']:
        _show_table(
            gvar,
            cloud_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
            ],
            )
    else:
        _show_table(
            gvar,
            cloud_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'authurl/URL',
                'project/Project',
                'username/User',
                'password/Password',
                'keyname/Keyname',
                'cacertificate/CA Certificate',
                'region/Region',
                'user_domain_name/User Domain',
                'project_domain_name/Project Domain',
                'cloud_type/Cloud Type',
                'cores_ctl/Cores (Control)',
                'cores_max/Core (Max)',
                'cores_used/Core (Used)',
                'ram_ctl/RAM (Control)',
                'ram_max/RAM (Max)',
                'ram_used/RAM (Used)',
                'instances_max/Instances (Max)',
                'instances_used/Instances (Used)',
                'floating_ips_max/Floating IPs (Max)',
                'floating_ips_used/Floating IPs (Used)',
                'security_groups_max/Security Groups (Max)',
                'security_groups_used/Security Groups (Used)',
                'server_groups_max/Server Groups (Max)',
                'server_groups_used/Server Groups (Used)',
                'image_meta_max/Image Metadata (Max)',
                'keypairs_max/Keypairs (Max)',
                'personality_max/Personality (Max)',
                'personality_size_max/Personality Size (Max)',
                'security_group_rules_max/Security Group Rules (Max)',
                'server_group_members_max/Security Group Members (Max)',
                'server_meta_max/Server Metadata (Max)',
            ],
            )

def _modify(gvar):
    """
    Modify a cloud in the active group.
    """

def _status(gvar):
    """
    List cloud status for the active group.
    """

    # Check for missing arguments or help required.
    _check_keys(gvar, 'cloud status', [], ['-cn', '-g', '-ok', '-xA'])

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

