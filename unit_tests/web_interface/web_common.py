def assert_exactly_one(parent, driver_wait, error_reporter, identifier, attributes=None, missing_message=None, multiple_message=None):
    '''
    Assert that a parent element contains precisely one child element matching the given identifier(s) and attribute(s), and return this child.
    parent (selenium.webdriver.firefox.webdriver.WebDriver, selenium.webdriver.firefox.webelement.FirefoxWebElement, or similar for a different browser): The driver or element expected to contain one element matching the identifier.
    identifier (2-tuple): Specifies an identifier, e.g. 'tag name', and the value that the child must have for this identifier, e.g. 'form'. A list of identifiers can be found at selenium.webdriver.common.by.By.
    attributes (dict): Maps the names of attributes, e.g. 'type', to the values that the child is expected to have, e.g. 'checkbox'.
    error_reporter (usually unittest.TestCase.fail): Will be called with an error message (str) if the expectation fails.
    missing_message (str): May be given to specify a custom error message used when zero matching elements are found.
    multiple_message (str): May be given to specify a custom error message used when more than one matching element is found.
    '''
    from selenium.webdriver.support import expected_conditions as ec

    if not attributes:
        attributes = {}
    default_message = 'Expected 1 element with identifier {} and attributes {}, but found {}'
    matching_elems = []
    for elem in driver_wait.until(ec.presence_of_all_elements_located(identifier)):
        if all(elem.get_attribute(att_name) == att_value for att_name, att_value in attributes.items()):
            matching_elems.append(elem)

    if len(matching_elems) == 0:
        error_reporter(missing_message if missing_message else default_message.format(identifier, attributes, 0))
    elif len(matching_elems) == 1:
        return matching_elems[0]
    else:
        error_reporter(multiple_message if multiple_message else default_message.format(identifier, attributes, len(matching_elems)))

def submit_form(driver, driver_wait, error_reporter, form_xpath, data, expected_response=None, retains_values=False):
    '''
    Fill a form with the specified data and submit it.
    driver (selenium.webdriver.firefox.webdriver.WebDriver or similar for a different browser): The driver that contains the form.
    form_xpath (str): An absolute XPath that uniquely identifies the form element to fill out.
    data (dict): Maps the `name` attributes of <input> and <select> elements in the form to the values that they should have. These values should be bools for checkboxes and radio buttons, objects that can be cast to strs for text entries, and the visible text of an option (not its `value` attribute) as a str for <select> tags. Any <input>s which are not mapped will not be touched.
    error_reporter (callable, usually unittest.TestCase.fail): Will be called with an error message if an unexpected input type is encountered. Therefore, this function will not continue with remaining fields if `error_reporter` raises an exception.
    max_wait (number): The maximum number of seconds to wait for the form to become stale after submitting it if `expected_response` or `retains_values` are specified, and in the latter case to wait for another form with the same name to appear.
    expected_response (str): If given, assume submitting the form will generate a response containing an element with id='message', and assert that `expected_response` is in its content.
    retains_values (bool): If True, assume that after the form is submitted, a new page will be served containing a form with the same name. After waiting for the old form to become stale, wait for the new form to appear. Assert that all of the data given match the values in the new form (except for <input>s with type='password', which are ignored).
    Forms are allowed to be dynamic; i.e. fields are allowed to completely change in response to previous fields being filled out.
    '''
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as ec
    import re

    form = assert_exactly_one(driver, driver_wait, error_reporter, (By.XPATH, form_xpath))
    for parameter, value in data.items():
        entries = driver_wait.until(ec.presence_of_all_elements_located((By.XPATH, '{}//*[@name="{}"]'.format(form_xpath, parameter))))
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
                    assert_exactly_one(entry, driver_wait, error_reporter, (By.XPATH, '{}//select[@name="{}"]//option[text()="{}"]'.format(form_xpath, parameter, value)), missing_message='Option \'{}\' not found for parameter \'{}\'.'.format(value, parameter)).click()
                else:
                    error_reporter('Unrecognized tag name <{}> for parameter \'{}\'.'.format(entry_tag_name, parameter))
        # No entries were found.
        else:
            error_reporter('Input for \'{}\' is missing.'.format(parameter))

    # Submit the form.
    assert_exactly_one(form, driver_wait, error_reporter, (By.XPATH, '{}//input[@type="submit"]'.format(form_xpath)), missing_message='<input> with type=\'submit\' not found.').click()

    driver_wait.until(ec.staleness_of(form))
    if expected_response:
        actual_response = driver_wait.until(ec.presence_of_element_located((By.ID, 'message'))).text
        if expected_response not in actual_response:
            error_reporter('Expected a response containing \'{}\', but received \'{}\'.'.format(expected_response, actual_response))

    if retains_values:
        new_data = get_data_from_form(driver, driver_wait, error_reporter, form_xpath)
        print(f'DEBUG: {new_data}')
        # Iterating over the old values allows us to ignore values that were in the form but never specified in data.
        for parameter, old_value in data.items():
            # Allow values in parameters to be given as ints or floats but come back from the server as strs.
            try:
                new_data[parameter] = float(new_data[parameter])
            except KeyError:
                error_reporter('Expected the parameter \'{}\' to be retained, but the entry for it was missing.'.format(parameter))
            except ValueError:
                pass
            if new_data[parameter] != old_value:
                error_reporter('Expected {} to be retained for the parameter \'{}\', but found {}.'.format(old_value, parameter, new_data[parameter]))

def parameters_submissions(driver, driver_wait, error_reporter, form_xpath, parameters, clicked_before_submitting=None):
    '''
    Submit forms with parameter combinations that are expected to fail.
    driver (selenium.webdriver.firefox.webdriver.WebDriver or similar for a different browser): The driver that contains the form to submit.
    form_xpath (str): An absolute XPath that uniquely identifies the form element to fill out.
    parameters (dict): TODO
    error_reporter (callable, usually unittest.TestCase.fail): Will be called with an error message if an unexpected input type is encountered. Therefore, this function will not continue with remaining fields if `error_reporter` raises an exception.
    max_wait (float): The maximum number of seconds to wait for the web interface to process requests. Passed on to `submit_form`.
    clicked_before_submitting (str or None): The absolute XPath of an element. If given, this element will be clicked before every form submission. This is usually used to cause the form to become visible again.
    '''
    from selenium.webdriver.common.by import By

    mandatory_params = {name: details[1] for name, details in parameters.items() if len(details) > 1}
    if clicked_before_submitting:
        for p_name, p_details in parameters.items():
            for value, message in p_details[0].items():
                assert_exactly_one(driver, driver_wait, error_reporter, (By.XPATH, clicked_before_submitting)).click()
                # mandatory_params are listed first so that p_name overwrites them as necessary.
                submit_form(driver, driver_wait, error_reporter, form_xpath, {**mandatory_params, p_name: value}, expected_response=message)
    else:
        for p_name, p_details in parameters.items():
            for value, message in p_details[0].items():
                submit_form(driver, driver_wait, error_reporter, form_xpath, {**mandatory_params, p_name: value}, expected_response=message)

def get_data_from_form(driver, driver_wait, error_reporter, form_xpath):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as ec

    form = assert_exactly_one(driver, driver_wait, error_reporter, (By.XPATH, form_xpath))
    data = {}
    for input_ in driver_wait.until(ec.presence_of_all_elements_located((By.XPATH, '{}//input'.format(form_xpath)))):
        print(f'DEBUG: {get_open_tag(input_)}')
        input_type = input_.get_attribute('type')
        input_name = input_.get_attribute('name')
        # All inputs with no name are ignored.
        if input_name:
            if input_type == 'checkbox':
                data[input_name] = input_.is_selected() 
            # Password fields are assumed to be blank when received from the server.
            elif input_type == 'hidden' or input_type == 'password':
                continue
            elif input_type == 'number' or input_type == 'range':
                value = input_.get_attribute('value')
                try:
                    data[input_name]: float(value)
                except ValueError:
                    error_reporter('Found an <input> with name=\'{}\', type=\'number\', and a value of \'{}\', which is not parsable as a float.'.format(input_name, value))
            elif input_type == 'text':
                data[input_name] = input_.get_attribute('value') 
            else:
                error_reporter('Unrecognized <input> type \'{}\' with name \'{}\'.'.format(input_type, input_name))

    driver_wait.until(ec.presence_of_all_elements_located((By.TAG_NAME, 'select')))
    for select in driver_wait.until(ec.presence_of_all_elements_located((By.XPATH, '{}//select'.format(form_xpath)))):
        select_name = select.get_attribute('name')
        if select_name:
            try:
                data[select_name] = next(filter(lambda option: option.is_selected(), select.find_elements_by_tag_name('option'))).text
            except StopIteration:
                # WebDriver defaults to the first option if the HTML does not specify which is selected (at least for Firefox), so this should only occur if there are no options.
                continue

    return data

def assert_nav(driver, driver_wait, error_reporter, address, privileged=False):
    '''Factor out testing the top navigation.'''
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as ec
    import re

    expected_nav_links = [('/cloud/status/', 'Status'), ('/cloud/list/', 'Clouds'), ('/alias/list/', 'Aliases'), ('/group/defaults/', 'Defaults'), ('/images/', 'Images'), ('/keypairs/', 'Keys'), ('/user/settings/', 'User Settings'), ('/settings/log-out', 'Log out')]
    if privileged:
        # Insert these tuples starting at position 6.
        expected_nav_links[6:6] = [('/user/list/', 'Users'), ('/group/list/', 'Groups'), ('/server/config/', 'Config')]
    top_nav = assert_exactly_one(driver, driver_wait, error_reporter, (By.CLASS_NAME, 'top-nav'), missing_message='The top navigation is missing.')
    nav_links = []
    link_pattern = re.escape(address) + r'(/[^?]+)'
    for elem in top_nav.find_elements_by_tag_name('a'):
        link_match = re.match(link_pattern, elem.get_attribute('href'))
        if link_match:
            nav_links.append((link_match[1], elem.get_attribute('innerHTML')))
        else:
            error_reporter('Expected the link {} to match the pattern {}'.format(get_open_tag(elem), link_pattern))
    if nav_links != expected_nav_links:
        error_reporter('Expected the top nav to contain the links {}, but found the links {}.'.format(expected_nav_links, nav_links))

def setup(address_extension):
    '''Load global settings and create test objects.'''
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.support import expected_conditions as ec, wait
    import subprocess
    from cloudscheduler.unit_tests.unit_test_common import load_settings

    metadata_path = '../notyamlfile.txt'
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

        print('Creating test objects. Run cleanup.py later to remove them.')
        for command in setup_commands:
            try:
                process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                print('.', end='', flush=True)
            except subprocess.CalledProcessError as err:
                raise Exception('Error setting up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(err.cmd), err.stderr, err.stdout))
        print()
        set_setup_required(False)

    gvar['driver'] = webdriver.Firefox(webdriver.FirefoxProfile(gvar['firefox_profile']))
    try:
        gvar['wait'] = wait.WebDriverWait(gvar['driver'], gvar['max_wait'])
        # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
        gvar['driver'].get(gvar['address'] + address_extension)
        # The Firefox profile will automatically fill in the server credentials, so we just accept the prompt.
        gvar['wait'].until(ec.alert_is_present()).accept()
    except TimeoutException:
        gvar['driver'].quit()
        raise
    return gvar

def cleanup(gvar):
    '''Delete all the test objects created by setup().'''
    import subprocess

    cleanup_commands = [['group', 'delete', '-gn', '{}-wig{}'.format(gvar['user'], i), '-Y'] for i in range(1, 5)]
    cleanup_commands.extend([['user', 'delete', '-un', '{}-wiu{}'.format(gvar['user'], j), '-Y'] for j in range(1, 6)])

    print('Removing test objects.')
    for command in cleanup_commands:
        process = subprocess.run(['cloudscheduler', *command, '-s', 'unit-test'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        print('.', end='', flush=True)
        # We want to know if the server returns an unexpected HTTP status code, but not if it failed just because the object did not exist.
        if process.returncode > 1:
            raise Exception('Error cleaning up tests.\ncmd={}\nstderr={}\nstdout={}'.format(format_command(command), process.stderr, process.stdout))
    print()

    set_setup_required(True)

def set_setup_required(set_to=True):
    import os.path
    import yaml
    from cloudscheduler.unit_tests.unit_test_common import load_settings

    credentials_path = os.path.expanduser('~/cloudscheduler/unit_tests/credentials.yaml')
    try:
        with open(credentials_path) as credentials_file:
            settings = yaml.safe_load(credentials_file)
    except FileNotFoundError:
        load_settings(web=True)
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

def get_tag_name(element):
    '''Return the tag name of an element.'''
    return element.get_attribute('outerHTML').split(maxsplit=1)[0][1:]

def get_open_tag(element):
    '''Return the opening tag of an element (including all of the attributes defined in it).'''
    return element.get_attribute('outerHTML').split('>', maxsplit=1)[0] + '>'
