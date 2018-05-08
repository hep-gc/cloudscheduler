from csv2_common import check_keys, requests, show_table, verify_yaml_file
from subprocess import Popen, PIPE

import filecmp
import os

KEY_MAP = {
    '-gn':  'group_name',
    '-gm':  'condor_central_manager',
    '-jc':  'job_cpus',
    '-jd':  'job_disk',
    '-jed': 'job_scratch',
    '-jr':  'job_ram',
    '-js':  'job_swap',
    }

def _filter_by_group(gvar, qs):
    """
    Internal function to filter a query set by the specified group name.
    """

    if 'group-name' in gvar['command_args']:
        for _ix in range(len(qs)-1, -1, -1):
            if qs[_ix]['group_name'] != gvar['command_args']['group-name']:
                del(qs[_ix])

    return qs

def add(gvar):
    """
    Add a group to the active group.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-gm', '-gn'],
        [],
        [],
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

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        [],
        [],
        ['-g', '-jc', '-jd', '-jed', '-jr', '-js'],
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
    print('Active User: %s, Active Group: %s, User\'s Groups: %s' % (response['active_user'], response['active_group'], response['user_groups']))
    show_table(
        gvar,
        response['defaults_list'],
        [
            'group_name/Group',
            'job_cpus/Job Cores',
            'job_disk/Job Disk (GBs)',
            'job_scratch/Job Ephemeral Disk (GBs)',
            'job_ram/Job RAM (MBs)',
            'job_swap/Job Swap (GBs)',
            ],
        )

def delete(gvar):
    """
    Delete a group from the active group.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-gn'], [], [])

    # Check that the target group exists.
    response = requests(gvar, '/group/list/')
    _found = False
    for row in response['group_list']:
      if row['group_name'] == gvar['user_settings']['group-name']:
        _found = True
        break
   
    if not _found:
        print('Error: "csv2 group delete" cannot delete "%s", group doesn\'t exist.' % gvar['user_settings']['group-name'])
        exit(1)

    # Confirm group delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete group "%s"? (yes|..)' % gvar['user_settings']['group-name'])
        _reply = input()
        if _reply != 'yes':
          print('csv2 group delete "%s" cancelled.' % gvar['user_settings']['group-name'])
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

    # Check for missing arguments or help required.
    check_keys(gvar, [], [], ['-gn', '-ok'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/group/list/')
    
    if response['message']:
        print(response['message'])

    # Filter response as requested (or not).
    group_list = _filter_by_group(gvar, response['group_list'])

    # Print report
    print('Active User: %s, Active Group: %s, User\'s Groups: %s' % (response['active_user'], response['active_group'], response['user_groups']))
    if gvar['command_args']['only-keys']:
        show_table(
            gvar,
            group_list,
            [
                'group_name/Group',
            ],
            )
    else:
        show_table(
            gvar,
            group_list,
            [
                'group_name/Group',
                'condor_central_manager/Central Manager',
                'yaml_names/YAML Filenames',
                ],
            )

def update(gvar):
    """
    Modify the specified group.
    """

    # Check for missing arguments or help required.
    form_data = check_keys(
        gvar,
        ['-gn'],
        [],
        ['-gm'],
        key_map=KEY_MAP)

    if len(form_data) < 2:
        print('Error: "csv2 group update" requires at least one option to update.')
        exit(1)

    # Create the group.
    response = requests(
        gvar,
        '/group/update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

def yaml_delete(gvar):
    """
    Delete a group/YAML file.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-yn'], [], ['-g'])

    # Check that the target groupYAML file exists.
    response = requests(gvar, '/group/list/')
    _found = False
    for row in response['group_list']:
        if row['group_name'] == gvar['active_group']:
            yaml_names = row['yaml_names'].split(',')
            for yaml_name in yaml_names:
                if row['group_name'] == gvar['active_group']:
                    _found = True
                    break
   
    if not _found:
        print('Error: "csv2 group yaml-delete" cannot delete "%s-%s-%s", file doesn\'t exist.' % (response['active_group'], gvar['user_settings']['group-name'], gvar['user_settings']['yaml-name']))
        exit(1)

    # Confirm group/YAML file delete.
    if not gvar['user_settings']['yes']:
        print('Are you sure you want to delete the YAML file "%s-%s-%s"? (yes|..)' % (response['active_group'], gvar['user_settings']['group-name'], gvar['user_settings']['yaml-name']))
        _reply = input()
        if _reply != 'yes':
            print('csv2 group yaml-delete "%s-&s-%s" cancelled.' % (response['active_group'], gvar['user_settings']['group-name'], gvar['user_settings']['yaml-name']))
            exit(0)

    # Delete the group/YAML file.
    response = requests(
        gvar,
        '/group/yaml_delete/',
        form_data = {
            'yaml_name': gvar['user_settings']['yaml-name'],
            }
        )
    
    if response['message']:
        print(response['message'])

def yaml_edit(gvar):
    """
    Edit the specified group/YAML file.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-yn'], ['-te'], ['-g'])

    # Retrieve data (possibly after changing the group).
    response = requests(gvar, '/group/yaml_fetch/%s.%s' % (gvar['active_group'], gvar['user_settings']['yaml-name']))

    # Ensure the fetch directory structure exists.
    fetch_dir = '%s/.csv2/%s/files/%s/yaml' % (
        gvar['home_dir'],
        gvar['server'],
        response['group_name'],
        )

    if not os.path.exists(fetch_dir):
        os.makedirs(fetch_dir, mode=0o700)  

    # Write the reference copy.
    fd = open('%s/.%s.yaml' % (fetch_dir, response['yaml_name']), 'w')
    fd.write('# yaml_enabled: %s, yaml_mime_type: %s\n%s' % (response['yaml_enabled'], response['yaml_mime_type'], response['yaml']))
    fd.close()

    # Write the edit copy.
    fd = open('%s/%s.yaml' % (fetch_dir, response['yaml_name']), 'w')
    fd.write('# yaml_enabled: %s, yaml_mime_type: %s\n%s' % (response['yaml_enabled'], response['yaml_mime_type'], response['yaml']))
    fd.close()

    p = Popen([gvar['user_settings']['text-editor'], '%s/%s.yaml' % (fetch_dir, response['yaml_name'])])
    p.communicate()

    if filecmp.cmp(
        '%s/.%s.yaml' % (fetch_dir, response['yaml_name']),
        '%s/%s.yaml' % (fetch_dir, response['yaml_name'])
        ):
        print('csv2 group yaml-edit "%s-%s" completed, no changes.' % (response['group_name'],  response['yaml_name']))
        exit(0)

    # Verify the changed YAML file.
    form_data = {
        **verify_yaml_file('%s/%s.yaml' % (fetch_dir, response['yaml_name'])),
        'yaml_name': response['yaml_name'],
        }

    # Replace the YAML file.
    response = requests(
        gvar,
        '/group/yaml_update/',
        form_data
        )
    
    if response['message']:
        print(response['message'])


def yaml_load(gvar):
    """
    Load a new group/YAML file.
    """

    # Check for missing arguments or help required.
    check_keys(gvar, ['-f', '-yn'], [], ['-g'])

    if not os.path.exists(gvar['user_settings']['file-path']):
        print('Error: The specified YAML file "%s" does not exist.' % gvar['user_settings']['file-path'])
        exit(1)

    # Verify the changed YAML file and build input form data.
    form_data = {
        **verify_yaml_file(gvar['user_settings']['file-path']),
        'yaml_name': gvar['user_settings']['yaml-name'],
        }

    # Replace the YAML file.
    response = requests(
        gvar,
        '/group/yaml_add/',
        form_data
        )
    
    if response['message']:
        print(response['message'])

