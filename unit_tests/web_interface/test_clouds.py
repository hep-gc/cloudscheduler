from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec, wait
import unittest
import web_common as wc

EXPECTED_CLOUD_TABS = ['Settings', 'Metadata', 'Exclusions']

class TestClouds(unittest.TestCase):
    def setUpClass(cls):
        cls.gvar = wc.setup('/cloud/status/')
        cls.driver = cls.gvar['driver']
        cls.wait = cls.gvar['wait']
        cls.active_group = '{}-wig1'.format(cls.gvar['user'])
        cls.cloud_to_list = '{}-wic1'.format(cls.gvar['user'])
        cls.cloud_to_delete = '{}-wic2'.format(cls.gvar['user'])
        cls.cloud_to_update = '{}-wic3'.format(cls.gvar['user'])
        cls.cloud_to_add = '{}-wic4'.format(cls.gvar['user'])
        cls.metadata_to_list = '{}-wicm1'.format(cls.gvar['user'])
        cls.metadata_to_delete = '{}-wicm2'.format(cls.gvar['user'])
        cls.metadata_to_update = '{}-wicm3'.format(cls.gvar['user'])
        cls.metadata_to_add = '{}-wicm4'.format(cls.gvar['user'])
        cls.cloud_add_parameters = {
            'cloud_name': ({
                '': 'cloud add value specified for "cloud_name" must not be the empty string.',
                'Invalid-Unit-Test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'invalid-unit--test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                '-invalid-unit-test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'invalid-unit-test!': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
                'cloud-name-that-is-too-long-for-the-database': 'Data too long for column \'cloud_name\' at row 1',
                cls.cloud_to_list: 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(cls.active_group, cls.cloud_to_list)
            }, 'invalid-unit-test'),
            'priority': ({
                '': 'cloud add value specified for "priority" must be an integer value.',
                'invalid-unit-test': 'cloud add value specified for "priority" must be an integer value.',
                '3.1': 'cloud add value specified for "priority" must be an integer value.'
            }, 0),
            'cloud_type': ({}, 'openstack'),
            'authurl': ({'': 'cloud add parameter "authurl" contains an empty string which is specifically disallowed.'}, cls.gvar['cloud_credentials']['authurl']),
            'username': ({'': 'cloud add parameter "username" contains an empty string which is specifically disallowed.'}, cls.gvar['cloud_credentials']['username']),
            'password': ({'': 'cloud add parameter "password" contains an empty string which is specifically disallowed.'}, cls.gvar['cloud_credentials']['password']),
            'project': ({'': 'cloud add parameter "project" contains an empty string which is specifically disallowed.'}, cls.gvar['cloud_credentials']['project']),
            'region': ({'': 'cloud add parameter "region" contains an empty string which is specifically disallowed.'}, cls.gvar['cloud_credentials']['region'])
        }
        cls.cloud_add_valid = {'cloud_name': cls.cloud_to_add, 'cloud_type': 'openstack', **cls.gvar['cloud_credentials'], 'enabled': True}
        cls.cloud_update_parameters = {
            'authurl': ({'': 'parameter "authurl" contains an empty string which is specifically disallowed.'},),
            'username': ({'': 'parameter "username" contains an empty string which is specifically disallowed.'},),
            'project': ({'': 'parameter "project" contains an empty string which is specifically disallowed.'},),
            'region': ({'': 'parameter "region" contains an empty string which is specifically disallowed.'},),
            'cloud_type': ({}, 'local'),
            'priority': ({
                '': 'cloud add value specified for "priority" must be an integer value.',
                'invalid-unit-test': 'cloud add value specified for "priority" must be an integer value.',
                '3.1': 'cloud add value specified for "priority" must be an integer value.'
            },),
            'vm_keep_alive': ({'invalid-unit-test': 'value specified for "vm_keep_alive" must be an integer value.'},),
            'spot_price': ({'invalid-unit-test': 'cloud update value specified for "spot_price" must be a floating point value.'},)
            # ram_ctl and cores_ctl are <input>s with type='number', meaning the browser prevents the submission of the form unless they are integers.
            # AFAIK it is impossible to test the details of the browser's response, because it shows a message that is not part of the DOM.
        }
        cls.cloud_update_valid = {
            'enabled': False,
            'user_domain_name': 'unit-test.ca',
            'project_domain_name': 'unit-test.ca',
            'vm_keep_alive': 3,
            'spot_price': 1.4,
            'cores_softmax': 1,
            'cores_ctl': 5,
            'ram_ctl': 9
        }

    def test_nav(self):
        wc.test_nav(self.driver, self.wait, self.fail)
    
    @unittest.skip
    def test_menu(self):
        cloud_listing = self.select_cloud(self.cloud_to_list)
        # self.select_cloud() already asserted the existence and singularity of menu, but we need to reference it later.
        menu = self.driver.find_element_by_class_name('menu')
        # The link text below is not a hyphen but a minus sign (U+2212).
        wc.assert_exactly_one(cloud_listing, self.wait, self.fail, (By.LINK_TEXT, '−'), missing_message='The link to delete {} is missing.'.format(self.cloud_to_list))
        # Look for descendants of cloud_listing that are of class 'tab', then within those look for labels. Create a list of the innerHTMLs of all such labels.
        cloud_tab_elems = wait.WebDriverWait(cloud_listing, gvar['max_wait']).until(ec.presence_of_all_elements_located((By.XPATH, './/*[@class="tab"]/label'.format(self.cloud_to_list))))
        cloud_tabs = [label.get_attribute('innerHTML') for label in cloud_tab_elems]
        self.assertEqual(cloud_tabs, EXPECTED_CLOUD_TABS)
        wc.assert_exactly_one(menu, self.wait, self.fail, (By.ID, 'add-cloud'), missing_message='The link to add a cloud is missing.')

    def test_cloud_add(self):
        menu = wc.assert_exactly_one(self.driver, self.wait, self.fail, (By.CLASS_NAME, 'menu'))
        add_listing = wc.assert_exactly_one(menu, self.wait, self.fail, (By.ID, 'add-cloud'), missing_message='The link to add a cloud is missing.')
        add_link_xpath = '//*[@class="menu"]//*[@id="add-cloud"]//a[text()="+"]'
        add_form_xpath = '//*[@class="menu"]//*[@id="add-cloud"]//form[@name="add_cloud"]'
        wc.parameters_submissions(self.driver, self.wait, self.fail, add_form_xpath, self.cloud_add_parameters, clicked_before_submitting=add_link_xpath)
        wc.assert_exactly_one(self.driver, self.wait, self.fail, (By.XPATH, add_link_xpath)).click()
        wc.submit_form(self.driver, self.wait, self.fail, add_form_xpath, self.cloud_add_valid, expected_response='cloud "{}::{}" successfully added'.format(self.active_group, self.cloud_to_add))
    
    @unittest.skip
    def test_cloud_delete(self):
        cloud_listing = self.select_cloud(self.cloud_to_delete)
        delete_link = wc.assert_exactly_one(cloud_listing, self.wait, self.fail, (By.LINK_TEXT, '−'), missing_message='The link to delete {} is missing.'.format(self.cloud_to_delete))
        delete_link.click()
        delete_dialog = wc.assert_exactly_one(self.driver, self.wait, self.fail, (By.ID, 'delete-{}'.format(self.cloud_to_delete)))
        # Cancel the deletion.
        wc.assert_exactly_one(delete_dialog, self.wait, self.fail, (By.LINK_TEXT, 'X'), missing_message='The button to close the delete confirmation dialog is missing for {}.'.format(self.cloud_to_delete)).click()
        # Assert that the cloud still exists.
        try:
            cloud_listing.get_attribute('id')
        # We turn this exception into a failure because there is a difference between a test error and a test failure.
        except StaleElementReferenceException:
            self.fail('{} was removed from the list of clouds even though the deletion was cancelled.'.format(self.cloud_to_delete))
        delete_link.click()
        # Confirm deletion.
        wc.assert_exactly_one(delete_dialog, self.wait, self.fail, (By.TAG_NAME, 'input'), {'type': 'submit'}, missing_message='The button to confirm deletion is missing from the delete confirmation dialog for {}.'.format(self.cloud_to_delete)).click()
        # Wait for the deletion to occur.
        self.wait.until(ec.invisibility_of_element(delete_dialog))
        # Assert that the cloud has been removed.
        self.assertRaises(StaleElementReferenceException, cloud_listing.get_attribute, 'id')

    def test_cloud_update(self):
        cloud_listing = self.select_cloud(self.cloud_to_update)
        # self.test_menu() asserts for us the presence and order of the tabs, so we assume it here.
        settings_tab = wait.WebDriverWait(cloud_listing, gvar['max_wait'].until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'tab')))[0]
        settings_tab.click()
        update_form_xpath = '//*[@class="menu"]//*[@id="{0}"]//form[@name="{0}"]'.format(self.cloud_to_update)
        wc.parameters_submissions(self.driver, self.wait, self.fail, update_form_xpath, self.cloud_update_parameters)
        wc.submit_form(self.driver, self.wait, self.fail, update_form_xpath, self.cloud_update_valid, expected_response='cloud "{}::{}" successfully updated'.format(self.active_group, self.cloud_to_update), retains_values=True)

    @unittest.skip
    def test_metadata_tab(self):
        cloud_listing = self.select_cloud(self.cloud_to_list)
        settings_tab = wait.WebDriverWait(cloud_listing, gvar['max_wait'].until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'tab')))[1]
        metadata_tab.click()
        # Look within metadata_tab for elements of class 'tab2' (i.e. sub-tabs). Within each of these, look for labels that have text identical to self.metadata_to_list.
        metadata_listing = wc.assert_exactly_one(metadata_tab, self.wait, self.fail, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="{}"]'.format(self.metadata_to_list)), missing_message='{} is missing from the list of metadata for {}'.format(self.metadata_to_list, self.cloud_to_list))
        # We already know this label exists, but we need to find it so we can click on it.
        wc.assert_exactly_one(metadata_listing, self.wait, self.fail, (By.TAG_NAME, 'label'), {'innerHTML': self.metadata_to_list}).click()
        try:
            iframe = wait.WebDriverWait(metadata_listing, self.gvar['max_wait']).until(ec.presence_of_element_located((By.XPATH, './/iframe[@id="editor-{}-{}"]'.format(self.cloud_to_list, self.metadata_to_list))))
            self.driver.switch_to.frame(iframe)
            # self.driver now looks in the iframe for elements, so self.wait does as well.
            fetch_form = wc.assert_exactly_one(self.driver, self.wait, self.fail, (By.NAME, 'metadata-form'))
            wc.assert_exactly_one(fetch_form, self.wait, self.fail, (By.TAG_NAME, 'input'), {'type': 'submit', 'value': 'Update'}, missing_message='The \'Update\' button is missing from the form to update {}'.format(self.metadata_to_list))
            delete_link = wc.assert_exactly_one(fetch_form, self.wait, self.fail, (By.TAG_NAME, 'a'), {'href': '{}/cloud/metadata-fetch/?{}&cloud_name={}&metadata_name={}#delete-metadata'.format(self.gvar['address'], self.active_group, self.cloud_to_list, self.metadata_to_list)}, missing_message='The button to delete {} is missing.'.format(self.metadata_to_list))
        except TimeoutException:
            self.fail('Either the iframe to update {} or the form within it is missing.'.format(self.metadata_to_list))
        # Switch back out of the iframe so that other tests don't fail if this one does.
        finally:
            self.driver.switch_to.default_content()

    def test_exclusions_tab(self):
        cloud_listing = self.select_cloud(self.cloud_to_list)
        exclusions_tab = cloud_listing.find_elements_by_class_name('tab')[2]
        exclusions_tab.click()
        default_metadata = wc.assert_exactly_one(exclusions_tab, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="Default metadata"]'), None, self.fail, missing_message='The \'Default metadata\' tab for {} is missing.'.format(self.cloud_to_list))
        default_metadata.click()
        wc.assert_exactly_one(default_metadata, (By.TAG_NAME, 'form'), {'name': '{}-metadata-exclusions'.format(self.cloud_to_list)}, self.fail, missing_message='The form to update metadata exclusions for {} is missing'.format(self.cloud_to_list))
        default_flavors = wc.assert_exactly_one(exclusions_tab, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="Default flavors"]'), None, self.fail, missing_message='The \'Default flavors\' tab for {} is missing.'.format(self.cloud_to_list))
        default_flavors.click()
        wc.assert_exactly_one(default_flavors, (By.TAG_NAME, 'form'), {'name': '{}-flavor-exclusions'.format(self.cloud_to_list)}, self.fail, missing_message='The form to update flavor exclusions for {} is missing.'.format(self.cloud_to_list))

    def select_cloud(self, cloud_name):
        '''Select the given cloud and return its listing.'''
        menu = wc.assert_exactly_one(self.driver, (By.CLASS_NAME, 'menu'), None, self.fail)
        cloud_listing = wc.assert_exactly_one(menu, (By.ID, cloud_name), None, self.fail, missing_message='{} is missing from the list of clouds.'.format(cloud_name))
        wc.assert_exactly_one(cloud_listing, (By.LINK_TEXT, cloud_name), None, self.fail, missing_message='The link to select {} is missing.'.format(cloud_name)).click()
        return cloud_listing
    
    def select_metadata(self, metadata_name):
        '''Select the given metadata from the cloud_to_update and return the form within the iframe.'''
        cloud_listing = self.select_cloud(self.cloud_to_update)
        metadata_tab = cloud_listing.find_elements_by_class_name('tab')[1]
        metadata_tab.click()
        # Look within metadata_tab for elements of class 'tab2' (i.e. sub-tabs). Within each of these, look for labels that have text identical to self.metadata_to_list.
        metadata_listing = wc.assert_exactly_one(metadata_tab, (By.XPATH, './/*[contains(@class, "tab2")][label/text()="{}"]'.format(self.metadata_to_list)), None, self.fail, missing_message='{} is missing from the list of metadata for {}'.format(self.metadata_to_list, self.cloud_to_list))
        # We already know this label exists, but we need to find it so we can click on it.
        wc.assert_exactly_one(metadata_listing, (By.TAG_NAME, 'label'), {'innerHTML': self.metadata_to_list}, self.fail).click()
        try:
            iframe = wait.WebDriverWait(metadata_listing, self.gvar['max_wait']).until(ec.presence_of_element_located((By.XPATH, './/iframe[@id="editor-{}-{}"]'.format(self.cloud_to_list, self.metadata_to_list))))
            self.driver.switch_to.frame(iframe)
            fetch_form = self.wait.until(ec.presence_of_element_located((By.NAME, 'metadata-form')))
            wc.assert_exactly_one(fetch_form, (By.TAG_NAME, 'input'), {'type': 'submit', 'value': 'Update'}, self.fail, missing_message='The \'Update\' button is missing from the form to update {}'.format(self.metadata_to_list))
            delete_link = wc.assert_exactly_one(fetch_form, (By.TAG_NAME, 'a'), {'href': '{}/cloud/metadata-fetch/?{}&cloud_name={}&metadata_name={}#delete-metadata'.format(self.gvar['address'], self.active_group, self.cloud_to_list, self.metadata_to_list)}, self.fail, missing_message='The button to delete {} is missing.'.format(self.metadata_to_list))
        except TimeoutException:
            self.fail('Either the iframe to update {} or the form within it is missing.'.format(self.metadata_to_list))
        # Switch back out of the iframe so that other tests don't fail if this one does.
        finally:
            self.driver.switch_to.default_content()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
