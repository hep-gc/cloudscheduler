DEFAULT_MAX_WAIT = 30

def assert_one(parent, error_reporter, identifier, attributes=None, missing_message=None, multiple_message=None):
    '''
    Assert that a parent element contains precisely one child element matching the given identifier and attribute(s), and return this child.
    parent_wait (selenium.webdriver.wait.WebDriverWait): A WebDriverWait for the driver or element expected to contain the child.
    error_reporter (callable, usually unittest.TestCase.fail): Will be called with an error message (str) as its first and only argument if any expectation fails.
    identifier (2-tuple): Specifies the identifier key (str), e.g. 'tag name', and the identifier value (str), e.g. 'form', that the child must have. The identifier key is usually retrieved from selenium.webdriver.common.by.By (which provides a definitive set of possible keys).
    attributes (dict or None): Maps the names of attributes, e.g. 'type', to the values that the child is expected to have for these attributes, e.g. 'checkbox'.
    missing_message (str or None): May be given to specify a custom error message to use when zero matching elements are found.
    multiple_message (str or None): May be given to specify a custom error message to use when multiple matching elements are found.
    '''
    from selenium.common.exceptions import TimeoutException

    if not attributes:
        attributes = {}
    default_message = 'Expected 1 element with identifier {} and attributes {}, but found {}'

    candidates = parent.find_elements(*identifier)
    if not candidates and attributes:
        error_reporter('Did not find any elements matching the identifier {} (before considering any attributes).'.format(identifier))
    else:
        matching_elems = set()
        for elem in candidates:
            for name, value in attributes.items():
                # Some attribute names, most of which are constants from selenium.webdriver.common.by.By, are handled in special ways.
                if name == 'link text':
                    if elem.get_attribute('href') != value:
                        break
                elif name == 'partial link text':
                    if value not in elem.get_attribute('href'):
                        break
                elif name == 'tag name':
                    if elem.tag_name != value:
                        break
                elif name == 'class name':
                    if elem.get_attribute('class') != value:
                        break
                elif name == 'text':
                    if elem.text != value:
                        break
                elif elem.get_attribute(name) != value:
                    break
            # If the loop didn't break.
            else:
                matching_elems.add(elem)

        if len(matching_elems) == 1:
            return matching_elems.pop()
        elif not matching_elems:
            error_reporter(missing_message if missing_message else default_message.format(identifier, attributes, 0))
        # len(matching_elems) > 1
        else:
            error_reporter(multiple_message if multiple_message else default_message.format(identifier, attributes, len(matching_elems)))


def submit_valid_combinations(driver, error_reporter, form_xpath, valid_combinations, mandatory_parameters=None, max_wait=DEFAULT_MAX_WAIT, expected_response=None, click_before_filling=None, retains_values=False):
    '''
    Submit a form multiple times with parameter combinations that are expected to succeed.
    driver (selenium.webdriver.support.wait.WebDriverWait): A WebDriverWait for the driver that contains the form to submit.
    error_reporter (callable, usually unittest.TestCase.fail): Will be called with an error message (str) as its first and only argument if an error occurs. Therefore, this function will *not* continue with any remaining submissions if and only if `error_reporter` raises an exception.
    form_xpath (str): An absolute XPath that uniquely identifies the form element to fill out. This allows it to be re-found after each submission.
    clicked_before_filling (str or None): An absolute XPath that uniquely identifies an element. May be given to indicate that an element should be clicked before each time that the form is filled out and submitted. This is usually used to cause the form to become visible again.
    '''
    from selenium.webdriver.common.by import By

    if not mandatory_parameters or retains_values:
        mandatory_parameters = {}

    for valid_combination in valid_combinations:
        if click_before_filling:
            assert_one(driver, error_reporter, (By.XPATH, click_before_filling)).click()
        # mandatory_parameters are listed first so that they are overwriten as necessary.
        submit_form(driver, error_reporter, form_xpath, {**mandatory_parameters, **valid_combination}, max_wait=max_wait, expected_response=expected_response, retains_values=retains_values)

def submit_invalid_combinations(driver, error_reporter, form_xpath, invalid_combinations, mandatory_parameters=None, max_wait=DEFAULT_MAX_WAIT, click_before_filling=None):
    '''
    Submit a form multiple times with parameter combinations that are expected to fail.
    driver, error_reporter, form_xpath: See `submit_valid_combinations`.
    parameters (dict): A dictionary which maps parameter names to tuples, each of length 1 or 2 and containing:
        A dictionary of test cases which maps bad values for the parameter to the error messages that they are expected to produce.
        Optional: A valid value for the parameter. If and only if this is provided, it will be specified in each form submission for other parameters. This is useful when a form requires certain fields, but comes back blank when it is submitted.
    clicked_before_filling (str or None): An absolute XPath that uniquely identifies an element. May be given to indicate that an element should be clicked before each time that the form is filled out and submitted. This is usually used to cause the form to become visible again.
    '''
    from selenium.webdriver.common.by import By

    if not mandatory_parameters:
        mandatory_parameters = {}

    for name, test_cases in invalid_combinations.items():
        for value, message in test_cases.items():
            if click_before_filling:
                assert_one(driver, error_reporter, (By.XPATH, click_before_filling)).click()
            # mandatory_parameters are listed first so that they are overwriten as necessary.
            submit_form(driver, error_reporter, form_xpath, {**mandatory_parameters, name: value}, max_wait=max_wait, expected_response=message)

def submit_form(driver, error_reporter, form_xpath, data, max_wait=DEFAULT_MAX_WAIT, expected_response=None, retains_values=False):
    '''
    Fill an HTML form with the specified data and submit it.
    driver (selenium.webdriver.support.waitWebDriverWait): A WebDriverWait for the driver that contains the form to submit. (This must be a driver, not an element, if retains_values, because all elements become stale when the form is submitted.)
    error_reporter (callable, usually unittest.TestCase.fail): Will be called with an error message (str) as its first and only argument if an error occurs. Therefore, this function will *not* continue with any remaining fields after an error if and only if `error_reporter` raises an exception.
    form_xpath (str): An absolute XPath that uniquely identifies the form element to fill out. (This allows the form to be re-found after it is submitted.)
    data (dict): Maps the `name` attributes of <input> and <select> elements in the form to the values that they should have. These values should be bools for checkboxes and radio buttons, objects that can be cast to strs for text entries, and the visible text of an option (not its `value` attribute) as a str for <select> tags. Any <input>s which are not mapped will not be silently ignored.
    expected_response (str or None): May be given to assert indicate that submitting the form will generate a response containing an element with id='message', and assert that `expected_response` is in its content.
    retains_values (bool): May be given as True to indicate that submitting the form will generate a response containing a form with the same name which contains all of the values just submitted. After submitting and waiting for the old form to become stale, wait for the new form to appear. Assert that all of the data given match the values in the new form (except for <input>s with type='password', which are ignored).
    Forms are allowed to be dynamic; i.e. fields are allowed to completely change in response to previous fields being filled out.
    '''
    from selenium.common.exceptions import ElementNotInteractableException
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as ec
    from selenium.webdriver.support.wait import WebDriverWait
    import re

    form = assert_one(driver, error_reporter, (By.XPATH, form_xpath))
    for parameter, value in data.items():
        # Re-finding the entries each time is necessary to support dynamic forms.
        entries = driver.find_elements(By.XPATH, '{}//*[@name="{}"]'.format(form_xpath, parameter))
        if entries:
            for entry in entries:
                entry_tag_name = entry.tag_name
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
                    assert_one(driver, error_reporter, (By.XPATH, '{}//select[@name="{}"]//option[text()="{}"]'.format(form_xpath, parameter, value)), missing_message='Option \'{}\' not found for parameter \'{}\'.'.format(value, parameter)).click()
                elif entry_tag_name == 'textarea':
                    try:
                        entry.send_keys(value)
                    except ElementNotInteractableException:
                        # Assume it is an ace_editor, which are tricky.
                        ace_input = assert_one(form, error_reporter, (By.CLASS_NAME, 'ace_editor'))
                        # Clear any old value and enter the new value.
                        ActionChains(driver).click(ace_input).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE + value).perform()
                else:
                    error_reporter('Unrecognized tag name <{}> for parameter \'{}\'.'.format(entry_tag_name, parameter))
        # No entries were found.
        else:
            error_reporter('Input for \'{}\' is missing.'.format(parameter))

    form.submit()
    WebDriverWait(driver, max_wait).until(ec.staleness_of(form))

    if expected_response:
        actual_response = assert_one(driver, error_reporter, (By.ID, 'message')).text
        if expected_response not in actual_response:
            error_reporter('Expected a response containing \'{}\', but received \'{}\'.'.format(expected_response, actual_response))

    if retains_values:
        new_data = get_data_from_form(driver, error_reporter, form_xpath)
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

def get_data_from_form(driver, error_reporter, form_xpath, max_wait=DEFAULT_MAX_WAIT):
    '''
    Retrieve the data currently in an HTML form.
    driver (selenium.webdriver.support.wait.WebDriverWait): A WebDriverWait for the driver that contains the form to retrieve data from.
    error_reporter (callable, usually unittest.TestCase.fail): Will be called with an error message (str) as its first and only argument if an error occurs. Therefore, this function will *not* continue with any remaining fields if and only if `error_reporter` raises an exception.
    form_xpath (str): An absolute XPath that uniquely identifies the form to retrieve data from.
    '''
    from selenium.webdriver.common.by import By

    form = assert_one(driver, error_reporter, (By.XPATH, form_xpath))
    data = {}
    # Many forms only have one type of entry, and Selenium implicitly waits for each type of entry, so we temporarily decrease the wait time.
    driver.implicitly_wait(0.1)
    for input_ in form.find_elements(By.TAG_NAME, 'input'):
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
                    data[input_name] = float(value)
                except ValueError:
                    error_reporter('Found an <input> with name=\'{}\', type=\'number\', and a value of \'{}\', which is not parsable as a float.'.format(input_name, value))
            elif input_type == 'text':
                data[input_name] = input_.get_attribute('value') 
            else:
                error_reporter('Unrecognized <input> type \'{}\' with name \'{}\'.'.format(input_type, input_name))

    for select in form.find_elements(By.TAG_NAME, 'select'):
        select_name = select.get_attribute('name')
        if select_name:
            try:
                data[select_name] = next(option for option in select.find_elements(By.TAG_NAME, 'option') if option.is_selected()).text
            except StopIteration:
                # WebDriver defaults to the first option if the HTML does not specify which is selected (at least for Firefox), so this should only occur if there are no options.
                continue

    for textarea in form.find_elements(By.TAG_NAME, 'textarea'):
        textarea_name = textarea.get_attribute('name')
        if textarea.is_displayed():
            data[textarea_name] = textarea.text
        else:
            # Assume it is an ace_editor, which are tricky.
            data[textarea_name] = assert_one(form, error_reporter, (By.CLASS_NAME, 'ace_text-layer')).text
    driver.implicitly_wait(max_wait)

    return data

def assert_nav(driver, error_reporter, address, privileged=False):
    '''Factor out testing the top navigation.
    address (str): The web address that the driver is currently visiting. This is required to assert that links lead to the right places.
    privileged (bool): Indicates whether the test user who is viewing Cloudscheduler has privileges (and can therefore access more pages).
    '''
    from selenium.webdriver.common.by import By
    import re

    expected_nav_links = [('/cloud/status/', 'Status'), ('/cloud/list/', 'Clouds'), ('/alias/list/', 'Aliases'), ('/group/defaults/', 'Defaults'), ('/images/', 'Images'), ('/keypairs/', 'Keys'), ('/user/settings/', 'User Settings'), ('/settings/log-out', 'Log out')]
    if privileged:
        # Insert these tuples starting at position 6.
        expected_nav_links[6:6] = [('/user/list/', 'Users'), ('/group/list/', 'Groups'), ('/server/config/', 'Config')]
    top_nav = assert_one(driver, error_reporter, (By.CLASS_NAME, 'top-nav'))
    nav_links = []
    link_pattern = re.escape(address) + r'(/[^?]+)'
    for elem in top_nav.find_elements(By.TAG_NAME, 'a'):
        link_match = re.match(link_pattern, elem.get_attribute('href'))
        if link_match:
            nav_links.append((link_match[1], elem.text))
        else:
            error_reporter('Expected the link {} to match the pattern {}'.format(get_open_tag(elem), link_pattern))
    if nav_links != expected_nav_links:
        error_reporter('Expected the top nav to contain the links {}, but found the links {}.'.format(expected_nav_links, nav_links))

def load_web_settings(address_extension, privileged=False):
    '''Load global settings and create test objects.'''
    import subprocess
    from cloudscheduler.unit_tests.unit_test_common import load_settings

    gvar = load_settings(web=True)
    switch_user(gvar, address_extension, 1 if privileged else 0)
    return gvar

def switch_user(gvar, address_extension, profile_index):
    '''
    Switch to a different Firefox profile, and therefore a different user.
    profile_index (int): The index (starting from 0) of the profile in gvar['firefox_profiles'] to switch to.
    '''
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.support.wait import WebDriverWait
    import os.path

    old_driver = gvar.get('driver')
    if old_driver:
        old_driver.quit()

    # ~/cloudscheduler/unit_tests must exist because we have already loaded settings from the credentials file there.
    gvar['driver'] = webdriver.Firefox(webdriver.FirefoxProfile(gvar['firefox_profiles'][profile_index]), service_log_path=os.path.expanduser('~/cloudscheduler/unit_tests/geckodriver.log'))
    try:
        gvar['driver'].implicitly_wait(gvar['max_wait'])
        gvar['driver_wait'] = WebDriverWait(gvar['driver'], gvar['max_wait'])
        # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
        gvar['driver'].get(gvar['address'] + address_extension)
        # The Firefox profile will automatically fill in the server credentials, so we just accept the prompt.
        gvar['driver'].switch_to.alert.accept()
    except WebDriverException:
        gvar['driver'].quit()
        raise

def get_open_tag(element):
   '''Return the opening tag of an element (including all of the attributes defined in it).'''
   import re

   # Match '<', then (any chars besides '>') any number of times and (anything in quotes) any number of times, then '>'.
   return re.match(r'<([^>]+|(([\'"]).*?\3))+>', element.get_attribute('outerHTML'))[0]
