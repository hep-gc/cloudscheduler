from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec, wait
import unittest
import web_common as wc

EXPECTED_CLOUD_TABS = ['Settings', 'Metadata', 'Exclusions']
EXPECTED_CLOUD_TYPES = ['amazon', 'azure', 'google', 'local', 'opennebula', 'openstack']
EXPECTED_AMAZON_REGIONS = ['ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'cn-north-1', 'cn-northwest-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'sa-east-1', 'us-east-1', 'us-east-2', 'us-gov-east-1', 'us-gov-west-1', 'us-west-1', 'us-west-2']
EXPECTED_IMAGE_FILTER_INPUTS = ['Operating Systems', 'Architectures', 'Owner Alias', 'Like', 'Not Like', 'Owner IDs']

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
        cls.cloud_update_valid_combinations = [{
                'enabled': True,
                'user_domain_name': 'unit-test.ca',
                'project_domain_name': 'unit-test.ca',
                'vm_keep_alive': 3,
                'spot_price': 1.4,
                'cores_softmax': 15,
                'cores_ctl': 9,
                'ram_ctl': 2
            }
        ]

    def test_nav(self):
        wc.assert_nav(self.driver, self.fail, self.gvar['address'])
    
    def test_cloud_add(self):
        # Look for links with visible text '+' within elements with id 'add-cloud' which are themselves in elements of class 'menu'.
        link_xpath = '//*[@class="menu"]//*[@id="add-cloud"]//a[text()="+"]'
        # Look for forms with name 'cloud' within elements with id 'add-cloud' which are themselves in elements of class 'menu'.
        form_xpath = '//*[@class="menu"]//*[@id="add-cloud"]//form[@name="add_cloud"]'
        wc.submit_invalid_combinations(self.driver, self.fail, form_xpath, self.cloud_add_invalid_combinations, self.cloud_add_mandatory_parameters, self.max_wait, click_before_filling=link_xpath)
        wc.submit_valid_combinations(self.driver, self.fail, form_xpath, self.cloud_add_valid_combinations, self.cloud_add_mandatory_parameters, self.max_wait, expected_response='successfully added', click_before_filling=link_xpath)
        wc.assert_exactly_one(self.driver, self.fail, (By.XPATH, link_xpath)).click()
        # Assert that the new cloud appears in the list of clouds.
        wc.assert_exactly_one(self.driver, self.fail, (By.XPATH, '//*[@class="menu"]//*[@id="{}"]'.format(self.cloud_to_add)), missing_message='{} was missing from the list of clouds after it was created.'.format(self.cloud_to_add))
        self.assert_cloud_types(form_xpath)
    
    @unittest.skip
    def test_cloud_delete(self):
        cloud_listing = self.select_cloud_tab(self.cloud_to_delete)
        delete_link = wc.assert_exactly_one(cloud_listing, self.fail, (By.LINK_TEXT, '−'), missing_message='The link to delete {} is missing.'.format(self.cloud_to_delete))
        delete_link.click()
        delete_dialog = wc.assert_exactly_one(self.driver, self.fail, (By.ID, 'delete-{}'.format(self.cloud_to_delete)))
        # Cancel deletion.
        wc.assert_exactly_one(delete_dialog, self.fail, (By.LINK_TEXT, 'X'), missing_message='The button to close the delete confirmation dialog is missing for {}.'.format(self.cloud_to_delete)).click()
        # Assert that the cloud still exists.
        try:
            cloud_listing.get_attribute('id')
        # We turn this exception into a failure because there is a difference between a test error and a test failure.
        except StaleElementReferenceException:
            self.fail('{} was removed from the list of clouds even though the deletion was cancelled.'.format(self.cloud_to_delete))
        delete_link.click()
        # Confirm deletion.
        wc.assert_exactly_one(delete_dialog, self.fail, (By.TAG_NAME, 'form'), {'name': self.cloud_to_delete}, missing_message='The form to confirm deletion is missing from the delete confirmation dialog for {}.'.format(self.cloud_to_delete)).submit()
        # Wait for the deletion to occur.
        menu = wc.assert_exactly_one(self.driver, self.fail, (By.CLASS_NAME, 'menu'))
        # Assert that the cloud has been removed from the cloud list.
        self.assertRaises(NoSuchElementException, menu.find_element, By.ID, self.cloud_to_delete)

    def test_cloud_update(self):
        settings_tab = self.select_cloud_tab(self.cloud_to_update, 0)
        # Look for forms with name equal to cloud_to_update within elements with id equal to cloud_to_update which are themselves in elements of class 'menu'.
        form_xpath = '//*[@class="menu"]//*[@id="{0}"]//form[@name="{0}"]'.format(self.cloud_to_update)
        wc.submit_invalid_combinations(self.driver, self.fail, form_xpath, self.cloud_update_invalid_combinations, max_wait=self.max_wait)
        wc.submit_valid_combinations(self.driver, self.fail, form_xpath, self.cloud_update_valid_combinations, max_wait=self.max_wait, expected_response='successfully updated', retains_values=True)
        form, cloud_type_options = self.assert_cloud_types(form_xpath)
        # Amazon.
        cloud_type_options[0].click()
        wc.assert_exactly_one(form, self.fail, (By.PARTIAL_LINK_TEXT, 'Image filter')).click()
        popup = wc.assert_exactly_one(self.driver, self.fail, (By.CLASS_NAME, 'popup'))
        close_button = wc.assert_exactly_one(popup, self.fail, (By.LINK_TEXT, 'x'))
        wc.assert_exactly_one(form, self.fail, (By.TAG_NAME, 'input'), {'type': 'submit', 'value': 'Update filter'})
        for input_label in EXPECTED_IMAGE_FILTER_INPUTS:
            pass
        footer = wc.assert_exactly_one(form, self.fail, (By.CLASS_NAME, 'footer'))
        self.assertIn('ec2 images, specified cloud "{}::{}" is not an "amazon" cloud.'.format(self.active_group, self.cloud_to_update), footer.text)
        close_button.click()
        self.assertTrue(ec.invisibility_of_element(popup))

    def test_exclusions_tab(self):
        exclusions_tab = self.select_cloud_tab(self.cloud_to_list, 2)
        # Look within elements of class 'tab' for an element of class 'tab2' that has within it a label with the text 'Default metadata'.
        default_metadata = wc.assert_exactly_one(exclusions_tab, self.fail, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="Default metadata"]'), missing_message='The \'Default metadata\' sub-tab (under \'Exclusions\') for {} is missing.'.format(self.cloud_to_list))
        default_metadata.click()
        wc.assert_exactly_one(exclusions_tab, self.fail, (By.TAG_NAME, 'form'), {'name': '{}-metadata-exclusions'.format(self.cloud_to_list)}, missing_message='The form to update metadata exclusions for {} is missing'.format(self.cloud_to_list))
        # Look within elements of class 'tab' for an element of class 'tab2' that has within it a label with the text 'Default flavors'.
        default_flavors = wc.assert_exactly_one(exclusions_tab, self.fail, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="Default flavors"]'), missing_message='The \'Default flavors\' sub-tab (under \'Exclusions\') for {} is missing.'.format(self.cloud_to_list))
        default_flavors.click()
        wc.assert_exactly_one(exclusions_tab, self.fail, (By.TAG_NAME, 'form'), {'name': '{}-flavor-exclusions'.format(self.cloud_to_list)}, missing_message='The form to update flavor exclusions for {} is missing.'.format(self.cloud_to_list))

    @unittest.skip
    def test_metadata_fetch(self):
        raise NotImplementedError()
        form = select_metadata(self.metadata_to_list)
        try:
            metadata_content = wc.assert_exactly_one(form, self.fail, (By.TAG_NAME, 'h2'), {'id': 'metadata-name'})
            self.assertEqual(metadata_content, EXPECTED_METADATA_CONTENT)
        finally:
            self.driver.switch_to.default_content()

    @unittest.skip
    def test_metadata_add(self):
        raise NotImplementedError()

    @unittest.skip
    def test_metadata_delete(self):
        delete_link = wc.assert_exactly_one(metadata_form, self.driver, self.fail, (By.TAG_NAME, 'a'), {'href': '{}/cloud/metadata-fetch/?{}&cloud_name={}&metadata_name={}#delete-metadata'.format(self.gvar['address'], self.active_group, self.cloud_to_list, self.metadata_to_list)}, missing_message='The button to delete {} is missing.'.format(self.metadata_to_list))
        raise NotImplementedError()

    @unittest.skip
    def test_metadata_update(self):
        wc.assert_exactly_one(metadata_form, self.driver, self.fail, (By.TAG_NAME, 'input'), {'type': 'submit', 'value': 'Update'}, missing_message='The \'Update\' button is missing from the form to update {}'.format(self.metadata_to_list))
        raise NotImplementedError()

    def select_cloud_tab(self, cloud_name, tab_index=None):
        '''Select the tab at the given tab_index under the given cloud and return the tab element.'''
        cloud_listing = wc.assert_exactly_one(self.driver, self.fail, (By.XPATH, '//*[@class="menu"]//*[@id="{}"]'.format(cloud_name)), missing_message='{} is missing from the list of clouds, or the whole list is missing.'.format(cloud_name))
        wc.assert_exactly_one(cloud_listing, self.fail, (By.LINK_TEXT, cloud_name), missing_message='The link to select {} is missing.'.format(cloud_name)).click()
        if tab_index == None:
            return cloud_listing
        else:
            tabs = cloud_listing.find_elements(By.CLASS_NAME, 'tab')
            try:
                tab = tabs[tab_index]
            except IndexError:
                self.fail('Expected tab at index {} (0-indexed) of {} to be \'{}\', but found only {} tabs.'.format(tab_index, cloud_name, EXPECTED_CLOUD_TABS[tab_index], len(tabs)))
            # Assert that the tab has a label in it with the correct text.
            tab_label = wc.assert_exactly_one(tab, self.fail, (By.XPATH, './/label[text()="{}"]'.format(EXPECTED_CLOUD_TABS[tab_index])), missing_message='Expected tab at index {} (0-indexed) of {} to be \'{}\', but it was not.'.format(tab_index, cloud_name, EXPECTED_CLOUD_TABS[tab_index]))
            tab_label.click()
            return tab

    def select_metadata(self, metadata_name):
        '''
        Select the specified metadata from the cloud_to_update and return the form within the iframe.
        Leave the driver looking inside the iframe so that the form can be manipulated, but the caller must switch the driver back to default_content.
        '''
        metadata_tab = self.select_cloud_tab(self.cloud_to_update, 1)
        # Look within metadata_tab for elements of class 'tab2' (i.e. sub-tabs) which have within them labels with text equal to metadata_name.
        metadata_listing = wc.assert_exactly_one(metadata_tab, self.fail, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="{}"]'.format(metadata_name)), missing_message='\'{}\' is missing from the list of metadata for {}'.format(metadata_name, self.cloud_to_update))
        # We already know this label exists, but we need to find it so we can click on it.
        wc.assert_exactly_one(metadata_tab, self.fail, (By.XPATH, './/label[text()="{}"]'.format(metadata_name))).click()
        try:
            iframe = wc.assert_exactly_one(metadata_listing, self.fail, (By.XPATH, './/iframe[@id="editor-{}-{}"]'.format(self.cloud_to_update, metadata_name)))
            self.driver.switch_to.frame(iframe)
            form = wc.assert_exactly_one(self.driver, self.fail, (By.NAME, 'metadata-form'))
        except AssertionError:
            self.driver.switch_to.default_content()
            raise
        return form

    def assert_cloud_types(self, form_xpath):
        '''Assert that the <select> with name='cloud_type' in form has the right <option>s and changes other <input>s appropriately.'''
        form = wc.assert_exactly_one(self.driver, self.fail, (By.XPATH, form_xpath))
        cloud_type_select = wc.assert_exactly_one(form, self.fail, (By.TAG_NAME, 'select'), {'name': 'cloud_type'})
        cloud_type_options = cloud_type_select.find_elements(By.TAG_NAME, 'option')
        cloud_types = [option.text for option in cloud_type_options]
        self.assertEqual(cloud_types, EXPECTED_CLOUD_TYPES)
        # Amazon.
        cloud_type_options[0].click()
        wc.assert_exactly_one(form, self.fail, (By.TAG_NAME, 'input'), {'name': 'authurl', 'value': 'ec2.ap-east-1.amazonaws.com', 'readonly': 'true'})
        amazon_region_select = wc.assert_exactly_one(form, self.fail, (By.TAG_NAME, 'select'), {'name': 'region'})
        amazon_regions = [option.text for option in amazon_region_select.find_elements(By.TAG_NAME, 'option')]
        self.assertEqual(amazon_regions, EXPECTED_AMAZON_REGIONS)
        wc.assert_exactly_one(form, self.fail, (By.TAG_NAME, 'input'), {'name': 'project', 'value': 'N/A', 'readonly': 'true'})
        # Azure (as an example of one that is not Amazon).
        cloud_type_options[1].click()
        for name in ['authurl', 'region', 'project']:
            wc.assert_exactly_one(form, self.fail, (By.TAG_NAME, 'input'), {'name': name, 'value': '', 'readonly': None})
        return form, cloud_type_options

    @classmethod
    def tearDownClass(cls):
        cls.gvar['driver'].quit()

if __name__ == '__main__':
    unittest.main()
