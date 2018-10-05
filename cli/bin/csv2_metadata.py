from csv2_common import check_keys, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

import filecmp
import json
import os
import yaml

KEY_MAP = {
    '-g':   'group',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def get_repository_and_servers(gvar):
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
        gvar['user_settings']['backup-repository'] = os.path.abspath(gvar['user_settings']['backup-repository'])
        if not os.path.isdir(gvar['user_settings']['backup-repository']):
            print('Error: path specified for backup repository "%s" is not a directory or does not exist.' % gvar['user_settings']['backup-repository'])
            exit(1)

        if gvar['user_settings']['backup-repository'] != backup_repository:
            fd = open('%s/.csv2/backup_repository' % gvar['home_dir'], 'w')
            fd.write(gvar['user_settings']['backup-repository'])
            fd.close

    elif backup_repository:
        gvar['user_settings']['backup-repository'] = backup_repository

    servers = {}
    server_xref = {}
    for server_dir in os.listdir('%s/.csv2' % gvar['home_dir']):
        if not os.path.isdir('%s/.csv2/%s' % (gvar['home_dir'], server_dir)):
            continue

        _fd = open('%s/.csv2/%s/settings.yaml' % (gvar['home_dir'], server_dir))
        servers[server_dir] = yaml.load(_fd)
        _fd.close()

        server_xref[servers[server_dir]['server-address'][8:]] = server_dir

    return servers, server_xref

def make_dir(path):
    """
    Set the address and credentials for the specified cloudscheduler server.
    """

    try:
        os.mkdir(path)
    except FileExistsError:
        pass
#   except:
#       print('Error: can\'t create directory "%s".' % path)


def set_server(gvar, servers, server):
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

    return '%s/%s' % (gvar['user_settings']['backup-repository'], servers['settings'][server]['server-address'][8:])

def backup(gvar):
    """
    Backup all user data for all groups/clouds for each server configured in the user defaults.
    """

    mandatory = []
    required = ['-br']
    optional = ['-xA']
    servers = {}

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Retrieve the backup repository and all server information.
    servers['settings'], servers['xref'] = get_repository_and_servers(gvar)

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        mandatory,
        required,
        optional)

    # Retrieve data to backup For each cloudscheduler server.
    for server in servers['settings']:
        if server != 'prod':                     ########################## testing
            continue                             ########################## testing

        server_dir = set_server(gvar, servers, server)
        make_dir(server_dir)
        make_dir('%s/groups' % server_dir)

        response = requests(gvar, '/settings/prepare/')
        groups = gvar['user_groups']
        for group in groups:
            response = requests(gvar, '/settings/prepare/', {'group': group})
            group_dir = '%s/groups/%s' % (server_dir, group)
            make_dir(group_dir)
            make_dir('%s/clouds' % group_dir)
            make_dir('%s/metadata' % group_dir)



            print('Fetching: server=%s, group=%s' % (server, group))
            response = requests(gvar, '/group/defaults/')
            fd = open('%s/defaults' % group_dir, 'w')
            fd.write(json.dumps(response['defaults_list']))
            fd.close()

            response = requests(gvar, '/cloud/list/')
            for cloud in response['cloud_list']:
                cloud_dir = '%s/clouds/%s' % (group_dir, cloud['cloud_name'])
                make_dir(cloud_dir)

                fd = open('%s/settings' % cloud_dir, 'w')
                fd.write(json.dumps(cloud))
                fd.close()

            response = requests(gvar, '/group/metadata-list/')
            for metadata in response['group_metadata_list']:
                metadata_dir = '%s/clouds/%s' % (group_dir, metadata['metadata_name'])
                make_dir(metadata_dir)

                fd = open('%s/settings' % metadata_dir, 'w')
                fd.write(json.dumps(metadata))
                fd.close()

    print(servers)
    print(gvar['user_groups'])

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

