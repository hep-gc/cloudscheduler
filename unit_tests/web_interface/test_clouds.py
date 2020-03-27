from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
import unittest
import web_common as wc

EXPECTED_CLOUD_TABS = ['Settings', 'Metadata', 'Exclusions']

class TestClouds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.setup()
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.gvar['web']['firefox_profile']))
        try:
            cls.wait = ui.WebDriverWait(cls.driver, 40)
            cls.driver.get('{}/cloud/list/'.format(cls.gvar['address']))
            cls.wait.until(expected_conditions.alert_is_present()).accept()
            # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
            cls.wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'menu')))
        except TimeoutException:
            cls.driver.quit()
            raise
        cls.active_group = '{}-wig1'.format(cls.gvar['user'])
        cls.cloud_to_list = '{}-wic1'.format(cls.gvar['user'])
        cls.cloud_to_delete = '{}-wic2'.format(cls.gvar['user'])
        cls.cloud_to_update = '{}-wic3'.format(cls.gvar['user'])
        cls.cloud_to_add = '{}-wic4'.format(cls.gvar['user'])
        cls.metadata_to_list = '{}-wicm1'.format(cls.gvar['user'])
        cls.metadata_to_delete = '{}-wicm2'.format(cls.gvar['user'])
        cls.metadata_to_update = '{}-wicm3'.format(cls.gvar['user'])
        cls.metadata_to_add = '{}-wicm4'.format(cls.gvar['user'])

    def test_nav(self):
        wc.test_nav(self)
    
    def test_menu(self):
        cloud_listing = self.select_cloud(self.cloud_to_list)
        # self.select_cloud() already asserted the existence and singularity of menu, but we need to reference it later.
        menu = self.driver.find_element_by_class_name('menu')
        # The link text below is not a hyphen but a minus sign (U+2212).
        wc.assert_exactly_one(cloud_listing, (By.LINK_TEXT, '−'), None, self.fail, missing_message='The link to delete {} is missing.'.format(self.cloud_to_list))
        # Look for descendants of cloud_listing that are of class 'tab', then within those look for labels. Create a list of the innerHTMLs of all such labels.
        cloud_tabs = [label.get_attribute('innerHTML') for label in cloud_listing.find_elements_by_xpath('.//*[@class="tab"]/label'.format(self.cloud_to_list))]
        self.assertEqual(cloud_tabs, EXPECTED_CLOUD_TABS)
        wc.assert_exactly_one(menu, (By.ID, 'add-cloud'), None, self.fail, missing_message='The link to add a cloud is missing.')

    def test_cloud_add(self):
        menu = wc.assert_exactly_one(self.driver, (By.CLASS_NAME, 'menu'), None, self.fail)
        add_listing = wc.assert_exactly_one(menu, (By.ID, 'add-cloud'), None, self.fail, missing_message='The link to add a cloud is missing.')
        wc.assert_exactly_one(add_listing, (By.LINK_TEXT, '+'), None, self.fail).click()
        add_form = wc.assert_exactly_one(add_listing, (By.TAG_NAME, 'form'), {'name': 'add_cloud'}, self.fail)
        new_cloud_settings = {'cloud_name': self.cloud_to_add, 'cloud_type': 'openstack', **self.gvar['cloud_credentials'], 'enabled': True}
        wc.submit_form(add_form, new_cloud_settings, self.fail)
    
    def test_cloud_delete(self):
        cloud_listing = self.select_cloud(self.cloud_to_delete)
        delete_link = wc.assert_exactly_one(cloud_listing, (By.LINK_TEXT, '−'), None, self.fail, missing_message='The link to delete {} is missing.'.format(self.cloud_to_delete))
        delete_link.click()
        delete_dialog = wc.assert_exactly_one(self.driver, (By.ID, 'delete-{}'.format(self.cloud_to_delete)), None, self.fail)
        # Cancel the deletion.
        wc.assert_exactly_one(delete_dialog, (By.LINK_TEXT, 'X'), None, self.fail, missing_message='The button to close the delete confirmation dialog is missing for {}.'.format(self.cloud_to_delete)).click()
        # Assert that the cloud still exists.
        try:
            cloud_listing.get_attribute('id')
        # We turn this exception into a failure because there is a difference between a test error and a test failure.
        except StaleElementReferenceException:
            self.fail('{} was removed from the list of clouds even though the deletion was cancelled.'.format(self.cloud_to_delete))
        delete_link.click()
        # Confirm deletion.
        wc.assert_exactly_one(delete_dialog, (By.TAG_NAME, 'input'), {'type': 'submit'}, self.fail, missing_message='The button to confirm deletion is missing from the delete confirmation dialog for {}.'.format(self.cloud_to_delete)).click()
        # Wait for the deletion to occur.
        self.wait.until(expected_conditions.invisibility_of_element(delete_dialog))
        # Assert that the cloud has been removed.
        self.assertRaises(StaleElementReferenceException, cloud_listing.get_attribute, 'id')

    @unittest.skip
    def test_cloud_update(self):
        raise NotImplementedError()

    def test_settings_tab(self):
        cloud_listing = self.select_cloud(self.cloud_to_list)
        # self.test_menu() asserts for us the presence and order of the tabs, so we assume it here.
        settings_tab = cloud_listing.find_elements_by_class_name('tab')[0]
        settings_tab.click()
        wc.assert_exactly_one(settings_tab, (By.TAG_NAME, 'form'), {'name': self.cloud_to_list}, self.fail, missing_message='The settings form for {} is missing.'.format(self.cloud_to_list))

    def test_metadata_tab(self):
        cloud_listing = self.select_cloud(self.cloud_to_list)
        metadata_tab = cloud_listing.find_elements_by_class_name('tab')[1]
        metadata_tab.click()
        tab_content = wc.assert_exactly_one(metadata_tab, (By.CLASS_NAME, 'tab-content'), None, self.fail)
        # Look within tab_content for elements of class 'tab2' (i.e. sub-tabs). Within each of these, look for labels with an innerHTML of self.metadata_to_list.
        metadata_listing = wc.assert_exactly_one(tab_content, (By.XPATH, './*[contains(@class, "tab2")][label/text()="{}"]'.format(self.metadata_to_list)), None, self.fail, missing_message='{} is missing from the list of metadata for {}'.format(self.metadata_to_list, self.cloud_to_list))
        # We already know this label exists, but we need to find it so we can click on it.
        wc.assert_exactly_one(metadata_listing, (By.TAG_NAME, 'label'), {'innerHTML': self.metadata_to_list}, self.fail).click()
        # Wait until the src of the iframe has been updated.
        fetch_url = '{}/cloud/metadata-fetch?{}&cloud_name={}&metadata_name={}'.format(self.gvar['address'], self.active_group, self.cloud_to_list, self.metadata_to_list)
        iframe = ui.WebDriverWait(metadata_listing, 40).until(expected_conditions.presence_of_element_located((By.XPATH, './/iframe[@src="{}"]'.format(fetch_url)))
        try:
            self.driver.switch_to.frame(iframe)
            fetch_form = self.wait.until(expected_conditions.presence_of_element_located((By.NAME, 'metadata-form')))
            wc.assert_exactly_one(fetch_form, (By.TAG_NAME, 'input'), {'type': 'submit', 'value': 'Update'}, self.fail, missing_message='The \'Update\' button is missing from the form to update {}'.format(self.metadata_to_list))
            wc.assert_exactly_one(fetch_form, (By.TAG_NAME, 'a'), {'href': '{}#delete-metadata'.format(fetch_url)}, self.fail, missing_message='The button to delete {} is missing.'.format(self.metadata_to_list))
        # Switch back so that other tests don't fail if this one does.
        finally:
            self.driver.switch_to.default_content()

    @unittest.skip
    def test_exclusions_tab(self):
        raise NotImplementedError()

    def select_cloud(self, cloud_name):
        menu = wc.assert_exactly_one(self.driver, (By.CLASS_NAME, 'menu'), None, self.fail)
        cloud_listing = wc.assert_exactly_one(menu, (By.ID, cloud_name), None, self.fail, missing_message='{} is missing from the list of clouds.'.format(cloud_name))
        wc.assert_exactly_one(cloud_listing, (By.LINK_TEXT, cloud_name), None, self.fail, missing_message='The link to select {} is missing.'.format(cloud_name)).click()
        return cloud_listing

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
