from csv2_common import _required_settings, _requests, _show_table

import json

def _cloud_list(gvar):
    """
    List clouds for the active group.
    """

    # Check for mandatory arguments.
    if 'group' in gvar['command_args']:
        response = _requests(gvar, '/cloud/prepare/')

        response = _requests(gvar,
            '/cloud/list/',
            form_data = {
                'group': gvar['user_settings']['group'],
                }
          )

    else:
        response = _requests(gvar, '/cloud/list/')

    print('Active User: %s, Active Group: %s, User\'s Groups: %s' % (response['active_user'], response['active_group'], response['user_groups']))
    _show_table(
        gvar,
        json.loads(response['cloud_list']),
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


def _cloud_status(gvar):
    """
    List cloud status for the active group.
    """

    # Check for mandatory arguments.
    if 'group' in gvar['command_args']:
#       response = _requests(gvar, '/cloud/list/')
        response = _requests(gvar, '/cloud/prepare/')

        response = _requests(gvar,
            '/cloud/status/',
            form_data = {
                'group': gvar['user_settings']['group'],
                }
          )

    else:
        response = _requests(gvar, '/cloud/status/')

    _show_table(
        gvar,
        json.loads(response['status_list']),
        [
            'group_name/Group',
            'cloud_name/Cloud',
            'VMs',
            'VMs_starting/VMs Starting',
            'VMs_running/VMs_running',
            'VMs_retiring/VMs_retiring',
            'VMs_other/VMs_other',
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

