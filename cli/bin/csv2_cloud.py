from csv2_common import check_keys, get_editor, requests, show_active_user_groups, show_table, verify_yaml_file
from subprocess import Popen, PIPE
from csv2_base_metadata import base_metadata_save

import filecmp
import os

KEY_MAP = {
    '-bvt': 'vm_boot_volume_type',
    '-bvs': 'vm_boot_volume_size',
    '-bvc': 'vm_boot_volume_per_core',
    '-ca':  'authurl',
    '-ce':  'enabled',
    '-cfe': 'flavor_name',
    '-cfo': 'flavor_option',
    '-cn':  'cloud_name',
    '-cp':  'priority',
    '-cpw': 'password',
    '-cP':  'project',
    '-cr':  'region',
    '-csp': 'spot_price',
    '-ct':  'cloud_type',
    '-cU':  'username',
    '-cPD': 'project_domain_name',
    '-cPI': 'project_domain_id',
    '-cUD':  'user_domain_name',
    '-cUI': 'user_domain_id',
    '-cac':  'app_credentials',
    '-cas': 'app_credentials_secret',
    '-ui': 'userid',
    '-g':   'group',
    '-ga':  'cacertificate',
    '-gme': 'metadata_name',
    '-gmo': 'metadata_option',
    '-me':  'enabled',
    '-mmt': 'mime_type',
    '-mn':  'metadata_name',
    '-mp':  'priority',
    '-vbv': 'vm_boot_volume',
    '-vc':  'cores_ctl',
    '-vcs': 'cores_softmax',
    '-vf':  'vm_flavor',
    '-vi':  'vm_image',
    '-vka': 'vm_keep_alive',
    '-vk':  'vm_keyname',
    '-vn':  'vm_network',
    '-vr':  'ram_ctl',
    '-vsg':  'vm_security_groups',
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

    mandatory = ['-ca', '-cn', '-cP', '-cr', '-ct']
    required = []
    optional = ['-bvt', '-bvs', '-bvc', '-ce', '-cfe', '-cp', '-cPD', '-cPI', '-csp', '-cUD', '-cUI', '-cpw', '-cU', '-cac', '-cas', '-ui', '-g', '-ga', '-gme',  '-H', '-h', '-s', '-vbv', '-vc', '-vcs', '-vf', '-vi', '-vk', '-vka', '-vn', '-vr', '-vsg', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        mandatory,
        required,
        optional,
        key_map=KEY_MAP)

    auth_type = None
    if form_data.get('username') and form_data.get('password'):
        auth_type = "userpass"
    elif form_data.get('app_credentials') and form_data.get('app_credentials_secret'):
        auth_type = "app_creds"
    elif form_data.get('username') or form_data.get('password'):
        auth_type = "userpass"
    elif form_data.get('app_credentials') or form_data.get('app_credentials_secret'):
        auth_type = "app_creds"

    if auth_type == "app_creds":
        form_data['auth_type'] = 'app_creds'
        if not form_data.get('username'):
            form_data['username'] = ''
        if not form_data.get('password'):
            form_data['password'] = ''

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

    mandatory = ['-cn']
    required = []
    optional = ['-g', '-H', '-h', '-s', '-v', '-x509', '-xA', '-Y']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

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

    mandatory = []
    required = []
    optional = ['-cn', '-CSEP', '-CSV', '-g', '-H', '-h', '-ok', '-r', '-s', '-V', '-VC', '-NV', '-w', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

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
            'cloud_priority/Priority',
            'authurl/URL',
            'project/Name/Project',
            'project_domain_name/Domain Name/Project',
            'project_domain_id/Domain ID/Project',
            'username/Name/User',
            'user_domain_name/Domain Name/User',
            'user_domain_id/Domain ID/User',
            'region/Region',
            'spot_price/Spot Price',
            'cloud_type/Cloud Type',
            'cores_ctl/Control/Cores',
            'cores_softmax/SoftMax/Cores',
            'cores_max/Max/Cores',
            'ram_ctl/Control/RAM',
            'ram_max/Max/RAM',
            'vm_boot_volume/Boot Volume/Cloud Default',
            'vm_flavor/Flavor/Cloud Default',
            'vm_image/Image/Cloud Default',
            'vm_keep_alive/Keep Alive/Cloud Default',
            'vm_keyname/Keyname/Cloud Default',
            'vm_network/Network/Cloud Default',
            'vm_security_groups/Security Groups/Cloud Default',
            'cascading_vm_flavor/Flavor/Cascading Default',
            'cascading_vm_image/Image/Cascading Default',
            'cascading_vm_keep_alive/Keep Alive/Cascading Default',
            'cascading_vm_keyname/Keyname/Cascading Default',
            'cascading_vm_network/Network/Cascading Default',
            'cascading_vm_security_groups/Security Groups/Cascading Default',
            'cacertificate/CA Certificate',
            'flavor_exclusions/Flavor Exclusions/Cloud',
            'flavor_names/Flavors/Cloud',
            'group_exclusions/Group Exclusions/Metadata',
            'metadata_names/Filenames/Metadata',
            ],
        title="Clouds",
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

def status(gvar):
    """
    List cloud status for the active group.
    """

    mandatory = []
    required = []
    optional = ['-cn', '-CSEP', '-CSV', '-g', '-H', '-h', '-NV', '-o', '-ok', '-r', '-s', '-V', '-VC', '-v', '-w', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/status/')

    # Filter response as requested (or not).
    cloud_status_list = _filter_by_cloud_name_and_or_metadata_name(gvar, response['cloud_status_list'])

    # Print report
    show_active_user_groups(gvar, response)

    columns = [
        'group_name/Group,k',
        'Jobs',
        'Idle',
        'Running',
        'Completed',
        'Other',
        'foreign/Foreign',
        'htcondor_status/HTCondor/Status',
        'agent_status/Agent/Status',
        'htcondor_fqdn/HTCondor FQDN',
        'condor_days_left/Condor/Days Left on Certificates',
        'worker_days_left/Worker/Days Left on Certificates',
    ]

    if response['jobs_by_target_alias_flag']:
        columns.insert(1, 'target_alias/Target Alias,k')

    show_table(
        gvar,
        response['job_status_list'],
        columns,
        title="Job status",
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
            'keep_alive/Keep Alive/Defaults',
            'communication_up/Up/Communications',
            'communication_rt/Request Time/Communications',
            'VMs_quota/Quota/VMs',
            'VMs/Total/VMs',
            'VMs_starting/Starting/VMs',
            'VMs_unregistered/Unregistered/VMs',
            'VMs_idle/idle/VMs',
            'VMs_running/Running/VMs',
            'VMs_retiring/Retiring/VMs',
            'VMs_manual/Manual/VMs',
            'VMs_in_error/Error/VMs',
            'VMs_other/Other/VMs',
            'cores_quota/Quota/Cores',
            'cores_limit/Limit/Cores',
            'cores_ctl/Setting/Cores',
            'cores_idle/Idle/Cores',
            'cores_native/Used/Cores',
            'ram_quota/Quota/RAM',
            'ram_limit/Limit/RAM',
            'ram_ctl/Setting/RAM',
            'ram_idle/Idle/RAM',
            'ram_native/Used/RAM',
            'slot_count/Busy/Condor Slots',
            'slot_core_count/Busy Cores/Condor Slots',
            'slot_idle_core_count/Idle Cores/Condor Slots',
            'Foreign_VMs/VMs/Foreign',
            'cores_foreign/Cores/Foreign',
            'ram_foreign/RAM/Foreign',
        ],
        title="Cloud status",
        )

    show_table(
        gvar,
        response['flavor_slot_detail_summary'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'flavor/Flavor,k',
            'slot_type/Type/Slot',
            'slot_count/Count/Slot',
            'core_count/Core Count',
            ],
        title="Flavor Slot Detail Summary",
        optional=True,
        )

    show_table(
        gvar,
        response['flavor_slot_detail'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'flavor/Flavor,k',
            'slot_type/Type/Slot',
            'slot_id/ID/Slot',
            'slot_count/Count/Slot',
            'core_count/Core Count',
            ],
        title="Flavor Slot Detail",
        optional=True,
        )

    show_table(
        gvar,
        response['flavor_slot_summary'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'flavor/Flavor,k',
            'busy/Busy/Cores',
            'idle/Idle/Cores',
            'idle_percent/Idle Percent/Cores',
            ],
        title="Flavor Slot Summary",
        optional=True,
        )

    show_table(
        gvar,
        response['slot_detail_summary'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'slot_type/Type/Slot',
            'slot_count/Count/Slot',
            'core_count/Core Count',
            ],
        title="Slot Detail Summary",
        optional=True,
        )

    show_table(
        gvar,
        response['slot_detail'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'slot_type/Type/Slot',
            'slot_id/ID/Slot',
            'slot_count/Count/Slot',
            'core_count/Core Count',
            ],
        title="Slot Detail",
        optional=True,
        )

    show_table(
        gvar,
        response['slot_summary'],
        [
            'group_name/Group,k',
            'cloud_name/Cloud,k',
            'busy/Busy/Cores',
            'idle/Idle/Cores',
            'idle_percent/Idle Percent/Cores',
            ],
        title="Slot Summary",
        optional=True,
        )

def update(gvar):
    """
    Modify a cloud in the active group.
    """

    mandatory = ['-cn']
    required = []
    optional = ['-bvt', '-bvs', '-bvc', '-ca', '-ce', '-cfe', '-cfo', '-cpw', '-cp', '-cP', '-cPD', '-cPI', '-cr', '-csp', '-ct', '-cU', '-cac', '-cas', '-ui', '-cUD', '-cUI', '-g', '-ga', '-gme', '-gmo', '-H', '-h', '-s', '-vbv', '-vc', '-vcs', '-vf', '-vi', '-vk', '-vka', '-vn', '-vr', '-vsg', '-v', '-x509', '-xA']

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
        print('Error: "%s cloud update" requires at least one option to modify.' % gvar['command_name'])
        exit(1)

    if form_data.get('username') and form_data.get('password'):
        form_data['auth_type'] = 'userpass' 
    elif form_data.get('app_credentials') and form_data.get('app_credentials_secret'):
        form_data['auth_type'] = 'app_creds'

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

    mandatory = []
    required = []
    optional = ['-cn', '-CSEP', '-CSV', '-g', '-H', '-h', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

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
            'priority/Priority',
            'type/Type',
            ],
        title="Clouds/Metadata Collation",
        )

def metadata_delete(gvar):
    """
    Delete a cloud metadata file.
    """

    mandatory = ['-cn', '-mn']
    required = []
    optional = ['-g', '-H', '-h', '-s', '-v', '-x509', '-xA', '-Y']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

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

    mandatory = ['-cn', '-mn']
    required = ['-te']
    optional = ['-g', '-H', '-h', '-s', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/cloud/metadata-fetch/', query_data={'cloud_name': gvar['user_settings']['cloud-name'], 'metadata_name': gvar['user_settings']['metadata-name']})

    # Ensure the fetch directory structure exists.
    fetch_dir = '%s/.csv2/%s/files/%s/%s/metadata' % (
        gvar['home_dir'],
        gvar['pid_defaults']['server'],
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

    p = Popen(get_editor(gvar) + ['%s/%s' % (fetch_dir, response['metadata_name'])])
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

    mandatory = []
    required = []
    optional = ['-cn', '-CSEP', '-CSV', '-g', '-H', '-h', '-mn', '-NV', '-ok', '-r', '-s', '-V', '-VC', '-v', '-x509', '-xA']

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(gvar, mandatory, required, optional)

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
            'checksum/Checksum'
        ],
        title="Clouds/Metadata",
        )

def metadata_load(gvar):
    """
    Load a new cloud metadata file.
    """

    mandatory = ['-cn', '-f', '-mn']
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
        key_map=KEY_MAP
        )

    if not os.path.exists(gvar['user_settings']['file-path']):
        print('Error: The specified metadata file "%s" does not exist.' % gvar['user_settings']['file-path'])
        exit(1)

    # Set the default load command.
    url_command = '/cloud/metadata-add/'

    # If the "--force" option is used, change the url_command to overwrite the metadata if it already exists.
    if gvar['user_settings']['force']:
        # Replace the metadata file.
        response = requests(
            gvar,
            '/cloud/metadata-query/',
            query_data={
                'cloud_name': form_data['cloud_name'],
                'metadata_name': form_data['metadata_name'],
                }
            )
        
        if response['message']:
            print(response['message'])

        if response['metadata_exists']:
            url_command = '/cloud/metadata-update/'

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
    return base_metadata_save(gvar, context='cloud')

def metadata_update(gvar):
    """
    Modify a cloud in the active group.
    """

    mandatory = ['-cn', '-mn']
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

