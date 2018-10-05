from csv2_common import check_keys, requests, show_active_user_groups, show_table
from subprocess import Popen, PIPE

import filecmp
import os
import yaml

KEY_MAP = {
    '-g':   'group',
    }

COMMAS_TO_NL = str.maketrans(',','\n')

def backup(gvar):
    """
    Backup all user data for all groups/clouds for each server configured in the user defaults.
    """

    mandatory = ['-br']
    required = []
    optional = []

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        mandatory,
        required,
        optional)

    servers = {}
    server_xref = {}
    for server_dir in os.listdir('%s/.csv2' % gvar['home_dir']):
        if not os.path.isdir('%s/.csv2/%s' % (gvar['home_dir'], server_dir)):
            continue

        _fd = open('%s/.csv2/%s/settings.yaml' % (gvar['home_dir'], server_dir))
        servers[server_dir] = yaml.load(_fd)
        _fd.close()

        server_xref[servers[server_dir]['server-address'][8:]] = server_dir

    print(server_xref)
    print(servers)

def restore(gvar):
    """
    Restore selected user data.
    """

    mandatory = ['-br']
    required = []
    optional = []

    if gvar['retrieve_options']:
        return mandatory + required + optional

    # Check for missing arguments or help required.
    check_keys(
        gvar,
        mandatory,
        required,
        optional)

