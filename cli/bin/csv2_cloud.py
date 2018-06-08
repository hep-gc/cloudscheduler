from csv2_common import check_keys, requests, show_header, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-ca':  'authurl',
    '-cpw': 'password',
    '-cn':  'cloud_name',
    '-cp':  'project',
    '-cr':  'region',
    '-ct':  'cloud_type',
    '-cu':  'username',
    '-cP':  'project_domain_name',
    '-cU':  'user_domain_name',
    '-g':   'group',
    '-ga':  'cacertificate',
    '-vc':  'cores_ctl',
    '-vk':  'keyname',
    '-vr':  'ram_ctl',
    '-ye':  'enabled',
    '-ylo': 'yaml_list_option',
    '-ymt': 'mime_type',
    '-yn':  'yaml_name',
    '-yp':  'priority',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def _filter_by_cloud_name_and_or_yaml_name(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    if 'cloud-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['cloud_name'] != gvar['command_args']['cloud-name']:
                del(qs[_ix])

    if 'yaml-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['yaml_name'] != gvar['command_args']['yaml-name']:
                del(qs[_ix])

    return qs

def add(gvar):
    """
    Add a cloud to the active group.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-ca', '-cpw', '-cn', '-cp', '-cr', '-ct', '-cu'],
        [],
        ['-cP', '-cU', '-g', '-ga', '-vc', '-vk', '-vr'],
        key_map=KEY_MAP)

    # Create the cloud.
    response = requests(
        gvar,
        '/cloud/add/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def delete(gvar):
    """
    Delete a cloud from the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-cn'], [], ['-g'])

    # Check that the target cloud exists.
    response = requests(gvar, '/cloud/list/')
    _found = False
    for row in response['cloud_list']:
      if row['cloud_name'] == gvar['user_settings']['cloud-name']:
        _found = True
        break
   
    if not _found:
        print('Error: "%s cloud delete" cannot delete "%s", cloud doesn\'t exist in group "%s".' % (gvar['command_name'], gvar['user_settings']['cloud-name'], response['active_group']))
        exit(1)

    # Confirm cloud delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete cloud "%s::%s"? (yes|..)' % (response['active_group'], gvar['user_settings']['cloud-name']))
        _reply = input()
        if _reply != 'yes':
            print('%s cloud delete "%s::%s" cancelled.' % (gvar['command_name'], response['active_group'], gvar['user_settings']['cloud-name']))
            exit(0)

    # Delete the cloud.
    response = requests(
        gvar,
        '/cloud/delete/',
        form_data = {
            'cloud_name': gvar['user_settings']['cloud-name']
            }
        )
    
    if response['message']:
        print(response['message'])

def list(gvar):
    """
    List clouds for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-ok'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    cloud_list = _filter_by_cloud_name_and_or_yaml_name(gvar, response['cloud_list'])

    # Print report.
    show_header(gvar, response)

    if gvar['command_args']['only-keys']:
        show_table(
            gvar,
            cloud_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
            ],
            )
    else:
        show_table(
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
                'yaml_names/YAML Filenames',
                'cores_ctl/Cores (Control)',
                'cores_max/Cores (Max)',
                'cores_used/Cores (Used)',
                'cores_foreign/Foreign Cores',
                'cores_native/Native Cores',
                'ram_ctl/RAM (Control)',
                'ram_max/RAM (Max)',
                'ram_used/RAM (Used)',
                'ram_foreign/Foreign RAM',
                'ram_native/Native RAM',
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

def status(gvar):
    """
    List cloud status for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-ok'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/status/')

    # Filter response as requested (or not).
    status_list = _filter_by_cloud_name_and_or_yaml_name(gvar, response['status_list'])

    # Print report
    show_header(gvar, response)

    if gvar['command_args']['only-keys']:
        show_table(
            gvar,
            status_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
            ],
            )
    else:
        show_table(
            gvar,
            status_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'idle_cores/Idle Cores',
                'idle_ram/Idle RAM',
                'VMs',
                'VMs_unregistered/VMs Unregistered',
                'VMs_running/VMs Running',
                'VMs_retiring/VMs Retiring',
                'VMs_manual/VMs Manual',
                'VMs_in_error/VMs in Error',
                'VMs_other/VMs Other',
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

def update(gvar):
    """
    Modify a cloud in the active group.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-cn'],
        [],
        ['-ca', '-cpw', '-cP', '-cp', '-cr', '-ct', '-cU', '-cu', '-g', '-ga', '-vc', '-vk', '-vr'],
        key_map=KEY_MAP)

    if len(form_data) < 2:
        print('Error: "%s cloud update" requires at least one option to modify.' % gvar['command_name'])
        exit(1)

    # Create the cloud.
    response = requests(
        gvar,
        '/cloud/update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def yaml_delete(gvar):
    """
    Delete a cloud/YAML file.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-cn', '-yn'], [], ['-g'])

    # Check that the target cloudYAML file exists.
    response = requests(gvar, '/cloud/list/')
    _found = False
    for row in response['cloud_list']:
        if row['cloud_name'] == gvar['user_settings']['cloud-name']:
            yaml_names = row['yaml_names'].split(',')
            for yaml_name in yaml_names:
                if row['cloud_name'] == gvar['user_settings']['cloud-name']:
                    _found = True
                    break
   
    if not _found:
        print('Error: "%s cloud yaml-delete" cannot delete "%s::%s::%s", file doesn\'t exist.' % (gvar['command_name'], response['active_group'], gvar['user_settings']['cloud-name'], gvar['user_settings']['yaml-name']))
        exit(1)

    # Confirm cloud/YAML file delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete the YAML file "%s::%s::%s"? (yes|..)' % (response['active_group'], gvar['user_settings']['cloud-name'], gvar['user_settings']['yaml-name']))
        _reply = input()
        if _reply != 'yes':
            print('%s cloud yaml-delete "%s::%s::%s" cancelled.' % (gvar['command_name'], response['active_group'], gvar['user_settings']['cloud-name'], gvar['user_settings']['yaml-name']))
            exit(0)

    # Delete the cloud/YAML file.
    response = requests(
        gvar,
        '/cloud/yaml-delete/',
        form_data = {
            'cloud_name': gvar['user_settings']['cloud-name'],
            'yaml_name': gvar['user_settings']['yaml-name'],
            }
        )
    
    if response['message']:
        print(response['message'])

def yaml_edit(gvar):
    """
    Edit the specified cloud/YAML file.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-cn', '-yn'], ['-te'], ['-g'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/yaml-fetch/%s::%s::%s' % (gvar['active_group'], gvar['user_settings']['cloud-name'], gvar['user_settings']['yaml-name']))

    # Ensure the fetch directory structure exists.
    fetch_dir = '%s/.csv2/%s/files/%s/%s/yaml' % (
        gvar['home_dir'],
        gvar['server'],
        response['group_name'],
        response['cloud_name'] 
        )

    if not os.path.exists(fetch_dir):
        os.makedirs(fetch_dir, mode=0o700)  

    # Write the reference copy.
    fd = open('%s/.%s.yaml' % (fetch_dir, response['yaml_name']), 'w')
    fd.write(response['yaml'])
    fd.close()

    # Write the edit copy.
    fd = open('%s/%s.yaml' % (fetch_dir, response['yaml_name']), 'w')
    fd.write(response['yaml'])
    fd.close()

    p = Popen([gvar['user_settings']['text-editor'], '%s/%s.yaml' % (fetch_dir, response['yaml_name'])])
    p.communicate()

    if filecmp.cmp(
        '%s/.%s.yaml' % (fetch_dir, response['yaml_name']),
        '%s/%s.yaml' % (fetch_dir, response['yaml_name'])
        ):
        print('%s cloud yaml-edit "%s::%s::%s" completed, no changes.' % (gvar['command_name'], response['group_name'], gvar['user_settings']['cloud-name'], gvar['user_settings']['yaml-name']))
        exit(0)

    # Verify the changed YAML file.
    form_data = {
        **verify_yaml_file('%s/%s.yaml' % (fetch_dir, response['yaml_name'])),
        'group_name': response['group_name'],
        'cloud_name': response['cloud_name'],
        'yaml_name': response['yaml_name'],
        }

    # Replace the YAML file.
    response = requests(
        gvar,
        '/cloud/yaml-update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def yaml_list(gvar):
    """
    List clouds for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-ok', '-ylo', '-yn'])

    # Retrieve data (possibly after changing the group).
    if 'yaml-list-option' in gvar['user_settings'] and gvar['user_settings']['yaml-list-option'] == 'merge':
        response = requests(gvar, '/cloud/yaml-list/', {'yaml_list_option': 'merge'})
    else:
        response = requests(gvar, '/cloud/yaml-list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    cloud_yaml_list = _filter_by_cloud_name_and_or_yaml_name(gvar, response['cloud_yaml_list'])

    # Print report.
    show_header(gvar, response)

    if gvar['command_args']['only-keys']:
        show_table(
            gvar,
            cloud_yaml_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'yaml_name/YAML Filename',
            ],
            )
    elif 'yaml-list-option' in gvar['user_settings'] and gvar['user_settings']['yaml-list-option'] == 'merge':
        show_table(
            gvar,
            cloud_yaml_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'type/Type',
                'priority/priority',
                'yaml_name/YAML Filename',
                ],
            )
    else:
        show_table(
            gvar,
            cloud_yaml_list,
            [
                'group_name/Group',
                'cloud_name/Cloud',
                'yaml_name/YAML Filename',
                'enabled/Enabled',
                'priority/Priority',
                'mime_type/MIME Type',
            ],
            )

def yaml_load(gvar):
    """
    Load a new cloud/YAML file.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-cn', '-f', '-yn'],
        [],
        ['-g', '-ye', '-ymt', '-yp'],
        key_map=KEY_MAP
        )

    if not os.path.exists(gvar['user_settings']['file-path']):
        print('Error: The specified YAML file "%s" does not exist.' % gvar['user_settings']['file-path'])
        exit(1)

    # Replace the YAML file.
    response = requests(
        gvar,
        '/cloud/yaml-add/',
        {
            **form_data,
            **verify_yaml_file(gvar['user_settings']['file-path']),
            }
        )
    
    if response['message']:
        print(response['message'])

def yaml_update(gvar):
    """
    Modify a cloud in the active group.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-cn', '-yn'],
        [],
        ['-g', '-ye', '-ymt', '-yp'],
        key_map=KEY_MAP
        )

    if len(form_data) < 3:
        print('Error: "%s cloud yaml-update" requires at least one option to modify.' % gvar['command_name'])
        exit(1)

    # Update the YAML file information.
    response = requests(
        gvar,
        '/cloud/yaml-update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

