from cloudscheduler.unit_tests.unit_test_common import generate_secret, load_settings
import os
import re
import subprocess
import sys
import yaml

# os.makedirs() may get confused if '..' is used in WEB_SETTINGS_FILE.
WEB_SETTINGS_FILE = 'web_settings.yaml'
YAML_METADATA_FILE = '../ut.yaml'
NON_YAML_METADATA_FILE = '../notyamlfile.txt'

def setup():
    '''Load global settings and create test objects.'''
    gvar = load_settings(web=True)

    if gvar['setup_required']:
        cleanup(gvar)

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
            ['group', 'add', '-gn', '{}-wig1'.format(gvar['user']), '-htcf', gvar['fqdn']],
            # Group with no users.
            ['group', 'add', '-gn', '{}-wig2'.format(gvar['user']), '-htcf', gvar['fqdn']],
            # Group to be deleted.
            ['group', 'add', '-gn', '{}-wig3'.format(gvar['user']), '-htcf', gvar['fqdn']],
            # Group to be updated.
            ['group', 'add', '-gn', '{}-wig4'.format(gvar['user']), '-htcf', gvar['fqdn'],
                '--htcondor-container-hostname', 'unit-test.ca',
                '--htcondor-users', '{}-wiu1'.format(gvar['user']),
                '--job-cores', '3',
                '--job-disk', '1',
                '--job-ram', '4',
                '--job-swap', '1'],
            # User used to perform most actions not requiring privileges.
            ['user', 'add', '-un', '{}-wiu1'.format(gvar['user']), '-upw', gvar['user_secret'],
                '--group-name', '{}-wig1'.format(gvar['user'])],
            # User used to perform most actions requiring privileges.
            ['user', 'add', '-un', '{}-wiu2'.format(gvar['user']), '-upw', gvar['user_secret'],
                '--group-name', '{}-wig1'.format(gvar['user']),
                '--super-user', 'True'],
            # User who is not in any groups.
            ['user', 'add', '-un', '{}-wiu3'.format(gvar['user']), '-upw', gvar['user_secret']],
            # User to be deleted.
            ['user', 'add', '-un', '{}-wiu4'.format(gvar['user']), '-upw', gvar['user_secret'],
                '--group-name', '{}-wig1'.format(gvar['user'])],
            # User to be updated.
            ['user', 'add', '-un', '{}-wiu5'.format(gvar['user']), '-upw', gvar['user_secret'],
                '--group-name', '{}-wig1'.format(gvar['user']),
                '--user-common-name', '{} user 5'.format(gvar['user'])],
            # Cloud that should always exist to create aliases for.
            cloud_template + ['-cn', '{}-wic1'.format(gvar['user'])],
            # Cloud to be deleted.
            cloud_template + ['-cn', '{}-wic2'.format(gvar['user'])],
            # Cloud to be updated.
            cloud_template + ['-cn', '{}-wic3'.format(gvar['user'])],
            # Alias that should always exist.
            ['alias', 'add', *server_credentials, '-an', '{}-wia1'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user'])],
            # Alias to be updated and deleted.
            ['alias', 'add', *server_credentials, '-an', '{}-wia2'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user'])],
            # Cloud metadata that should always exist.
            ['cloud', 'metadata-load', *server_credentials, '-mn', '{}-wicm1'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user']), '-f', NON_YAML_METADATA_FILE],
            # Cloud metadata to be deleted.
            ['cloud', 'metadata-load', *server_credentials, '-mn', '{}-wicm2'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user']), '-f', NON_YAML_METADATA_FILE],
            # Cloud metadata to be updated.
            ['cloud', 'metadata-load', *server_credentials, '-mn', '{}-wicm3'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user']), '-f', NON_YAML_METADATA_FILE],
            # Group metadata that should always exist.
            ['metadata', 'load', *server_credentials, '-mn', '{}-wigm1'.format(gvar['user']), '-f', NON_YAML_METADATA_FILE],
            # Group metadata to be deleted.
            ['metadata', 'load', *server_credentials, '-mn', '{}-wigm2'.format(gvar['user']), '-f', NON_YAML_METADATA_FILE],
            # Group metadata to be updated.
            ['metadata', 'load', *server_credentials, '-mn', '{}-wigm3'.format(gvar['user']), '-f', NON_YAML_METADATA_FILE]
        ]

        print('Creating test objects. Run cleanup.py later to remove them.')
        for command in setup_commands:
            try:
                process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, encoding='utf-8', errors='ignore')
                print(f'DEBUG: {format_command(command)}')
            except subprocess.CalledProcessError as err:
                raise Exception('Error setting up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(err.cmd), err.stderr, err.stdout))

        set_setup_required(False)
    return gvar

def cleanup(gvar):
    '''Delete all the test objects created by setup().'''
    cleanup_commands = [['group', 'delete', '-gn', '{}-wig{}'.format(gvar['user'], i), '-Y'] for i in range(1, 5)]
    cleanup_commands.extend([['user', 'delete', '-un', '{}-wiu{}'.format(gvar['user'], j), '-Y'] for j in range(1, 6)])

    print('Removing test objects.')
    for command in cleanup_commands:
        process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8', errors='ignore')
        print(f'DEBUG: {format_command(command)}')
        # We want to know if the server returns an unexpected HTTP status code, but not if it failed just because the object did not exist.
        if process.returncode > 1:
            raise Exception('Error cleaning up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(command), process.stderr, process.stdout))

    set_setup_required(True)

def web_settings(setup_required=None):
    '''Return the web settings saved in WEB_SETTINGS_FILE, creating the file if it does not exist.'''
    try:
        with open(WEB_SETTINGS_FILE) as web_settings_file:
            settings = yaml.safe_load(web_settings_file.read())
    except FileNotFoundError:
        required = True
        setup_required = True
        # Create the web_settings file.
        print('Creating file at {} to remember if test objects are setup.'.format(WEB_SETTINGS_FILE))
        os.umask(0)
        dir_path = os.path.dirname(WEB_SETTINGS_FILE)
        if dir_path:
            os.makedirs(dir_path, mode=0o700, exist_ok=True)
    except ValueError:
        required = True
        setup_required = True
        print('Error: Failed to parse {}'.format(WEB_SETTINGS_FILE), file=sys.stderr)

def setup_required(
    if setup_required != None:
        with open(WEB_SETTINGS_FILE, 'w') as web_settings_file:
            web_settings_file.write(str(int(setup_required)))

    return required

def format_command(command):
    '''Format a list of parameters so that when the formatted string is printed it can be copy-pasted to re-run the command.'''
    return ' '.join((word if re.fullmatch(r'[\w\-\.]+', word) else '\'{}\''.format(word) for word in command))
