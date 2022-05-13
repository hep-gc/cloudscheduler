from csv2_common import check_keys, get_editor, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE
from csv2_base_metadata import base_metadata_save

import filecmp
import os

KEY_MAP = {
    '-gn':   'group_name',
    '-htcf': 'htcondor_fqdn',
    '-htch': 'htcondor_container_hostname',
    '-htcu': 'htcondor_other_submitters',
    '-me':   'enabled',
    '-mmt':  'mime_type',
    '-mn':   'metadata_name',
    '-mp':   'priority',
    '-jc':   'job_cpus',
    '-jd':   'job_disk',
    '-jed':  'job_scratch',
    '-jr':   'job_ram',
    '-js':   'job_swap',
    '-un':   'username',
    '-uo':   'user_option',
    '-vf':   'vm_flavor',
    '-vi':   'vm_image',
    '-vka':  'vm_keep_alive',
    '-vk':   'vm_keyname',
    '-vn':   'vm_network',
    '-vsg':  'vm_security_groups',
    '-pub':  'public_visibility',
    }

def _filter_by_group_name_and_or_metadata_name(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    if 'group-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['group_name'] != gvar['command_args']['group-name']:
                del(qs[_ix])

    if 'metadata-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['metadata_name'] != gvar['command_args']['metadata-name']:
                del(qs[_ix])

    return qs

def add(gvar):
    """
    Add a group to the active group.
    """

    mandatory = ['-gn']
    required = []
    optional = ['-g', '-H', '-h', '-htcf', '-htch', '-htcu', '-jc', '-jd', '-jr', '-js', '-NV', '-ok', '-pub', '-r', '-s', '-un', '-vf', '-vi', '-vka', '-vk', '-vn', '-vsg', '-v', '-x509', '-xA']


    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    # Create the group.
    response = requests(
        gvar,
        '/group/add/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def defaults(gvar):
    """
    Modify the specified group defaults.
    """

    mandatory = []
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-H', '-h', '-htcf', '-htch', '-htcu', '-jc', '-jd', '-jr', '-js', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-vf', '-vi', '-vka', '-vk', '-vn', '-vsg', '-w', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    # List the current defaults. If the form_data contains any optional fields,
    # those values will be updated before the list is retrieved.
    response = requests(
        gvar,
        '/group/defaults/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

    # Print report
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        response['defaults_list'],
        [
            'group_name/Group,k',
            'htcondor_fqdn/FQDN/HTCondor',
            'htcondor_container_hostname/Container Hostname/HTCondor',
            'htcondor_other_submitters/Other Submitters/HTCondor',
            'vm_flavor/Flavor/VM',
            'vm_image/Image/VM',
            'vm_keep_alive/Keep Alive/VM',
            'vm_keyname/Keyname/VM',
            'vm_network/Network/VM',
            'vm_security_groups/Security Groups/VM',
            'job_cpus/Cores/Job',
            'job_disk/Disk (GBs)/Job',
            'job_ram/RAM (MBs)/Job',
            'job_swap/Swap (GBs)/Job',
        ],
        title="Active Group Defaults",
    )

    show_table(
        gvar,
        response['flavor_list'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'name/Flavor',
            ],
        title="Flavors",
        optional=True,
        )

    show_table(
        gvar,
        response['image_list'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'name/Flavor',
            ],
        title="Images",
        optional=True,
        )

    show_table(
        gvar,
        response['keypairs_list'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'key_name/Key,k',
            'fingerprint/Fingerprint',
            'cloud_type/Cloud Type',
            ],
        title="Keypairs",
        optional=True,
        )

    show_table(
        gvar,
        response['network_list'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'name/Flavor',
            ],
        title="Networks",
        optional=True,
        )

    show_table(
        gvar,
        response['security_groups_list'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'name/Security Groups',
            ],
        title="Security Groups",
        optional=True,
        )

def delete(gvar):
    """
    Delete a group from the active group.
    """

    mandatory = ['-gn']
    required = []
    optional = ['-H', '-h','-s', '-v', '-x509', '-xA', '-Y']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Check that the target group exists.
    response = requests(gvar, '/group/list/')
    _found = False
    for row in response['group_list']:
      if row['group_name'] == gvar['user_settings']['group-name']:
        _found = True
        break
   
    if not _found:
        print('Error: "%s group delete" cannot delete "%s", group doesn\'t exist.' % (gvar['command_name'], gvar['user_settings']['group-name']))
        exit(1)

    # Confirm group delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete group "%s"? (yes|..)' % gvar['user_settings']['group-name'])
        _reply = input()
        if _reply != 'yes':
          print('%s group delete "%s" cancelled.' % (gvar['command_name'], gvar['user_settings']['group-name']))
          exit(0)

    # Delete the group.
    response = requests(
        gvar,
        '/group/delete/',
        form_data = {
            'group_name': gvar['user_settings']['group-name']
            }
        )
    
    if response['message']:
        print(response['message'])

def list(gvar):
    """
    List groups.
    """

    mandatory = []
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-gn', '-H', '-h', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/group/list/')

    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    group_list = _filter_by_group_name_and_or_metadata_name(gvar, response['group_list'])

    # Print report
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        group_list,
        [
            'group_name/Group,k',
            'htcondor_fqdn/FQDN/HTCondor',
            'htcondor_container_hostname/Container Hostname/HTCondor',
            'htcondor_other_submitters/Other Submitters/HTCondor',
            'public_visibility/Public Visiblity',
            'metadata_names/Metadata Filenames',
            ],
        title="Groups",
        )

def update(gvar):
    """
    Modify the specified group.
    """

    mandatory = ['-gn']
    required = []
    optional = ['-g', '-H', '-h', '-htcf', '-htch', '-htcu', '-jc', '-jd', '-jr', '-js', '-pub', '-NV', '-ok', '-r', '-s', '-un', '-uo', '-vf', '-vi', '-vka', '-vk', '-vn', '-vsg', '-v', '-x509', '-xA']

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
        print('Error: "%s group update" requires at least one option to update.' % gvar['command_name'])
        exit(1)

    # Create the group.
    response = requests(
        gvar,
        '/group/update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def metadata_delete(gvar):
    """
    Delete a group metadata file.
    """

    mandatory = ['-mn']
    required = []
    optional = ['-g', '-H', '-h', '-s', '-v', '-x509', '-xA', '-Y']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Check that the target group metadata file exists.
    response = requests(gvar, '/group/metadata-list/')

    if not any(row['metadata_name'] == gvar['user_settings']['metadata-name'] for row in response['group_metadata_list']):
        print('Error: "%s group metadata-delete" cannot delete "%s::%s", file doesn\'t exist.' % (gvar['command_name'], response['active_group'], gvar['user_settings']['metadata-name']))
        exit(1)

    # Confirm group metadata file delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete the metadata file "%s::%s"? (yes|..)' % (response['active_group'], gvar['user_settings']['metadata-name']))
        _reply = input()
        if _reply != 'yes':
            print('%s group metadata-delete "%s::%s" cancelled.' % (gvar['command_name'], response['active_group'], gvar['user_settings']['metadata-name']))
            exit(0)

    # Delete the group metadata file.
    response = requests(
        gvar,
        '/group/metadata-delete/',
        form_data = {
            'metadata_name': gvar['user_settings']['metadata-name'],
            }
        )
    
    if response['message']:
        print(response['message'])

def metadata_edit(gvar):
    """
    Edit the specified group metadata file.
    """

    mandatory = ['-mn']
    required = ['-te']
    optional = ['-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/group/metadata-fetch/', query_data={'metadata_name': gvar['user_settings']['metadata-name']})

    # Ensure the fetch directory structure exists.
    fetch_dir = '%s/.csv2/%s/files/%s/metadata' % (
        gvar['home_dir'],
        gvar['pid_defaults']['server'],
        response['group_name'],
        )

    if not os.path.exists(fetch_dir):
        os.makedirs(fetch_dir, mode=0o700)  

    # Write the reference copy.
    fd = open('%s/.%s' % (fetch_dir, response['metadata_name']), 'w')
#   fd.write('# metadata_enabled: %s, metadata_mime_type: %s\n%s' % (response['metadata_enabled'], response['metadata_mime_type'], response['metadata']))
    fd.write(response['metadata'])
    fd.close()

    # Write the edit copy.
    fd = open('%s/%s' % (fetch_dir, response['metadata_name']), 'w')
#   fd.write('# metadata_enabled: %s, metadata_mime_type: %s\n%s' % (response['metadata_enabled'], response['metadata_mime_type'], response['metadata']))
    fd.write(response['metadata'])
    fd.close()

    # Edit the metadata file.
    p = Popen(get_editor(gvar) + ['%s/%s' % (fetch_dir, response['metadata_name'])])
    p.communicate()

    if filecmp.cmp(
        '%s/.%s' % (fetch_dir, response['metadata_name']),
        '%s/%s' % (fetch_dir, response['metadata_name'])
        ):
        print('%s group metadata-edit "%s::%s" completed, no changes.' % (gvar['command_name'], response['group_name'],  response['metadata_name']))
        exit(0)

    # Verify the changed metadata file.
    form_data = {
        **verify_yaml_file('%s/%s' % (fetch_dir, response['metadata_name'])),
        'metadata_name': response['metadata_name'],
        }

    # Replace the metadata file.
    response = requests(
        gvar,
        '/group/metadata-update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def metadata_list(gvar):
    """
    List clouds for the active group.
    """

    mandatory = []
    required = []
    optional = ['-CSEP', '-CSV', '-g', '-H', '-h', '-mn', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/group/metadata-list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    group_metadata_list = _filter_by_group_name_and_or_metadata_name(gvar, response['group_metadata_list'])

    # Print report.
    show_active_user_groups(gvar, response)

    show_table(
        gvar,
        group_metadata_list,
        [
            'group_name/Group,k',
            'metadata_name/Metadata Filename,k',
            'enabled/Enabled',
            'priority/Priority',
            'mime_type/MIME Type',
            'checksum/Checksum'
        ],
        title="Active Group/Metadata",
        )

def metadata_load(gvar):
    """
    Load a new group metadata file.
    """

    mandatory = ['-f', '-mn']
    required = []
    optional = ['-F', '-g', '-H', '-h', '-me', '-mmt', '-mp', '-s', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    if not os.path.exists(gvar['user_settings']['file-path']):
        print('Error: The specified metadata file "%s" does not exist.' % gvar['user_settings']['file-path'])
        exit(1)

    # Set the default load command.
    url_command = '/group/metadata-add/'

    # If the "--force" option is used, change the url_command to overwrite the metadata if it already exists.
    if gvar['user_settings']['force']:
        # Replace the metadata file.
        response = requests(
            gvar,
            '/group/metadata-query/',
            query_data={
                'metadata_name': form_data['metadata_name'],
                }
            )
        
        if response['message']:
            print(response['message'])

        if response['metadata_exists']:
            url_command = '/group/metadata-update/'

    # Replace the metadata file.
    response = requests(
        gvar,
        url_command,
        {
            **form_data,
            **verify_yaml_file(gvar['user_settings']['file-path']),
            }
        )
    
    if response['message']:
        print(response['message'])

def metadata_save(gvar):
    """
    boilerplate code for base_metadata_save
    """
    return base_metadata_save(gvar, context='group')

def metadata_update(gvar):
    """
    Update metadata fiel information.
    """

    mandatory = ['-mn']
    required = []
    optional = ['-g', '-H', '-h', '-me', '-mmt', '-mp', '-s', '-v', '-x509', '-xA']

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
        print('Error: "%s group metadata-update" requires at least one option to modify.' % gvar['command_name'])
        exit(1)

    # Create the cloud.
    response = requests(
        gvar,
        '/group/metadata-update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

