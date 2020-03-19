from cloudscheduler.unit_tests.unit_test_common import generate_secret, load_settings
import os
import re
import subprocess
import sys
import yaml

SETUP_REQUIRED_FILE = 'setup_required.bool'

def setup():
    cleanup()
    gvar = load_settings()
    gvar['address'] = gvar['user_settings']['server-addres']
    gvar['user'] = gvar['user_settings']['server-user']
    del gvar['user_settings']

    # To avoid repeating all of this a few times. Only missing mandatory parameter is `--cloud-name`.
    cloud_template = ['cloud', 'add',
        '-ca', gvar['cloud_credentials']['authurl'],
        '-cU', gvar['cloud_credentials']['username'],
        '-cpw', gvar['cloud_credentials']['password'],
        '-cP', gvar['cloud_credentials']['project'],
        '-cr', gvar['cloud_credentials']['region'],
        '-ct', 'openstack'
    ]

    setup_commands = [
        # The active group most of the time.
        ['group', 'add', '-gn', '{}-wig1'.format(gvar['user']), '-htcf', gvar[3]],
        # Group with no users.
        ['group', 'add', '-gn', '{}-wig2'.format(gvar['user']), '-htcf', gvar[3]],
        # Group to be deleted.
        ['group', 'add', '-gn', '{}-wig3'.format(gvar['user']), '-htcf', gvar[3]],
        # Group to be updated.
        ['group', 'add', '-gn', '{}-wig4'.format(gvar['user']), '-htcf', gvar[3],
            '--htcondor-container-hostname', 'unit-test.ca',
            '--htcondor-other-submitters', '{}-wiu1'.format(gvar['user'])],
            '--job-cores', '3',
            '--job-disk', '1',
            '--job-ram', '4',
            '--job-swap', '1'],
        # User used to perform most actions not requiring privileges.
        ['user', 'add', '-un', '{}-wiu1'.format(gvar['user']), '-upw', gvar[1],
            '--group-name', '{}-wig1'.format(gvar['user'])],
        # User used to perform most actions requiring privileges.
        ['user', 'add', '-un', '{}-wiu2'.format(gvar['user']), '-upw', gvar[1],
            '--group-name', '{}-wig1'.format(gvar['user']),
            '--super-user', 'True'],
        # User who is not in any groups.
        ['user', 'add', '-un', '{}-wiu3'.format(gvar['user']), '-upw', gvar[1]],
        # User to be deleted.
        ['user', 'add', '-un', '{}-wiu4'.format(gvar['user']), '-upw', gvar[1],
            '--group-name', '{}-wig1'.format(gvar['user'])],
        # User to be updated.
        ['user', 'add', '-un', '{}-wiu5'.format(gvar['user']), '-upw', gvar[1],
            '--group-name', '{}-wig1'.format(gvar['user']),
            '--user-common-name', '{} user 5'.format(gvar['user'])],
        # Cloud that should always exist to create aliases for.
        cloud_template + ['-cn', '{}-wic1'.format(gvar['user'])],
        # Cloud to be deleted.
        cloud_template + ['-cn', '{}-wic2'.format(gvar['user'])],
        # Cloud to be updated.
        cloud_template + ['-cn', '{}-wic3'.format(gvar['user'])],
        # Alias that should always exist.
        ['alias', 'add', '-an', '{}-wia1'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user'])],
        # Alias to be updated and deleted.
        ['alias', 'add', '-an', '{}-wia2'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user'])],
        # Cloud metadata that should always exist.
        # Cloud metadata to be deleted.
        # Cloud metadata to be updated.
        # Group metadata that should always exist.
        # Group metadata to be deleted.
        # Group metadata to be updated.
    ]

    if setup_required(set_to=False):
        print('Creating test objects. Run web_common.cleanup() later to remove them.')
        for command in setup_commands:
            process = subprocess.run(['cloudscheduler'] + command, check=True)

    return gvar

def cleanup():
    cleanup_commands = [
        ['group', 'delete', '{}-wig1'.format(gvar)],
    ]

    for command in cleanup_commands:
        process = subprocess.run(['cloudscheduler'] + command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    setup_required(set_to=True)

def setup_required(set_to=None):
    try:
        with open(SETUP_REQUIRED_FILE) as setup_required_file:
            setup_required = (setup_required_file.read().strip('\n') != '0')
    except FileNotFoundError:
        set_to = True
        # Create the setup_required file.
        print('Creating file at {} to remember if test objects are setup.'.format(SETUP_REQUIRED_FILE))
        os.umask(0)
        os.makedirs(os.path.dirname(SETUP_REQUIRED_FILE), mode=0o700, exist_ok=True)
    except ValueError:
        set_to = True
        print('Error: Failed to parse {}'.format(SETUP_REQUIRED_FILE), file=sys.stderr)

    if set_to != None:
        with open(SETUP_REQUIRED_FILE, 'w') as setup_required_file:
            setup_required_file.write(str(int(set_to)))

    return setup_required
