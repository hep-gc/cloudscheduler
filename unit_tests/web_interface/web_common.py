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
    import os.path
    import yaml

    credentials_path = os.path.expanduser('~/cloudscheduler/unit_tests/credentials.yaml')
    try:
        with open(credentials_path) as credentials_file:
            settings = yaml.safe_load(credentials_file)
    except FileNotFoundError:
        load_settings()
        with open(credentials_path) as credentials_file:
            settings = yaml.safe_load(credentials_file)
    except yaml.YAMLError as err:
        print('YAML encountered an error while parsing {}: {}'.format(credentials_path, err))
    
    settings['web']['setup_required'] = set_to

    with open(credentials_path, 'w') as credentials_file:
        credentials_file.write(yaml.safe_dump(settings))

def format_command(command):
    '''Format a list of parameters so that when the formatted string is printed it can be copy-pasted to re-run the command.'''
    import re

    return ' '.join((word if re.fullmatch(r'[\w\-\.]+', word) else '\'{}\''.format(word) for word in command))

def assert_exactly_one(parent, identifier, attributes=None, error_reporter=print, missing_message=None, multiple_message=None):
    '''
    Assert that a parent element contains precisely one child element matching the given identifier(s) and attribute(s), and return this child.
    parent (selenium.webdriver.firefox.webdriver.WebDriver, selenium.webdriver.firefox.webelement.FirefoxWebElement, or similar for a different browser): The driver or element expected to contain one element matching the identifier.
    identifier (2-tuple): Specifies an identifier, e.g. 'tag name', and the value that the child must have for this identifier, e.g. 'form'. A list of identifiers can be found at selenium.webdriver.common.by.By.
    attributes (dict): Maps the names of attributes, e.g. 'type', to the values that the child is expected to have, e.g. 'checkbox'.
    error_reporter (usually unittest.TestCase.fail): Will be called with an error message (str) if the expectation fails.
    missing_message (str): May be given to specify a custom error message used when zero matching elements are found.
    multiple_message (str): May be given to specify a custom error message used when more than one matching element is found.
    '''

    if not attributes:
        attributes = {}
    default_message = 'Expected 1 element with identifier {} and attributes {}, but found {}'
    matching_elems = []
    for elem in parent.find_elements(*identifier):
        if all(elem.get_attribute(att_name) == att_value for att_name, att_value in attributes.items()):
            matching_elems.append(elem)

    if len(matching_elems) == 0:
        error_reporter(missing_message if missing_message else default_message.format(identifier, attributes, 0))
    elif len(matching_elems) == 1:
        return matching_elems[0]
    else:
        error_reporter(multiple_message if multiple_message else default_message.format(identifier, attributes, len(matching_elems)))

def submit_form(form, parameters, waiter=None, expected_response_regex=None, assert_values_retained=None, error_reporter=print):
    '''
    Fill a form with the specified parameters and submit it.
    form (selenium.webdriver.firefox.webelement.FirefoxWebElement, or similar for a different browser): The form element to fill out.
    parameters (dict): Maps the `name` attributes of <input> elements in the form to the values that they should have. These values should be bools for checkboxes and radio buttons, and objects that can be cast to strs for text entries. Any <input>s which are not mapped will not be touched. The value for a <select> tag should be the visible text of an option (not its `value` attribute).
    waiter (selenium.webdriver.support.ui.WebDriverWait or None): TODO.
    expected_response_regex (str): TODO.
    assert_values_retained (bool): If True, assume that after the form is submitted, another form with the same name will appear in the new page. Wait for the old form to become stale, then again to wait for the new form to appear. Assert that all of the parameters given match the values in the new form (except for <input>s with type='password'). Otherwise, return immediately after submitting the form.
    error_reporter (callable, usually unittest.TestCase.fail): Will be called with an error message if an unexpected input type is encountered. Therefore, this function will not continue with remaining fields if `error_reporter` raises an exception.
    Forms are allowed to be dynamic; i.e. fields are allowed to completely change in response to previous fields being filled out.
    '''
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions
    import re

    for parameter, value in parameters.items():
        entries = form.find_elements_by_name(parameter)
        if entries:
            for entry in entries:
                entry_tag_name = get_tag_name(entry)
                if entry_tag_name == 'input':
                    input_type = entry.get_attribute('type')
                    if input_type == 'checkbox':
                        if value != entry.is_selected():
                            entry.click()
                    # Sometimes two inputs will have the same name and one will be hidden. We want to ignore the hidden one.
                    elif input_type == 'hidden':
                        continue
                    elif input_type == 'radio':
                        if value == entry.get_attribute('value'):
                            entry.click()
                    elif input_type in ['number', 'password', 'text']:
                        entry.clear()
                        entry.send_keys(str(value))
                    else:
                        error_reporter('Unrecognized <input> type \'{}\' for parameter \'{}\'.'.format(input_type, parameter))
                elif entry_tag_name == 'select':
                    assert_exactly_one(entry, (By.TAG_NAME, 'option'), {'text': value}, error_reporter, missing_message='Option \'{}\' not found for parameter \'{}\'.'.format(value, parameter)).click()
                else:
                    error_reporter('Unrecognized tag name <{}> for parameter \'{}\'.'.format(entry_tag_name, parameter))
        # No entries were found.
        else:
            error_reporter('Input for \'{}\' is missing.'.format(parameter))

    form_name = form.get_attribute('name')
    assert_exactly_one(form, (By.TAG_NAME, 'input'), {'type': 'submit'}, error_reporter, missing_message='<input> with type=\'submit\' not found.').click()

    if expected_response_regex:
        waiter.until(expected_conditions.staleness_of(form))
        actual_response = assert_exactly_one(driver, (By.ID, 'message'), None, error_reporter).text
        if not re.search(expected_response_regex, actual_response):
            error_reporter('Expected a response matching \'{}\', but received \'{}\'.'.format(expected_response_regex, actual_response))

    if assert_values_retained:
        waiter.until(expected_conditions.staleness_of(form))
        new_form = waiter.until(expected_conditions.presence_of_element_located((By.XPATH, './/form[@name="{}"]'.format(form_name))))
        for parameter, expected_value in parameters.items():
            try:
                entry = new_form.find_element_by_name(parameter)
            except NoSuchElementException:
                error_reporter('Input for \'{}\' is missing.'.format(parameter))
            entry_tag_name = get_tag_name(entry)
            if entry_tag_name == 'input':
                entry_type = entry.get_attribute('type')
                if entry_type == 'checkbox':
                    actual_value = entry.is_selected() 
                elif entry_type == 'hidden' or entry_type == 'password':
                    continue
                elif entry_type == 'number' or entry_type == 'text':
                    actual_value = entry.get_attribute('value') 
                else:
                    error_reporter('Unrecognized <input> type \'{}\' for parameter \'{}\'.'.format(input_type, parameter))
            elif entry_tag_name == 'select':
                actual_value = next(filter(lambda option: option.is_selected(), entry.find_elements_by_tag_name('option'))).get_attribute('text')
            else:
                error_reporter('Unrecognized tag name <{}> for parameter \'{}\'.'.format(entry_tag_name, parameter))
            if isinstance(expected_value, (int, float)):
                try:
                    actual_value = float(actual_value)
                except ValueError:
                    error_reporter('Expected the number {} for the parameter \'{}\', but found \'{}\', which is not parsable as a number.'.format(expected_value, parameter, actual_value))
            # The values here may be strs, floats, a float and an int, or bools.
            if actual_value != expected_value:
                error_reporter('Expected {} for the parameter \'{}\', but found {}.'.format(expected_value, parameter, actual_value))

def parameters_submissions(form, parameters, error_reporter):
    '''Similar in concept to unit_test_common.parameters_requests and parameters_commands.'''
    
    mandatory_params = {name: details['valid'] for name, details in parameters.items() if details.get('mandatory')}

    for p_name, p_details in parameters.items():
        if p_details.get('mandatory'):
            # Temporarily remove.
            del mandatory_params[p_name]
            submit_form(form, 
        # Give the parameter with invalid values.
        for value, message in p_details['test_cases'].items():
            execute_csv2_request(
                gvar, 1, None, message,
                request, group=group, form_data={p_name: value, **mandatory_params}, server_user=server_user
            )
        # Add the parameter back in if it was mandatory.
        if p_details.get('mandatory'):
            mandatory_params[p_name] = p_details['valid']

def get_tag_name(element):
    return element.get_attribute('outerHTML').split(maxsplit=1)[0][1:]

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

