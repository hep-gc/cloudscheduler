from cloudscheduler.unit_tests.unit_test_common import generate_secret, load_settings
import os.path

def setup():
    '''Load global settings and create test objects.'''
    import subprocess

    metadata_path = '../notyamlfile.txt'
    gvar = load_settings(web=True)

    if gvar['web']['setup_required']:
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
            ['cloud', 'metadata-load', *server_credentials, '-mn', '{}-wicm1'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user']), '-f', metadata_path],
            # Cloud metadata to be deleted.
            ['cloud', 'metadata-load', *server_credentials, '-mn', '{}-wicm2'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user']), '-f', metadata_path],
            # Cloud metadata to be updated.
            ['cloud', 'metadata-load', *server_credentials, '-mn', '{}-wicm3'.format(gvar['user']), '-cn', '{}-wic1'.format(gvar['user']), '-f', metadata_path],
            # Group metadata that should always exist.
            ['metadata', 'load', *server_credentials, '-mn', '{}-wigm1'.format(gvar['user']), '-f', metadata_path],
            # Group metadata to be deleted.
            ['metadata', 'load', *server_credentials, '-mn', '{}-wigm2'.format(gvar['user']), '-f', metadata_path],
            # Group metadata to be updated.
            ['metadata', 'load', *server_credentials, '-mn', '{}-wigm3'.format(gvar['user']), '-f', metadata_path]
        ]

        print('Creating test objects. Run cleanup.py later to remove them.', end='')
        for command in setup_commands:
            try:
                process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, encoding='utf-8', errors='ignore')
                print('.', end='', flush=True)
            except subprocess.CalledProcessError as err:
                raise Exception('Error setting up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(err.cmd), err.stderr, err.stdout))
        print()

        set_setup_required(False)
    return gvar

def cleanup(gvar):
    '''Delete all the test objects created by setup().'''
    import subprocess

    cleanup_commands = [['group', 'delete', '-gn', '{}-wig{}'.format(gvar['user'], i), '-Y'] for i in range(1, 5)]
    cleanup_commands.extend([['user', 'delete', '-un', '{}-wiu{}'.format(gvar['user'], j), '-Y'] for j in range(1, 6)])

    print('Removing test objects.', end='')
    for command in cleanup_commands:
        process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8', errors='ignore')
        print('.', end='', flush=True)
        # We want to know if the server returns an unexpected HTTP status code, but not if it failed just because the object did not exist.
        if process.returncode > 1:
            raise Exception('Error cleaning up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(command), process.stderr, process.stdout))
    print()

    set_setup_required(True)

def set_setup_required(set_to=True):
    import yaml

    try:
        with open(CREDENTIALS_PATH) as credentials_file:
            settings = yaml.safe_load(credentials_file)
    except FileNotFoundError:
        load_settings()
        with open(CREDENTIALS_PATH) as credentials_file:
            settings = yaml.safe_load(credentials_file)
    except yaml.YAMLError as err:
        print('YAML encountered an error while parsing {}: {}'.format(credentials_path, err))
    
    settings['web']['setup_required'] = set_to

    with open(CREDENTIALS_PATH, 'w') as credentials_file:
        credentials_file.write(yaml.safe_dump(settings))

def format_command(command):
    '''Format a list of parameters so that when the formatted string is printed it can be copy-pasted to re-run the command.'''
    import re

    return ' '.join((word if re.fullmatch(r'[\w\-\.]+', word) else '\'{}\''.format(word) for word in command))

def test_nav(self, privileged=False):
    '''Factor out testing the top navigation.'''
    import re

    expected_nav_links = [('/cloud/status/', 'Status'), ('/cloud/list/', 'Clouds'), ('/alias/list/', 'Aliases'), ('/group/defaults/', 'Defaults'), ('/images/', 'Images'), ('/keypairs/', 'Keys'), ('/user/settings/', 'User Settings'), ('/settings/log-out', 'Log out')]
    if privileged:
        # Insert these tuples starting at position 6.
        expected_nav_links[6:6] = [('/user/list/', 'Users'), ('/group/list/', 'Groups'), ('/server/config/', 'Config')]
    top_nav = self.driver.find_element_by_class_name('top-nav')
    nav_links = [(re.match(self.gvar['address'] + r'([^?]+)', elem.get_attribute('href'))[1], elem.get_attribute('innerHTML')) for elem in top_nav.find_elements_by_tag_name('a')]
    self.assertEqual(nav_links, expected_nav_links)

def assert_exactly_one(parent, by, identifier, error_reporter, missing_message=None, multiple_message=None):
    '''
    Assert that a parent element contains precisely one child element matching a given identifier, and return this child.
    parent (selenium.webdriver.firefox.webdriver.WebDriver, selenium.webdriver.firefox.webelement.FirefoxWebElement, or similar for a different browser): The driver or element expected to contain one element matching the identifier.
    by (str): Indicates what type of identifier `identifier` is, e.g. 'tag name'. These constants can be found at selenium.webdriver.common.by.By.
    identifier (str): Identifies the object to expect.
    error_reporter (usually unittest.TestCase.fail): Will be called with an error message (str) if the expectation fails.
    missing_message (str): May be given to specify a custom error message used when zero matching elements are found.
    multiple_message (str): May be given to specify a custom error message used when more than one matching element is found.
    '''

    default_message = 'Expected 1 element with {} \'{}\', but found {}'
    elements = parent.find_elements(by, identifier)
    count = len(elements)
    if count == 0:
        test_case.fail(missing_message if missing_message else default_message.format(by, identifier, 0))
    elif count == 1:
        return elements[0]
    else:
        test_case.fail(multiple_message if multiple_message else default_message.format(by, identifier, count))

def submit_form(form, data, error_reporter):
    '''
    Fill a form with the specified data and submit it.
    form (selenium.webdriver.firefox.webelement.FirefoxWebElement, or similar for a different browser): The form element to fill out.
    data (dict): Maps the `name` attributes of `<input>` elements in the form to the values that they should have. These values should be bools for checkboxes and radio buttons, and strs for text entries.
    error_reporter (usually unittest.TestCase.fail): Will be called with an error message if an unexpected input type is encountered.
    '''
    from selenium.webdriver.common.by import By
    for parameter, value in data.items():
        input_elem = assert_exactly_one(add_form, By.NAME, parameter, 'Input for {} is missing.'.format(parameter))
        input_type = input_elem.get_attribute('type')
        if input_type == 'checkbox':
            if value != input_elem.is_selected():
                input_elem.click()
        elif input_type == 'radio':
            if value == input_elem.get_attribute('value'):
                input_elem.click()
        elif input_type == 'text':
            input_elem.send_keys(value)
        else:
            failer('Unrecognized input type \'{}\''.format(input_type))
    next((input_elem for input_elem in form.find_elements_by_tag_name('input') if input_elem.get_attribute('type') == 'submit')).click()
