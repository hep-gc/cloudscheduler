from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
import unittest
import web_common as wc

EXPECTED_CLOUD_TABS = ['Settings', 'Metadata', 'Exclusions']
CLOUD_TO_ADD = '{}-wic4'.format(self.gvar['user'])
CLOUD_TO_DELETE = '{}-wic2'.format(self.gvar['user'])
CLOUD_TO_UPDATE = '{}-wic3'.format(self.gvar['user'])

class TestClouds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.setup()
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.gvar['web']['firefox_profile']))
        try:
            cls.wait = ui.WebDriverWait(cls.driver, 120)
            cls.driver.get('{}/cloud/list/'.format(cls.gvar['address']))
            wait.until(expected_conditions.alert_is_present()).accept()
            # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
            cls.wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'menu')))
        except TimeoutException:
            cls.driver.quit()
            raise

    def test_nav(self):
        wc.test_nav(self)
    
    def test_menu(self):
        cloud_listing = self.select_cloud(CLOUD_TO_LIST)
        # self.select_cloud() already asserted the existence and singularity of menu, but we need to reference it later.
        menu = self.driver.find_element_by_class_name('menu')
        # The link text below is not a hyphen but a minus sign (U+2212).
        wc.assert_exactly_one(cloud_listing, By.LINK_TEXT, '−', self.fail, missing_message='Link to delete {} is missing.'.format(CLOUD_TO_LIST))
        cloud_tabs = [label.get_attribute('innerHTML') for label in self.driver.find_elements_by_xpath('//*[@class="menu"]/*[@id="{}"]//*[@class="tab"]/label'.format(CLOUD_TO_LIST))]
        self.assertEqual(cloud_tabs, EXPECTED_CLOUD_TABS)
        wc.assert_exactly_one(menu, By.ID, 'add-cloud', self.fail, missing_message='Link to add a cloud is missing.')

    def test_add(self):
        menu = wc.assert_exactly_one(self.driver, By.CLASS_NAME, 'menu', self.fail)
        add_listing = wc.assert_exactly_one(menu, By.ID, 'add-cloud', self.fail, missing_message='Link to add a cloud is missing.')
        wc.assert_exactly_one(add_listing, By.LINK_TEXT, '+', self.fail).click()
        add_forms = list(filter(lambda form: form.get_attribute('name') == 'add_cloud', add_listing.find_elements_by_tag_name('form')))
        self.assertEqual(len(add_forms), 1)
        new_cloud_settings = {'cloud_name': CLOUD_TO_ADD, 'cloud_type': 'openstack', **self.gvar['cloud_credentials'], 'enabled': True}
        wc.submit_form(add_forms[0], new_cloud_settings, self.fail)
    
    def test_delete(self):
        cloud_listing = self.select_cloud(CLOUD_TO_DELETE)
        delete_link = wc.assert_exactly_one(cloud_listing, By.LINK_TEXT, '−', self.fail, missing_message='Link to delete {} is missing.'.format(CLOUD_TO_DELETE)).click()
        delete_link.click()
        delete_dialog = wc.assert_exactly_one(cloud_listing, By.ID, 'delete-{}'.format(CLOUD_TO_DELETE), self.fail)
        # Cancel the deletion.
        wc.assert_exactly_one(delete_dialog, By.LINK_TEXT, 'X', self.fail, missing_message='The button to close the delete confirmation dialog is missing for {}.'.format(CLOUD_TO_DELETE)).click()
        # Assert that the cloud still exists.
        try:
            cloud_listing.get_attribute('id')
        except StaleElementReferenceException:
            self.fail('{} was removed from the list of clouds even though the deletion was cancelled.'.format(CLOUD_TO_DELETE))
        delete_link.click()
        # Confirm deletion.
        try:
            next(filter(lambda input_elem: input_elem.get_attribute('type') == 'submit', delete_dialog.find_elements_by_tag_name('input'))).click()
        except StopIteration:
            self.fail('The button to confirm deletion is missing from the delete confirmation dialog for {}.'.format(CLOUD_TO_DELETE))
        # Assert that the cloud has been removed.
        self.assertRaises(StaleElementReferenceException, cloud_listing.get_attribute, 'id')

    @unittest.skip
    def test_settings(self):
        cloud_listing = self.select_cloud(CLOUD_TO_LIST)
        # self.test_menu() asserts for us the presence and order of the tabs, so we assume it here.
        settings_tab = cloud_listing.find_elements_by_class_name('tab')[0]
        settings_tab.click()
        try:
            settings_form = next(filter(lambda form: form.get_attribute('name') == CLOUD_TO_LIST, settings_tab.find_elements_by_tag_name('form')))
        except StopIteration:
            self.fail('The settings form for {} is missing.'.format(CLOUD_TO_LIST))

    @unittest.skip
    def test_metadata(self):
        raise NotImplementedError()

    @unittest.skip
    def test_exclusions(self):
        raise NotImplementedError()

    def select_cloud(self, cloud_name):
        menu = wc.assert_exactly_one(self.driver, By.CLASS_NAME, 'menu', self.fail)
        cloud_listing = wc.assert_exactly_one(menu, By.ID, cloud_name, self.fail, missing_message='{}-wic2 is missing from the list of clouds.')
        wc.assert_exactly_one(cloud_listing, By.LINK_TEXT, cloud_name, self.fail, missing_message'Link to select {} is missing.'.format(cloud_name)).click()
        return cloud_listing

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
