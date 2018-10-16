from csv2_common import check_keys, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

from getpass import getuser
from tempfile import mkdtemp

import filecmp
import json
import os
import yaml

from csv2_group import defaults, metadata_delete, metadata_edit, metadata_list, metadata_load, metadata_update

KEY_MAP = {
    '-g':   'group',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def _create_backup_file(gvar, path, metadata):
    """
    Open the backup file (for writing), making the directory if necessary, and return the file descriptor.
    """

    path_dir = os.path.dirname(path)
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
        servers[host_dir] = yaml.load(_fd)
        _fd.close()

        server_xref[servers[host_dir]['server-address'][8:]] = host_dir

    return servers, server_xref

def _set_host(gvar, servers, server):
    """
    Set the address and credentials for the specified cloudscheduler server.
    """

    try:
        gvar['user_settings']['server-address'] = servers['settings'][server]['server-address']
        del gvar['user_settings']['server-grid-cert']
        del gvar['user_settings']['server-grid-key']
        del gvar['user_settings']['server-user']
        del gvar['user_settings']['server-password']
    except:
        pass

    if 'server-grid-cert' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-cert']) and \
        'server-grid-key' in gvar['user_settings'] and \
        os.path.exists(gvar['user_settings']['server-grid-key']):

        gvar['user_settings']['server-grid-cert'] = servers['settings'][server]['server-grid-cert']
        gvar['user_settings']['server-grid-key'] = servers['settings'][server]['server-grid-key']

    elif 'server-user' in gvar['user_settings']:
        gvar['user_settings']['server-user'] = servers['settings'][server]['server-user']
        if 'server-password' not in gvar['user_settings'] or gvar['user_settings']['server-password'] == '?':
            gvar['user_settings']['server-password'] = getpass('Enter your %s password for server "%s": ' % (gvar['command_name'], gvar['server']))
        else:
            gvar['user_settings']['server-password'] = servers['settings'][server]['server-password']

    return servers['settings'][server]['server-address'][8:], '%s/%s' % (gvar['user_settings']['backup-repository'], servers['settings'][server]['server-address'][8:])

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
                    '%s-backup commit by %s' % (msg, getuser())
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
    optional = ['-bk', '-xA']
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
    _update_git(gvar, 'pre')

    # If the backup directory is an encrypted git repository, create a working temorary directory.
    if 'backup-key' in gvar['user_settings'] and os.path.exists('%s/.git' % gvar['user_settings']['backup-repository']):
        gvar['temp_dir'] = mkdtemp()
    else:
        gvar['temp_dir'] = None

    # Retrieve data to backup for each cloudscheduler server.
    fetched = {}
    for server in sorted(servers['settings']):
        host, host_dir = _set_host(gvar, servers, server)
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

            response = requests(gvar, '/settings/prepare/', {'group': group})
            group_dir = '%s/groups/%s' % (host_dir, group)

            print('Fetching: server=%s, group=%s' % (server, group))
            response = requests(gvar, '/group/defaults/')
            _create_backup_file(gvar, '%s/defaults' % group_dir, response['defaults_list'])

            response = requests(gvar, '/group/metadata-list/')
            for metadata in response['group_metadata_list']:
                metadata_dir = '%s/metadata' % group_dir
                _create_backup_file(gvar, '%s/%s' % (metadata_dir, metadata['metadata_name']), metadata)

            response = requests(gvar, '/cloud/list/')
            for cloud in response['cloud_list']:
                cloud_dir = '%s/clouds/%s' % (group_dir, cloud['cloud_name'])
                _create_backup_file(gvar, '%s/settings' % cloud_dir, cloud)

            response = requests(gvar, '/cloud/metadata-list/')
            for metadata in response['cloud_metadata_list']:
                metadata_dir = '%s/metadata' % cloud_dir
                _create_backup_file(gvar, '%s/%s' % (metadata_dir, metadata['metadata_name']), metadata)

        # Restore the server's initial group.
        response = requests(gvar, '/settings/prepare/', {'group': servers['initial_server_group']})

    _update_git(gvar, 'post')

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
    Restore selected user data.
    """

    mandatory = []
    required = ['-br']
    optional = []

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        mandatory,
        required,
        optional)

def update(gvar):
    return metadata_update(gvar)

