from csv2_common import check_keys, qc, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

from getpass import getuser
from shutil import rmtree
from tempfile import mkdtemp

import filecmp
import json
import os
import yaml

from csv2_common import yaml_full_load
from csv2_group import defaults, metadata_delete, metadata_edit, metadata_list, metadata_load, metadata_update

KEY_MAP = {
    '-g':   'group',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def _conditionally_restore_a_file(gvar, path, metadata):
    """
    Compare the metadata on the server with its' backup and if they differ, ask the user
    whether they want to restore the backup.
    """

    if metadata and path in gvar['backup_path_list']:
        del gvar['backup_path_list'][path]

    path_dir = os.path.dirname(path)
    if path[:-1] == path_dir:
        print('Skipping metadata file with no name, path="%s"' % path)
        return

    work_path = '%s/work%s' % (gvar['temp_dir'], path)
    work_dir = os.path.dirname(work_path)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    
    fd = open(work_path, 'w')
    if metadata:
        fd.write(json.dumps(metadata))
    fd.close()

    if 'backup-key' in gvar['user_settings']:
        compare_path = '%s/compare%s' % (gvar['temp_dir'], path)
        compare_dir = os.path.dirname(compare_path)
        if not os.path.exists(compare_dir):
            os.makedirs(compare_dir)

        restore_path = compare_path

        p = Popen(
            [
                'ansible-vault',
                'decrypt',
                path,
                '--output',
                restore_path,
                '--vault-password-file',
                gvar['user_settings']['backup-key']
                ],
            stdout=PIPE, stderr=PIPE
            )
        stdout, stderr = p.communicate()

        if p.returncode != 0:
            raise Exception('Error: ansible-vault decrypt: stdout=%s, stderr=%s' % (stdout, stderr))

    else:
        restore_path = path

    if not metadata or not filecmp.cmp(work_path, restore_path, shallow=False):
        while(True):
            if metadata:
                rsp = input('Backup up differs from server metadata, path=%s. Do you want to restore the backup? (yes, no (default), show, or quit):' % path)
            else:
                rsp = input('File missing from server, backup file path=%s. Do you want to restore the backup? (yes, no (default), show, or quit):' % path)

            if rsp == '' or 'no'[:len(rsp)] == rsp.lower():
                break
            elif 'yes'[:len(rsp)] == rsp.lower():
                words = restore_path.split('/')
                ix = words.index('groups')

                response = requests(gvar, '/settings/prepare/', {'group': words[ix+1]})

                fd = open(restore_path)
                restore_data = qc(json.loads(fd.read()), columns=['group_name'], option='prune')
                fd.close()

                if len(words) == ix+3:
                    response = requests(gvar, '/group/defaults/', _get_restore_data(gvar, restore_path, other_prune_columns=['job_scratch']))
                elif len(words) == ix+4:
                    response = requests(gvar, '/group/metadata-update/', _get_restore_data(gvar, restore_path))
                elif len(words) == ix+5:
                    response = requests(gvar, '/cloud/update/', _get_restore_data(gvar, restore_path))
                elif len(words) == ix+6:
                    response = requests(gvar, '/cloud/metadata-update/', _get_restore_data(gvar, restore_path))

                if response['response_code'] == 0:
                    print('Successfully restored.')
                else:
                    raise Exception('Metadata restoration failed, msg=%s' % response['message'])

                break


            elif 'quit'[:len(rsp)] == rsp.lower():
                exit(0)
            elif 'show'[:len(rsp)] == rsp.lower():
                expanded_work_path = _expand(gvar, work_path)
                expanded_restore_path = _expand(gvar, restore_path)
                print('< server (%s), > backup' % gvar['pid_defaults']['server'])
                p = Popen(
                    [
                        'diff',
                        '-y',
                        expanded_work_path,
                        expanded_restore_path
                        ]
                    )
                p.communicate()

            else:
                print('Invalid response "%s".' % rsp)

def _create_backup_file(gvar, path, metadata):
    """
    Open the backup file (for writing), making the directory if necessary, and return the file descriptor.
    """

    path_dir = os.path.dirname(path)
    if path[:-1] == path_dir:
        print('Skipping metadata file with no name, path="%s"' % path)
        return

    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    if gvar['temp_dir'] and os.path.exists(path):
        compare_path = '%s/compare%s' % (gvar['temp_dir'], path)
        compare_dir = os.path.dirname(compare_path)
        if not os.path.exists(compare_dir):
            os.makedirs(compare_dir)

        work_path = '%s/work%s' % (gvar['temp_dir'], path)
        work_dir = os.path.dirname(work_path)
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        
        p = Popen(
            [
                'ansible-vault',
                'decrypt',
                path,
                '--output',
                compare_path,
                '--vault-password-file',
                gvar['user_settings']['backup-key']
                ],
            stdout=PIPE, stderr=PIPE
            )
        stdout, stderr = p.communicate()

        if p.returncode != 0:
            raise Exception('Error: ansible-vault decrypt: stdout=%s, stderr=%s' % (stdout, stderr))

        fd = open(work_path, 'w')
        fd.write(json.dumps(metadata))
        fd.close()

        if not filecmp.cmp(work_path, compare_path, shallow=False):
            print('Updating backup for %s' % path)
            p = Popen(
                [
                    'ansible-vault',
                    'encrypt',
                    work_path,
                    '--output',
                    path,
                    '--vault-password-file',
                    gvar['user_settings']['backup-key']
                    ],
                stdout=PIPE, stderr=PIPE
                )
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                raise Exception('Error: ansible-vault encrypt: stdout=%s, stderr=%s' % (stdout, stderr))

    else:
        fd = open(path, 'w')
        fd.write(json.dumps(metadata))
        fd.close()

        if 'backup-key' in gvar['user_settings']:
            p = Popen(
                [
                    'ansible-vault',
                    'encrypt',
                    path,
                    '--vault-password-file',
                    gvar['user_settings']['backup-key']
                    ],
                stdout=PIPE, stderr=PIPE
                )
            stdout, stderr = p.communicate()

def _expand(gvar, meta_path):
    """
    Expand the json file to make a readable diff.
    """

    expanded_meta_path = '%s-expanded' % meta_path

    fd = open(meta_path)
    metadata = json.loads(fd.read())
    fd.close()

    fd = open(expanded_meta_path, 'w')
    if metadata :
        for column in metadata:
            if column == 'metadata':
                fd.write('%-16s:\n' % column)
                lines = metadata[column].replace('\r\n', '\n').split('\n')
                count = 0
                for line in lines:
                    count += 1
                    fd.write('    %04d %s:\n' % (count, line))
            else:
                fd.write('%-16s: %s\n' % (column, metadata[column]))
    fd.close()

    return expanded_meta_path

def _get_backup_path_list(gvar, dir_path):
    """
    Scan the backup repository saving a list of all file paths.
    """

    for item in os.listdir(dir_path):
        current_path = '%s/%s' % (dir_path, item)
        if os.path.isdir(current_path) and item[0] != '.':
            _get_backup_path_list(gvar, current_path)
        elif os.path.isfile(current_path) and item [0] != '.':
            gvar['backup_path_list'][current_path] = True


def _get_cloud_settings(query_list):
    """
    Remove superfluous columns from the cloud query_list.
    """

    return qc(query_list, [
        'group_name',
        'cloud_name',
        'enabled',
        'spot_price',
        'vm_flavor',
        'vm_image',
        'vm_keep_alive',
        'vm_keyname',
        'vm_network',
        'authurl',
        'project_domain_name',
        'project',
        'user_domain_name',
        'username',
        'cacertificate',
        'region',
        'cloud_type',
        'cores_ctl'
        ], option='keep'
    )

def _get_repository_and_servers(gvar):
    """
    Backup all user data for all groups/clouds for each server configured in the user defaults.
    """

    # Retrieve default backup repository.
    if os.path.isfile('%s/.csv2/backup_repository' % gvar['home_dir']):
        fd = open('%s/.csv2/backup_repository' % gvar['home_dir'])
        backup_repository = fd.read()
        fd.close
    else:
        backup_repository = None

    if 'backup-repository' in gvar['user_settings']:
        if gvar['user_settings']['backup-repository'] == '':
            print('Error: path specified for backup repository cannot be null.')
            exit(1)

        else:
            gvar['user_settings']['backup-repository'] = os.path.abspath(gvar['user_settings']['backup-repository'])
            if not os.path.isdir(gvar['user_settings']['backup-repository']):
                print('Error: path specified for backup repository "%s" is not a directory or does not exist.' % gvar['user_settings']['backup-repository'])
                exit(1)

            if gvar['user_settings']['backup-repository'] != backup_repository:
                fd = open('%s/.csv2/backup_repository' % gvar['home_dir'], 'w')
                fd.write(gvar['user_settings']['backup-repository'])
                fd.close

                os.chmod('%s/.csv2/backup_repository' % gvar['home_dir'], 0o600)

    elif backup_repository:
        gvar['user_settings']['backup-repository'] = backup_repository

    # Retrieve default backup key - no key, no encryption.
    if os.path.isfile('%s/.csv2/backup_key' % gvar['home_dir']):
        fd = open('%s/.csv2/backup_key' % gvar['home_dir'])
        backup_key = fd.read()
        fd.close
    else:
        backup_key = None

    if 'backup-key' in gvar['user_settings']:
        if gvar['user_settings']['backup-key'] == '':
            os.remove('%s/.csv2/backup_key' % gvar['home_dir'])
            del gvar['user_settings']['backup-key']

        else:
            gvar['user_settings']['backup-key'] = os.path.abspath(gvar['user_settings']['backup-key'])
            if not os.path.isfile(gvar['user_settings']['backup-key']):
                print('Error: path specified for backup key "%s" is not a file or does not exist.' % gvar['user_settings']['backup-key'])
                exit(1)

            if gvar['user_settings']['backup-key'] != backup_key:
                fd = open('%s/.csv2/backup_key' % gvar['home_dir'], 'w')
                fd.write(gvar['user_settings']['backup-key'])
                fd.close

                os.chmod('%s/.csv2/backup_key' % gvar['home_dir'], 0o600)

    elif backup_key:
        gvar['user_settings']['backup-key'] = backup_key

    servers = {}
    server_xref = {}
    for host_dir in os.listdir('%s/.csv2' % gvar['home_dir']):
        if not os.path.isdir('%s/.csv2/%s' % (gvar['home_dir'], host_dir)) or host_dir[0] == '.':
            continue

        _fd = open('%s/.csv2/%s/settings.yaml' % (gvar['home_dir'], host_dir))
        servers[host_dir] = yaml_full_load(_fd)
        _fd.close()

        if 'server-address' in servers[host_dir]:
            server_xref[servers[host_dir]['server-address'][8:]] = host_dir

    return servers, server_xref

def _get_restore_data(gvar, restore_path, other_prune_columns=[]):
    """
    Return the backup data to be resored minus the group_name.
    """

    fd = open(restore_path)
    restore_data = qc(json.loads(fd.read()), columns=['group_name'] + other_prune_columns, option='prune')
    fd.close()

    return restore_data


def _set_host(gvar, servers, server):
    """
    Set the address and credentials for the specified cloudscheduler server.
    """

    try:
        gvar['user_settings']['server-address'] = servers['settings'][server]['server-address']
        del gvar['user_settings']['server-user']
        del gvar['user_settings']['server-password']
    except:
        pass

    if 'server-user' in gvar['user_settings']:
        gvar['user_settings']['server-user'] = servers['settings'][server]['server-user']
        if 'server-password' not in gvar['user_settings'] or gvar['user_settings']['server-password'] == '?':
            gvar['user_settings']['server-password'] = getpass('Enter your %s password for server "%s": ' % (gvar['command_name'], gvar['pid_defaults']['server']))
        else:
            gvar['user_settings']['server-password'] = servers['settings'][server]['server-password']

    if 'server-address' in servers['settings'][server]:
        gvar['pid_defaults']['server'] = server
        return servers['settings'][server]['server-address'][8:], '%s/%s' % (gvar['user_settings']['backup-repository'], servers['settings'][server]['server-address'][8:])
    else:
        gvar['pid_defaults']['server'] = None
        return None, None

def _update_git(gvar, msg):
    """
    Add untracked items and commit all updates.
    """

    # If the backup directory is a git repository, update git.
    if os.path.exists('%s/.git' % gvar['user_settings']['backup-repository']):
        p = Popen(
            [
                'git',
                'status',
                '-s'
                ],
            cwd=gvar['user_settings']['backup-repository'], stdout=PIPE, stderr=PIPE
            )
        stdout, stderr = p.communicate()

        if p.returncode != 0:
            raise Exception('Error: git status: stdout=%s, stderr=%s' % (stdout, stderr))

        # Process untracked files.
        count = 0
        lines = stdout.decode("utf-8").split('\n')
        for line in lines:
            if line[:3] == ' A ' or line[:3] == ' M ':
                count += 1
            if line[:3] == '?? ':
                count += 1
                p = Popen(
                    [
                        'git',
                        'add',
                        line[3:]
                        ],
                    cwd=gvar['user_settings']['backup-repository'], stdout=PIPE, stderr=PIPE
                    )
                stdout, stderr = p.communicate()

                if p.returncode != 0:
                    raise Exception('Error: git add: stdout=%s, stderr=%s' % (stdout, stderr))

        if count > 0:
            p = Popen(
                [
                    'git',
                    'commit',
                    '-am',
                    '%s commit by %s' % (msg, getuser())
                    ],
                cwd=gvar['user_settings']['backup-repository'], stdout=PIPE, stderr=PIPE
                )
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                raise Exception('Error: git commit: stdout=%s, stderr=%s' % (stdout, stderr))

def backup(gvar):
    """
    Backup all user data for all groups/clouds for each server configured in the user defaults.
    """

    mandatory = []
    required = ['-br']
    optional = ['-bk', '-v', '-x509', '-xA']
    servers = {}

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Retrieve the backup repository and all server information.
    servers['settings'], servers['xref'] = _get_repository_and_servers(gvar)

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        mandatory,
        required,
        optional)

    # If the backup directory is an encrypted git repository, create a working temorary directory.
    _update_git(gvar, 'pre-backup')

    # If the backup directory is an encrypted git repository, create a working temorary directory.
    if 'backup-key' in gvar['user_settings'] and os.path.exists('%s/.git' % gvar['user_settings']['backup-repository']):
        gvar['temp_dir'] = mkdtemp()
    else:
        gvar['temp_dir'] = None

    # Retrieve data to backup for each cloudscheduler server.
    fetched = {}
    for server in sorted(servers['settings']):
        host, host_dir = _set_host(gvar, servers, server)
        if not host:
            print('Skipping server="%s", no server address.' % server)
            continue

        if host not in fetched:
            fetched[host] = {}

        # Save the initital server group so it can be restored later.
        response = requests(gvar, '/settings/prepare/')
        servers['initial_server_group'] = gvar['active_group']

        groups = gvar['user_groups']
        for group in sorted(groups):
            if group in fetched[host]:
                continue

            fetched[host][group] = True

            # Switch groups.
            response = requests(gvar, '/settings/prepare/', {'group': group})

            print('Fetching: server=%s, group=%s' % (server, group))
            response = requests(gvar, '/group/defaults/')
            _create_backup_file(gvar, '%s/groups/%s/defaults' % (host_dir, response['defaults_list'][0]['group_name']), response['defaults_list'][0])

            response = requests(gvar, '/group/metadata-list/')
            for metadata in response['group_metadata_list']:
                _create_backup_file(gvar, '%s/groups/%s/metadata/%s' % (host_dir, metadata['group_name'], metadata['metadata_name']), metadata)

            response = requests(gvar, '/cloud/list/')
            for cloud in response['cloud_list']:
                _create_backup_file(gvar, '%s/groups/%s/clouds/%s/settings' % (host_dir, cloud['group_name'], cloud['cloud_name']), _get_cloud_settings(cloud))

            response = requests(gvar, '/cloud/metadata-list/')
            for metadata in response['cloud_metadata_list']:
                _create_backup_file(gvar, '%s/groups/%s/clouds/%s/metadata/%s' % (host_dir, metadata['group_name'], metadata['cloud_name'], metadata['metadata_name']), metadata)

        # Restore the server's initial group.
        response = requests(gvar, '/settings/prepare?%s' % servers['initial_server_group'])

    _update_git(gvar, 'post-backup')

    if gvar['temp_dir']:
        rmtree(gvar['temp_dir'])

def delete(gvar):
    return metadata_delete(gvar)

def edit(gvar):
    return metadata_edit(gvar)

def group(gvar):
    return defaults(gvar)

def list(gvar):
    return metadata_list(gvar)

def load(gvar):
    return metadata_load(gvar)

def restore(gvar):
    """
    Restore user data.
    """

    mandatory = []
    required = ['-br']
    optional = ['-bk', '-v', '-x509', '-xA']
    servers = {}

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Retrieve the backup repository and all server information.
    servers['settings'], servers['xref'] = _get_repository_and_servers(gvar)

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        mandatory,
        required,
        optional)

    # Commit any outstanding repository updates prior to the restore.
    _update_git(gvar, 'pre-restore')

    # Retrieve an inventory of the current backup files.
    gvar['backup_path_list'] = {}
    _get_backup_path_list(gvar, gvar['user_settings']['backup-repository'])

    # We need a temporary working directory.
    gvar['temp_dir'] = mkdtemp()

    # Retrieve data from each cloudscheduler server to compare with its' backup. If the
    # backup is different, conditionally (allow the user to choose) restore it.
    fetched = {}
    host_group_xref = {}
    for server in sorted(servers['settings']):
        host, host_dir = _set_host(gvar, servers, server)
        if not host:
            print('Skipping server="%s", no server address.' % server)
            continue

        if host not in fetched:
            fetched[host] = {}

        # Save the initital server group so it can be restored later.
        response = requests(gvar, '/settings/prepare/')
        servers['initial_server_group'] = gvar['active_group']

        groups = gvar['user_groups']
        for group in sorted(groups):
            if group in fetched[host]:
                continue

            fetched[host][group] = True
            host_group_xref['%s::%s' % (host, group)] = server

            # Switch groups.
            response = requests(gvar, '/settings/prepare/', {'group': group})

            print('Checking: server=%s, group=%s' % (server, group))
            response = requests(gvar, '/group/defaults/')
            _conditionally_restore_a_file(gvar, '%s/groups/%s/defaults' % (host_dir, response['defaults_list'][0]['group_name']), response['defaults_list'][0])

            response = requests(gvar, '/group/metadata-list/')
            for metadata in response['group_metadata_list']:
                _conditionally_restore_a_file(gvar, '%s/groups/%s/metadata/%s' % (host_dir, metadata['group_name'], metadata['metadata_name']), metadata)

            response = requests(gvar, '/cloud/list/')
            for cloud in response['cloud_list']:
                _conditionally_restore_a_file(gvar, '%s/groups/%s/clouds/%s/settings' % (host_dir, cloud['group_name'], cloud['cloud_name']), _get_cloud_settings(cloud))

            response = requests(gvar, '/cloud/metadata-list/')
            for metadata in response['cloud_metadata_list']:
                _conditionally_restore_a_file(gvar, '%s/groups/%s/clouds/%s/metadata/%s' % (host_dir, metadata['group_name'], metadata['cloud_name'], metadata['metadata_name']), metadata)

        # Restore the server's initial group.
        response = requests(gvar, '/settings/prepare?%s' % servers['initial_server_group'])

    # Scan remaining backup files building an inventory to restore.
    remaining_inventory = {}
    for path in sorted(gvar['backup_path_list']):
        words = path.split('/')
        ix = words.index('groups')
        host = words[ix-1]
        group = words[ix+1]
        xref_key = '%s::%s' % (host, group)
        if xref_key in gvar['host_group_xref']:
            server = host_group_xref[xref_key]

            if server not in remaining_inventory:
                remaining_inventory[server] = {}

            if group not in remaining_inventory[server]:
                remaining_inventory[server][group] = []

            remaining_inventory[server][group].append(path)

        else:
            print('Skipping backup file "%s", you have no access to the server.')
            continue

    # Perform remaining conditional restores.
    for server in sorted(remaining_inventory):
        host, host_dir = _set_host(gvar, servers, server)

        # Save the initital server group so it can be restored later.
        response = requests(gvar, '/settings/prepare/')
        servers['initial_server_group'] = gvar['active_group']

        for group in sorted(remaining_inventory[server]):
            print('Processing missing files: server=%s, group=%s' % (server, group))

            # Switch groups.
            response = requests(gvar, '/settings/prepare/', {'group': group})

            for path in remaining_inventory[server][group]:
                _conditionally_restore_a_file(gvar, path, None)

        # Restore the server's initial group.
        response = requests(gvar, '/settings/prepare?%s' % servers['initial_server_group'])

    _update_git(gvar, 'post-restore')

    rmtree(gvar['temp_dir'])

def update(gvar):
    return metadata_update(gvar)

