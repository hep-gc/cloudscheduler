from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec, wait
import unittest
import web_common as wc

EXPECTED_CLOUD_TABS = ['Settings', 'Metadata', 'Exclusions']
EXPECTED_CLOUD_TYPES = {'amazon', 'azure', 'google', 'local', 'opennebula', 'openstack'}
EXPECTED_AMAZON_REGIONS = {'ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'cn-north-1', 'cn-northwest-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'sa-east-1', 'us-east-1', 'us-east-2', 'us-gov-east-1', 'us-gov-west-1', 'us-west-1', 'us-west-2'}
# When Amazon is the cloud type and the 'Image filter' link is clicked, a popup is expected with a form containing these (input_label, input_name) pairs.
EXPECTED_IMAGE_FILTER_INPUTS = {('Operating Systems', 'operating_systems'), ('Architectures', 'architectures'), ('Owner Alias', 'owner_aliases'), ('Like', 'like'), ('Not Like', 'not_like'), ('Owner IDs', 'owner_ids')}
EXPECTED_FLAVOR_FILTER_INPUTS = {('Processor Families', 'families'), ('Operating Systems', 'operating_systems'), ('Processors', 'processors'), ('Manufacturers', 'processor_manufacturers'), ('Cores', 'cores'), ('Min RAM (GB)', 'memory_min_gigabytes_per_core'), ('Max RAM (GB)', 'memory_max_gigabytes_per_core')}
# The form to add new metadata is expected to contain <label>s, <input>s, and <select>s in a table row that match the following (label_text, input_type, input_name) triples. input_type == 'select' indicates a <select> tag.
EXPECTED_METADATA_ADD_ENTRIES = [('Metadata Name:', 'text', 'metadata_name'), ('Enabled:', 'checkbox', 'enabled'), ('Priority:', 'number', 'priority'), ('MIME Type:', 'select', 'mime_type')]
EXPECTED_METADATA_MIME_TYPE_OPTIONS = ['cloud-config', 'ucernvm-config']

class TestClouds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.setup('/cloud/list/')
        cls.driver = cls.gvar['driver']
        cls.max_wait = cls.gvar['max_wait']
        cls.active_group = '{}-wig1'.format(cls.gvar['user'])
        cls.cloud_to_list = '{}-wic1'.format(cls.gvar['user'])
        cls.cloud_to_delete = '{}-wic2'.format(cls.gvar['user'])
        cls.cloud_to_update = '{}-wic3'.format(cls.gvar['user'])
        cls.cloud_to_add = '{}-wic4'.format(cls.gvar['user'])
        cls.metadata_to_list = '{}-wicm1'.format(cls.gvar['user'])
        cls.metadata_to_delete = '{}-wicm2'.format(cls.gvar['user'])
        cls.metadata_to_update = '{}-wicm3'.format(cls.gvar['user'])
        cls.metadata_to_add = '{}-wicm4'.format(cls.gvar['user'])
        # It is important that cloud_type comes before cloud_credentials, because it can change these fields.
        cls.cloud_add_mandatory_parameters = {'cloud_name': cls.cloud_to_add, 'cloud_type': 'openstack', **cls.gvar['cloud_credentials']}
        cls.cloud_add_invalid_combinations = {
            'cloud_name': {
                '': 'cloud add value specified for "cloud_name" must not be the empty string.',
                'Invalid-Unit-Test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'invalid-unit--test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                '-invalid-unit-test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'invalid-unit-test!': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'cloud-name-that-is-too-long-for-the-database': 'Data too long for column \'cloud_name\' at row 1',
                cls.cloud_to_list: 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(cls.active_group, cls.cloud_to_list)
            },
            'authurl': {'': 'cloud add parameter "authurl" contains an empty string which is specifically disallowed.'},
            'username': {'': 'cloud add parameter "username" contains an empty string which is specifically disallowed.'},
            'password': {'': 'cloud add parameter "password" contains an empty string which is specifically disallowed.'},
            'project': {'': 'cloud add parameter "project" contains an empty string which is specifically disallowed.'},
            'region': {'': 'cloud add parameter "region" contains an empty string which is specifically disallowed.'},
            'priority': {
                '': 'cloud add value specified for "priority" must be an integer value.',
                'invalid-unit-test': 'cloud add value specified for "priority" must be an integer value.',
                '3.1': 'cloud add value specified for "priority" must be an integer value.'
            }
        }
        cls.cloud_add_valid_combinations = [{'enabled': True}]
        cls.cloud_update_invalid_combinations = {
            'authurl': {'': 'cloud update parameter "authurl" contains an empty string which is specifically disallowed.'},
            'username': {'': 'cloud update parameter "username" contains an empty string which is specifically disallowed.'},
            'project': {'': 'cloud update parameter "project" contains an empty string which is specifically disallowed.'},
            'region': {'': 'cloud update parameter "region" contains an empty string which is specifically disallowed.'},
            'priority': {
                '': 'cloud update value specified for "priority" must be an integer value.',
                'invalid-unit-test': 'cloud update value specified for "priority" must be an integer value.',
                '3.1': 'cloud update value specified for "priority" must be an integer value.'
            },
            'vm_keep_alive': {
                '': 'value specified for "vm_keep_alive" must be an integer value.',
                'invalid-unit-test': 'value specified for "vm_keep_alive" must be an integer value.',
                '3.1': 'value specified for "vm_keep_alive" must be an integer value.'
            },
            'spot_price': {
                '': 'value specified for "spot_price" must be a floating point value.',
                'invalid-unit-test': 'value specified for "spot_price" must be a floating point value.'
            },
            # ram_ctl and cores_ctl are <input>s with type='number', meaning the browser prevents the submission of the form unless they are integers.
            # AFAIK it is impossible to test the details of the browser's response (using Selenium), because it shows a message that is not part of the DOM.
        }

    def test_nav(self):
        wc.assert_nav(self.driver, self.fail, self.gvar['address'])
    
    @unittest.skip
    def test_cloud_add(self):
        # Look for links with visible text '+' within elements with id 'add-cloud' which are themselves in elements of class 'menu'.
        link_xpath = '//*[@class="menu"]//*[@id="add-cloud"]//a[text()="+"]'
        # Look for forms with name 'cloud' within elements with id 'add-cloud' which are themselves in elements of class 'menu'.
        form_xpath = '//*[@class="menu"]//*[@id="add-cloud"]//form[@name="add_cloud"]'
        wc.submit_invalid_combinations(self.driver, self.fail, form_xpath, self.cloud_add_invalid_combinations, self.cloud_add_mandatory_parameters, self.max_wait, click_before_filling=link_xpath)
        wc.submit_valid_combinations(self.driver, self.fail, form_xpath, self.cloud_add_valid_combinations, self.cloud_add_mandatory_parameters, self.max_wait, expected_response='successfully added', click_before_filling=link_xpath)
        wc.assert_one(self.driver, self.fail, (By.XPATH, link_xpath)).click()
        # Assert that the new cloud appears in the list of clouds.
        wc.assert_one(self.driver, self.fail, (By.XPATH, '//*[@class="menu"]//*[@id="{}"]'.format(self.cloud_to_add)), missing_message='{} was missing from the list of clouds after it was created.'.format(self.cloud_to_add))
        self.assert_cloud_types(form_xpath)
    
    @unittest.skip
    def test_cloud_delete(self):
        cloud_listing = self.select_cloud_tab(self.cloud_to_delete)
        delete_link = wc.assert_one(cloud_listing, self.fail, (By.LINK_TEXT, '−'), missing_message='The link to delete {} is missing.'.format(self.cloud_to_delete))
        delete_link.click()
        delete_dialog = wc.assert_one(self.driver, self.fail, (By.ID, 'delete-{}'.format(self.cloud_to_delete)))
        # Cancel deletion. The link text is an uppercase letter 'X'.
        wc.assert_one(delete_dialog, self.fail, (By.LINK_TEXT, 'X'), missing_message='The button to close the delete confirmation dialog is missing for {}.'.format(self.cloud_to_delete)).click()
        # Assert that the cloud still exists.
        try:
            cloud_listing.get_attribute('id')
        # We turn this exception into a failure because there is a difference between a test error and a test failure.
        except StaleElementReferenceException:
            self.fail('{} was removed from the list of clouds even though the deletion was cancelled.'.format(self.cloud_to_delete))
        delete_link.click()
        # Confirm deletion.
        wc.assert_one(delete_dialog, self.fail, (By.TAG_NAME, 'form'), {'name': self.cloud_to_delete}, missing_message='The form to confirm deletion is missing from the delete confirmation dialog for {}.'.format(self.cloud_to_delete)).submit()
        menu = wc.assert_one(self.driver, self.fail, (By.CLASS_NAME, 'menu'))
        # Assert that the cloud has been removed from the cloud list.
        self.assertRaises(NoSuchElementException, menu.find_element, By.ID, self.cloud_to_delete)

    @unittest.skip
    def test_cloud_update(self):
        self.select_cloud_tab(self.cloud_to_update, 0)
        # Look for forms with name equal to cloud_to_update within elements with id equal to cloud_to_update which are themselves in elements of class 'menu'.
        form_xpath = '//*[@class="menu"]//*[@id="{0}"]//form[@name="{0}"]'.format(self.cloud_to_update)
        wc.submit_invalid_combinations(self.driver, self.fail, form_xpath, self.cloud_update_invalid_combinations, max_wait=self.max_wait)
        wc.submit_valid_combinations(self.driver, self.fail, form_xpath, self.cloud_update_valid_combinations, max_wait=self.max_wait, expected_response='successfully updated', retains_values=True)
        self.assert_cloud_types(form_xpath)

    @unittest.skip
    def test_amazon_filters(self):
        self.assert_amazon_popup('Image filter', EXPECTED_IMAGE_FILTER_INPUTS)
        self.assert_amazon_popup('Flavor filter', EXPECTED_FLAVOR_FILTER_INPUTS)
    
    def test_exclusions_tab(self):
        exclusions_tab = self.select_cloud_tab(self.cloud_to_list, 2)
        # Look within elements of class 'tab' for an element of class 'tab2' that has within it a label with the text 'Default metadata'.
        default_metadata = wc.assert_one(exclusions_tab, self.fail, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="Default metadata"]'), missing_message='The \'Default metadata\' sub-tab (under \'Exclusions\') for {} is missing.'.format(self.cloud_to_list))
        default_metadata.click()
        wc.assert_one(exclusions_tab, self.fail, (By.TAG_NAME, 'form'), {'name': '{}-metadata-exclusions'.format(self.cloud_to_list)}, missing_message='The form to update metadata exclusions for {} is missing'.format(self.cloud_to_list))
        # Look within elements of class 'tab' for an element of class 'tab2' that has within it a label with the text 'Default flavors'.
        default_flavors = wc.assert_one(exclusions_tab, self.fail, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="Default flavors"]'), missing_message='The \'Default flavors\' sub-tab (under \'Exclusions\') for {} is missing.'.format(self.cloud_to_list))
        default_flavors.click()
        wc.assert_one(exclusions_tab, self.fail, (By.TAG_NAME, 'form'), {'name': '{}-flavor-exclusions'.format(self.cloud_to_list)}, missing_message='The form to update flavor exclusions for {} is missing.'.format(self.cloud_to_list))

    def test_metadata_fetch(self):
        with open(self.gvar['metadata_path']) as metadata_file:
            expected_metadata_content = metadata_file.read()
        form = self.select_metadata(self.metadata_to_list)
        try:
            wc.assert_one(form, self.fail, (By.TAG_NAME, 'h2'), {'id': 'metadata-name'})
            actual_metadata_content = wc.assert_one(form, self.fail, (By.TAG_NAME, 'textarea'), {'name': 'metadata'}).get_attribute('value')
            self.assertEqual(actual_metadata_content, expected_metadata_content)
        finally:
            self.driver.switch_to.default_content()

    def test_metadata_add(self):
        mandatory_parameters = {'metadata_name': self.metadata_to_add}
        invalid_metadata_name_values = {
            '': 'metadata add value specified for "metadata_name" must not be the empty string.',
            'Invalid-Unit-Test': 'metadata add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            'invalid-unit--test': 'metadata add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            '-invalid-unit-test': 'metadata add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            'invalid-unit-test!': 'metadata add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            'metadata-name-that-is-too-long-for-the-database': 'Data too long for column \'metadata_name\' at row 1',
            self.metadata_to_list: 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(self.active_group, self.metadata_to_list)
        }
        valid_combination = {
            'enabled': True,
            'priority': 3,
            'metadata': 'valid metadata content'
        }
        self.select_metadata()
        form_xpath = '//form[@name="metadata-form"]'
        try:
            # A modified version of submit_invalid_combinations, because we need to switch out of and back into the iframe after every invalid submission.
            for value, message in invalid_priority_values.items():
                # Mandatory parameters are listed first so that they are overwriten as necessary.
                wc.submit_form(self.driver, self.fail, form_xpath, {**mandatory_parameters, name: value}, max_wait=self.gvar['max_wait'], expected_response=message)
                self.driver.switch_to.default_content()
                self.select_metadata()
            # Submit a name that ends with '.yaml' but content that is invalid as YAML.
            invalid_yaml_parameters = {**mandatory_parameters, 'metadata_name': '{}.yaml'.format(self.metadata_to_add), 'metadata': 'foo: bar: this is invalid yaml'}
            wc.submit_form(self.driver, self.fail, form_xpath, invalid_yaml_parameters, self.gvar['max_wait'], expected_response='cloud metadata-add yaml value specified for "metadata (metadata_name)" is invalid - scanner error')
            self.driver.switch_to.default_content()
            self.select_metadata()
            # Submit valid parameters.
            wc.submit_form(self.driver, self.fail, form_xpath, {**mandatory_parameters, valid_combination}, self.gvar['max_wait'])
            self.driver.switch_to.default_content()
            # We cannot assert an expected_response through submit_form() because the driver is set to the iframe that that point (and the message appears outside it).
            footer = wc.assert_one(self.driver, self.fail, (By.ID, 'message'))
            self.assertIn('cloud metadata file "grobertson-wig1::grobertson-wic3::foo.yaml" successfully added.', footer.text)
            form = self.select_metadata()
            self.assert_metadata_mime_types(form)
        finally:
            self.driver.switch_to.default_content()

    def test_metadata_delete(self):
        form = self.select_metadata(self.metadata_to_delete)
        try:
            delete_button = wc.assert_one(form, self.fail, (By.TAG_NAME, 'a'), {'href': '{}/cloud/metadata-fetch/?{}&cloud_name={}&metadata_name={}#delete-metadata'.format(self.gvar['address'], self.active_group, self.cloud_to_update, self.metadata_to_delete)}, missing_message='The button to delete {} is missing.'.format(self.metadata_to_delete))
            delete_button.click()
            delete_dialog = wc.assert_one(self.driver, self.fail, (By.ID, 'delete-metadata'))
            # The link text below is an uppercase letter 'X'.
            wc.assert_one(delete_dialog, self.fail, (By.LINK_TEXT, 'X')).click()
            self.assertTrue(ec.invisibility_of_element(delete_dialog))
            delete_button.click()
            wc.assert_one(delete_dialog, self.fail, (By.NAME, '{}-{}-delete'.format(self.cloud_to_update, self.metadata_to_delete))).submit()
            wait.WebDriverWait(self.driver, self.gvar['max_wait']).until(ec.staleness_of(delete_button))
        finally:
            self.driver.switch_to.default_content()

    @unittest.skip
    def test_metadata_update(self):
        valid_combination = {
            'enabled': True,
            'user_domain_name': 'unit-test.ca',
            'project_domain_name': 'unit-test.ca',
            'vm_keep_alive': 3,
            'spot_price': 1.4,
            'cores_softmax': 15,
            'cores_ctl': 9,
            'ram_ctl': 2
        }
        form_xpath = '//form[@name="metadata-form"]'
        self.select_metadata('{}.yaml'.format(self.metadata_to_update))
        try:
            wc.submit_form(self.driver, self.fail, form_xpath, {'metadata': 'foo: bar: this is invalid yaml'}, self.gvar['max_wait'], expected_response='TODO')
            self.driver.switch_to.default_content()
            self.select_metadata(self.metadata_to_update)
            wc.submit_form(self.driver, self.fail, form_xpath, valid_combination, self.gvar['max_wait'], expected_message='cloud metadata file "{}::{}::{}" successfully updated.'.format(self.active_group, self.cloud_to_update, self.metadata_to_update), retains_values=True)
            self.driver.switch_to.default_content()
            form = self.select_metadata(self.metadata_to_update)
            self.assert_metadata_mime_types(form)
        finally:
            self.driver.switch_to.default_content()

    def select_cloud_tab(self, cloud_name, tab_index=None):
        '''Select the tab at the given tab_index under the given cloud and return the tab element.'''
        cloud_listing = wc.assert_one(self.driver, self.fail, (By.XPATH, '//*[@class="menu"]//*[@id="{}"]'.format(cloud_name)), missing_message='{} is missing from the list of clouds, or the whole list is missing.'.format(cloud_name))
        wc.assert_one(cloud_listing, self.fail, (By.LINK_TEXT, cloud_name), missing_message='The link to select {} is missing.'.format(cloud_name)).click()
        if tab_index == None:
            return cloud_listing
        else:
            tabs = cloud_listing.find_elements(By.CLASS_NAME, 'tab')
            try:
                tab = tabs[tab_index]
            except IndexError:
                self.fail('Expected tab at index {} (0-indexed) of {} to be \'{}\', but found only {} tabs.'.format(tab_index, cloud_name, EXPECTED_CLOUD_TABS[tab_index], len(tabs)))
            # Assert that the tab has a label in it with the correct text.
            tab_label = wc.assert_one(tab, self.fail, (By.XPATH, './/label[text()="{}"]'.format(EXPECTED_CLOUD_TABS[tab_index])), missing_message='Expected tab at index {} (0-indexed) of {} to be \'{}\', but it was not.'.format(tab_index, cloud_name, EXPECTED_CLOUD_TABS[tab_index]))
            tab_label.click()
            return tab

    def select_metadata(self, metadata_name=None):
        '''
        Select the specified metadata from the cloud_to_update and return the form within the iframe. If not metadata_name, select the option to add metadata.
        Leave the driver looking inside the iframe so that the form can be manipulated, but the caller must switch the driver back to default_content.
        '''
        metadata_tab = self.select_cloud_tab(self.cloud_to_update, 1)
        # Look within metadata_tab for elements of class 'tab2' (i.e. sub-tabs) which have within them labels with text equal to metadata_name.
        metadata_listing = wc.assert_one(metadata_tab, self.fail, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="{}"]'.format(metadata_name if metadata_name else '+')), missing_message='\'{}\' is missing from the list of metadata for {}'.format(metadata_name if metadata_name else '+', self.cloud_to_update))
        # We already know this label exists, but we need to find it so we can click on it.
        wc.assert_one(metadata_tab, self.fail, (By.XPATH, './/label[text()="{}"]'.format(metadata_name if metadata_name else '+'))).click()
        iframe = wc.assert_one(metadata_listing, self.fail, (By.XPATH, './/iframe[@id="editor-{}-{}"]'.format(self.cloud_to_update, metadata_name if metadata_name else 'add')))
        self.driver.switch_to.frame(iframe)
        try:
            return wc.assert_one(self.driver, self.fail, (By.TAG_NAME, 'form'), {'name': 'metadata-form'})
        except AssertionError:
            self.driver.switch_to.default_content()
            raise

    def assert_cloud_types(self, form_xpath):
        '''Assert that the <select> with name='cloud_type' in form has the right <option>s and changes other <input>s appropriately.'''
        form = wc.assert_one(self.driver, self.fail, (By.XPATH, form_xpath))
        cloud_type_select = wc.assert_one(form, self.fail, (By.TAG_NAME, 'select'), {'name': 'cloud_type'})
        cloud_type_options = cloud_type_select.find_elements(By.TAG_NAME, 'option')
        cloud_types = {option.text for option in cloud_type_options}
        self.assertEqual(cloud_types, EXPECTED_CLOUD_TYPES)
        # Amazon.
        cloud_type_options[0].click()
        wc.assert_one(form, self.fail, (By.TAG_NAME, 'input'), {'name': 'authurl', 'value': 'ec2.ap-east-1.amazonaws.com', 'readonly': 'true'})
        amazon_region_select = wc.assert_one(form, self.fail, (By.TAG_NAME, 'select'), {'name': 'region'})
        amazon_regions = {option.text for option in amazon_region_select.find_elements(By.TAG_NAME, 'option')}
        self.assertEqual(amazon_regions, EXPECTED_AMAZON_REGIONS)
        wc.assert_one(form, self.fail, (By.TAG_NAME, 'input'), {'name': 'project', 'value': 'N/A', 'readonly': 'true'})
        # Azure (as an example of one that is not Amazon).
        cloud_type_options[1].click()
        for name in ['authurl', 'region', 'project']:
            wc.assert_one(form, self.fail, (By.TAG_NAME, 'input'), {'name': name, 'value': '', 'readonly': None})

    def assert_amazon_popup(self, partial_link_text, expected_inputs):
        '''Select the Settings tab of the cloud_to_list, click on the link in the form that has partial_link_text, and switch to the form in the iframe in the popup that appears.'''
        settings_tab = self.select_cloud_tab(self.cloud_to_list, 0)
        form = wc.assert_one(settings_tab, self.fail, (By.TAG_NAME, 'form'), {'name': self.cloud_to_list})
        wc.assert_one(form, self.fail, (By.TAG_NAME, 'option'), {'value': 'amazon'}).click()
        wc.assert_one(form, self.fail, (By.PARTIAL_LINK_TEXT, partial_link_text)).click()
        popup = wc.assert_one(self.driver, self.fail, (By.CLASS_NAME, 'popup'))
        try:
            popup_iframe = wc.assert_one(popup, self.fail, (By.TAG_NAME, 'iframe'), {'id': 'vms-iframe'})
            self.assertIn('/ec2/', popup_iframe.get_attribute('src'))
            self.driver.switch_to.frame(popup_iframe)
            try:
                popup_form = wc.assert_one(self.driver, self.fail, (By.TAG_NAME, 'form'), {'name': 'ec2_filters'})
                input_containers = popup_form.find_elements(By.TAG_NAME, 'li')
                wc.assert_one(input_containers[0], self.fail, (By.TAG_NAME, 'input'), {'type': 'submit', 'value': 'Update filter'})
                actual_inputs = set()
                for input_container in input_containers[1:]:
                    label = wc.assert_one(input_container, self.fail, (By.TAG_NAME, 'a')).text
                    name = wc.assert_one(input_container, self.fail, (By.TAG_NAME, 'input')).get_attribute('name')
                    actual_inputs.add((label, name))
                self.assertEqual(actual_inputs, expected_inputs)
                footer = wc.assert_one(self.driver, self.fail, (By.CLASS_NAME, 'footer'))
                self.assertIn('specified cloud "{}::{}" is not an "amazon" cloud.'.format(self.active_group, self.cloud_to_list), footer.text)
            finally:
                self.driver.switch_to.default_content()
        finally:
            # The link text below is a multiplication sign (U+00D7), not the letter 'x'.
            wc.assert_one(popup, self.fail, (By.LINK_TEXT, '×')).click()
            # Wait for the page to start reloading.
            wait.WebDriverWait(self.driver, self.max_wait).until(ec.staleness_of(settings_tab))

    def assert_metadata_mime_types(self, form):
        mime_type_select = wc.assert_one(form, self.fail, (By.TAG_NAME, 'select'), {'name': 'mime_type'})
        mime_type_options = [option.text for option in mime_type_select.find_elements(By.TAG_NAME, 'option')]
        self.assertEqual(mime_type_options, EXPECTED_METADATA_MIME_TYPE_OPTIONS)

    @classmethod
    def tearDownClass(cls):
        cls.gvar['driver'].quit()

if __name__ == '__main__':
    unittest.main()
