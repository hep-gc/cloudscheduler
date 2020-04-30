import subprocess
from sys import argv
from cloudscheduler.unit_tests.unit_test_common import load_settings

def main():
    gvar = load_settings(web=True)
    if len(argv) > 1:
        if argv[1] == '--setup' or parameter == '-s':
            setup(gvar)
        elif argv[1] == '--cleanup' or parameter == '-c':
            cleanup(gvar)
        else:
            raise SystemExit('Unrecognized flag \'{}\'.'.format(argv[1]))
    else:
        cleanup(gvar)
        setup(gvar)

def setup(gvar):
    '''Create test objects.'''

    server_credentials = ['-su', '{}-wiu1'.format(gvar['user']), '-spw', gvar['user_secret']]
    # To avoid repeating all of this a few times. Only missing mandatory parameter is --cloud-name.
    cloud_template = ['cloud', 'add',
        *server_credentials,
        '-ca', gvar['cloud_credentials']['authurl'],
        '-cU', gvar['cloud_credentials']['username'],
        '-cpw', gvar['cloud_credentials']['password'],
        '-cP', gvar['cloud_credentials']['project'],
        '-cr', gvar['cloud_credentials']['region'],
        '-ct', 'openstack'
    ]

    setup_commands = [
        # The active group most of the time.
        ['group', 'add', '-gn', gvar['user'] + '-wig1', '-htcf', gvar['fqdn']],
        # Group with no users.
        ['group', 'add', '-gn', gvar['user'] + '-wig2', '-htcf', gvar['fqdn']],
        # Group to be deleted.
        ['group', 'add', '-gn', gvar['user'] + '-wig3', '-htcf', gvar['fqdn']],
        # Group to be updated.
        ['group', 'add', '-gn', gvar['user'] + '-wig4', '-htcf', gvar['fqdn'],
            '--htcondor-container-hostname', 'unit-test.ca',
            '--htcondor-users', gvar['user'] + '-wiu1',
            '--job-cores', '3',
            '--job-disk', '1',
            '--job-ram', '4',
            '--job-swap', '1'],
        # User used to perform most actions not requiring privileges.
        ['user', 'add', '-un', gvar['user'] + '-wiu1', '-upw', gvar['user_secret'],
            '--group-name', gvar['user'] + '-wig1'],
        # User used to perform most actions requiring privileges.
        ['user', 'add', '-un', gvar['user'] + '-wiu2', '-upw', gvar['user_secret'],
            '--group-name', gvar['user'] + '-wig1',
            '--super-user', 'True'],
        # User who is not in any groups.
        ['user', 'add', '-un', gvar['user'] + '-wiu3', '-upw', gvar['user_secret']],
        # User to be deleted.
        ['user', 'add', '-un', gvar['user'] + '-wiu4', '-upw', gvar['user_secret'],
            '--group-name', gvar['user'] + '-wig1'],
        # User to be updated.
        ['user', 'add', '-un', gvar['user'] + '-wiu5', '-upw', gvar['user_secret'],
            '--group-name', gvar['user'] + '-wig1',
            '--user-common-name', gvar['user'] + ' user 5'],
        # Cloud that should always exist to create aliases for.
        cloud_template + ['-cn', gvar['user'] + '-wic1'],
        # Cloud to be deleted.
        cloud_template + ['-cn', gvar['user'] + '-wic2'],
        # Cloud to be updated.
        cloud_template + ['-cn', gvar['user'] + '-wic3'],
        # Alias that should always exist.
        ['alias', 'add', *server_credentials, '-an', gvar['user'] + '-wia1', '-cn', gvar['user'] + '-wic1'],
        # Alias to be deleted.
        ['alias', 'add', *server_credentials, '-an', gvar['user'] + '-wia2', '-cn', gvar['user'] + '-wic1'],
        # Alias to be updated.
        ['alias', 'add', *server_credentials, '-an', gvar['user'] + '-wia3', '-cn', gvar['user'] + '-wic1'],
        # Cloud metadata that should always exist.
        ['cloud', 'metadata-load', *server_credentials, '-mn', gvar['user'] + '-wicm1', '-cn', gvar['user'] + '-wic3', '-f', gvar['metadata_path']],
        # Cloud metadata to be deleted.
        ['cloud', 'metadata-load', *server_credentials, '-mn', gvar['user'] + '-wicm2', '-cn', gvar['user'] + '-wic3', '-f', gvar['metadata_path']],
        # Cloud metadata to be updated.
        ['cloud', 'metadata-load', *server_credentials, '-mn', gvar['user'] + '-wicm3', '-cn', gvar['user'] + '-wic3', '-f', gvar['metadata_path']],
        # Cloud YAML metadata to be updated.
        ['cloud', 'metadata-load', *server_credentials, '-mn', gvar['user'] + '-wicm4.yaml', '-cn', gvar['user'] + '-wic3', '-f', gvar['metadata_yaml_path']],
        # Group metadata that should always exist.
        ['metadata', 'load', *server_credentials, '-mn', gvar['user'] + '-wigm1', '-f', gvar['metadata_path']],
        # Group metadata to be deleted.
        ['metadata', 'load', *server_credentials, '-mn', gvar['user'] + '-wigm2', '-f', gvar['metadata_path']],
        # Group metadata to be updated.
        ['metadata', 'load', *server_credentials, '-mn', gvar['user'] + '-wigm3', '-f', gvar['metadata_path']]
    ]

    print('Creating test objects. Run `util.py -c` later to remove them.')
    for command in setup_commands:
        try:
            process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print('.', end='', flush=True)
        except subprocess.CalledProcessError as err:
            raise Exception('Error setting up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(err.cmd), err.stderr.decode(), err.stdout.decode()))
    print()

def cleanup(gvar):
    '''Delete all the test objects created by setup().'''

    # Deleting groups deletes all the aliases, clouds, etc. in the groups.
    cleanup_commands = [['group', 'delete', '-gn', '{}-wig{}'.format(gvar['user'], i), '-Y'] for i in range(1, 5)]
    cleanup_commands.extend([['user', 'delete', '-un', '{}-wiu{}'.format(gvar['user'], j), '-Y'] for j in range(1, 6)])

    print('Removing test objects.')
    for command in cleanup_commands:
        process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        print('.', end='', flush=True)
        # We want to know if the server returns an unexpected HTTP status code, but not if it failed just because the object did not exist.
        if process.returncode > 1:
            raise Exception('Error cleaning up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(command), process.stderr.decode(), process.stdout.decode()))
    print()

def format_command(command):
    '''Format a list of parameters so that when the formatted string is printed it can be copy-pasted to re-run the command.'''
    import re

    return ' '.join((word if re.fullmatch(r'[\w\-\.]+', word) else '\'{}\''.format(word) for word in command))

if __name__ == '__main__':
    main()
