from csv2_common import check_keys, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-ca':  'authurl',
    '-ce':  'enabled',
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
    '-me':  'enabled',
    '-mmt': 'mime_type',
    '-mn':  'metadata_name',
    '-mp':  'priority',
    '-vc':  'cores_ctl',
    '-vf':  'vm_flavor',
    '-vi':  'vm_image',
    '-vk':  'keyname',
    '-vka': 'vm_keep_alive',
    '-vr':  'ram_ctl',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def _filter_by_cloud_name_and_or_metadata_name(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    if 'cloud-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['cloud_name'] != gvar['command_args']['cloud-name']:
                del(qs[_ix])

    if 'metadata-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['metadata_name'] != gvar['command_args']['metadata-name']:
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
        ['-cP', '-cU', '-g', '-ga', '-vc', '-vk', '-vr', '-ce', '-vka', '-vi', '-vf' '-s', '-xA', '-h', '-H'],
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
    check_keys(gvar, ['-cn'], [], ['-g', '-s', '-xA', '-h', '-H'])

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
    check_keys(gvar, [], [], ['-cn', '-g', '-ok', '-r', '-V', '-VC', '-NV', '-s', '-xA', '-h', '-H'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    cloud_list = _filter_by_cloud_name_and_or_metadata_name(gvar, response['cloud_list'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        cloud_list,
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'enabled/Enabled',
            'authurl/URL',
            'project_domain_name/Project Domain',
            'project/Project',
            'user_domain_name/User Domain',
            'username/User',
            'region/Region',
            'cloud_type/Cloud Type',
            'keyname/Keyname',
            'cores_max/Cores',
            'ram_max/RAM',
            'vm_flavor/VM Flavor',
            'vm_image/VM Image',
            'vm_keep_alive/VM Keep Alive',
            'cacertificate/CA Certificate',
            'metadata_names/Metadata Filenames',
            'instances_max/Maximum/Instances',
            'instances_used/Used/Instances',
            'floating_ips_max/Maximum/Floating IPs',
            'floating_ips_used/Used/Floating IPs',
            'security_groups_max/Maximum/Security Groups',
            'security_groups_used/Used/Security Groups',
            'server_groups_max/Maximum/Server Groups',
            'server_groups_used/Used/Server Groups',
            'image_meta_max/Image Metadata',
            'keypairs_max/Keypairs',
            'personality_max/Personality',
            'personality_size_max/Personality Size',
            'security_group_rules_max/Security Group Rules',
            'server_group_members_max/Security Group Members',
            'server_meta_max/Server Metadata',
            ],
        title="Clouds:",
        )

def status(gvar):
    """
    List cloud status for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-o', '-ok', '-r', '-V', '-VC', '-NV', '-s', '-xA', '-h', '-H'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/status/')

    # Filter response as requested (or not).
    cloud_status_list = _filter_by_cloud_name_and_or_metadata_name(gvar, response['cloud_status_list'])

    # Print report
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['job_status_list'],
        [
            'group_name/Group,k',
            'Jobs',
            'Idle',
            'Running',
            'Completed',
            'Other',
        ],
        title="Job status:",
        )

    show_table(
        gvar,
        cloud_status_list,
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'enabled/Enabled/Defaults',
            'default_flavor/Flavor/Defaults',
            'default_image/Image/Defaults',
            'vm_keep_alive/Keep Alive/Defaults',
            'VMs/Total/VMs',
            'VMs_unregistered/Unregistered/VMs',
            'VMs_running/Running/VMs',
            'VMs_retiring/Retiring/VMs',
            'VMs_manual/Manual/VMs',
            'VMs_in_error/Error/VMs',
            'VMs_other/Other/VMs',
            'cores_max/Total/Cores',
            'cores_ctl/Setting/Cores',
            'cores_idle/Idle/Cores',
            'cores_native/Used/Cores',
            'ram_max/Total/RAM',
            'ram_ctl/Setting/RAM',
            'ram_idle/Idle/RAM',
            'ram_native/Used/RAM',
            'slots_max/Total/Slots',
            'slots_used/Used/Slots',
            'Foreign_VMs/VMs/Foreign',
            'cores_foreign/Cores/Foreign',
            'ram_foreign/RAM/Foreign',
        ],
        title="Cloud status:",
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
        ['-ca', '-cpw', '-cP', '-cp', '-cr', '-ct', '-cU', '-cu', '-g', '-ga', '-vc', '-vk', '-vr', '-ce', '-vka', '-vi', '-vf', '-s', '-xA', '-h', '-H'],
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

def metadata_collation(gvar):
    """
    List cloud metadata collation for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-ok', '-r', '-V', '-VC', '-NV', '-s', '-xA', '-h', '-H'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/metadata-collation/')
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    cloud_metadata_list = _filter_by_cloud_name_and_or_metadata_name(gvar, response['cloud_metadata_list'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        cloud_metadata_list,
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'metadata_name/Metadata Filename,k',
            'type/Type',
            'priority/priority',
            ],
        title="Clouds/Metadata Collation:",
        )

def metadata_delete(gvar):
    """
    Delete a cloud metadata file.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-cn', '-mn'], [], ['-g', '-s', '-xA', '-h', '-H'])

    # Check that the target cloud metadata file exists.
    response = requests(gvar, '/cloud/list/')
    _found = False
    for row in response['cloud_list']:
        if row['cloud_name'] == gvar['user_settings']['cloud-name']:
            metadata_names = row['metadata_names'].split(',')
            for metadata_name in metadata_names:
                if row['cloud_name'] == gvar['user_settings']['cloud-name']:
                    _found = True
                    break
   
    if not _found:
        print('Error: "%s cloud metadata-delete" cannot delete "%s::%s::%s", file doesn\'t exist.' % (gvar['command_name'], response['active_group'], gvar['user_settings']['cloud-name'], gvar['user_settings']['metadata-name']))
        exit(1)

    # Confirm cloud metadata file delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete the metadata file "%s::%s::%s"? (yes|..)' % (response['active_group'], gvar['user_settings']['cloud-name'], gvar['user_settings']['metadata-name']))
        _reply = input()
        if _reply != 'yes':
            print('%s cloud metadata-delete "%s::%s::%s" cancelled.' % (gvar['command_name'], response['active_group'], gvar['user_settings']['cloud-name'], gvar['user_settings']['metadata-name']))
            exit(0)

    # Delete the cloud metadata file.
    response = requests(
        gvar,
        '/cloud/metadata-delete/',
        form_data = {
            'cloud_name': gvar['user_settings']['cloud-name'],
            'metadata_name': gvar['user_settings']['metadata-name'],
            }
        )
    
    if response['message']:
        print(response['message'])

def metadata_edit(gvar):
    """
    Edit the specified cloud metadata file.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-cn', '-mn'], ['-te'], ['-g', '-s', '-xA', '-h', '-H'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/metadata-fetch/%s::%s' % (gvar['user_settings']['cloud-name'], gvar['user_settings']['metadata-name']))

    # Ensure the fetch directory structure exists.
    fetch_dir = '%s/.csv2/%s/files/%s/%s/metadata' % (
        gvar['home_dir'],
        gvar['server'],
        response['group_name'],
        response['cloud_name'] 
        )

    if not os.path.exists(fetch_dir):
        os.makedirs(fetch_dir, mode=0o700)  

    # Write the reference copy.
    fd = open('%s/.%s' % (fetch_dir, response['metadata_name']), 'w')
    fd.write(response['metadata'])
    fd.close()

    # Write the edit copy.
    fd = open('%s/%s' % (fetch_dir, response['metadata_name']), 'w')
    fd.write(response['metadata'])
    fd.close()

    p = Popen([gvar['user_settings']['text-editor'], '%s/%s' % (fetch_dir, response['metadata_name'])])
    p.communicate()

    if filecmp.cmp(
        '%s/.%s' % (fetch_dir, response['metadata_name']),
        '%s/%s' % (fetch_dir, response['metadata_name'])
        ):
        print('%s cloud metadata-edit "%s::%s::%s" completed, no changes.' % (gvar['command_name'], response['group_name'], gvar['user_settings']['cloud-name'], gvar['user_settings']['metadata-name']))
        exit(0)

    # Verify the changed metadata file.
    form_data = {
        **verify_yaml_file('%s/%s' % (fetch_dir, response['metadata_name'])),
        'group_name': response['group_name'],
        'cloud_name': response['cloud_name'],
        'metadata_name': response['metadata_name'],
        }

    # Replace the metadata file.
    response = requests(
        gvar,
        '/cloud/metadata-update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def metadata_list(gvar):
    """
    List cloud metadata for the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-cn', '-g', '-ok', '-mn', '-r', '-V', '-VC', '-NV', '-s', '-xA', '-h', '-H'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/metadata-list/')
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    cloud_metadata_list = _filter_by_cloud_name_and_or_metadata_name(gvar, response['cloud_metadata_list'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        cloud_metadata_list,
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'metadata_name/Metadata Filename,k',
            'enabled/Enabled',
            'priority/Priority',
            'mime_type/MIME Type',
        ],
        title="Clouds/Metadata:",
        )

def metadata_load(gvar):
    """
    Load a new cloud metadata file.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-cn', '-f', '-mn'],
        [],
        ['-g', '-me', '-mmt', '-mp', '-s', '-xA', '-h', '-H'],
        key_map=KEY_MAP
        )

    if not os.path.exists(gvar['user_settings']['file-path']):
        print('Error: The specified metadata file "%s" does not exist.' % gvar['user_settings']['file-path'])
        exit(1)

    # Replace the metadata file.
    response = requests(
        gvar,
        '/cloud/metadata-add/',
        {
            **form_data,
            **verify_yaml_file(gvar['user_settings']['file-path']),
            }
        )
    
    if response['message']:
        print(response['message'])

def metadata_update(gvar):
    """
    Modify a cloud in the active group.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-cn', '-mn'],
        [],
        ['-g', '-me', '-mmt', '-mp', '-s', '-xA', '-h', '-H'],
        key_map=KEY_MAP
        )

    if len(form_data) < 3:
        print('Error: "%s cloud metadata-update" requires at least one option to modify.' % gvar['command_name'])
        exit(1)

    # Update the metadata file information.
    response = requests(
        gvar,
        '/cloud/metadata-update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

