from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
import re
import os.path
from time import sleep
import unittest
import web_common as wc

EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', '&nbsp;', 'Foreign', '&nbsp;', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', '&nbsp;', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', '&nbsp;', 'Slots', 'Slot Cores', 'Busy', 'Idle', '&nbsp;', 'Native Cores', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', '&nbsp;', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['status', 'main', 'database', 'rabbitmq', 'openstack', 'jobs', 'machines', 'timeseries', 'ec2', 'watch', 'VMdata', '<nobr>Cert Info</nobr>', '&nbsp;', 'LOAD', 'RAM', 'SWAP', 'DISK']

class TestClouds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.setup()
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.gvar['web']['firefox_profile']))
        try:
            wait = ui.WebDriverWait(cls.driver, 120)
            cls.driver.get('{}/cloud/list/'.format(cls.gvar['address']))
            wait.until(expected_conditions.alert_is_present()).accept()
            # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
            wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'menu')))
        except TimeoutException:
            cls.driver.quit()
            raise

    def test_nav(self):
        wc.test_nav(self)
    
    def test_menu(self):
        menus = self.driver.find_elements_by_class_name('menu')
        self.assertEqual(len(menus), 1)
        cloud_listing = wc.assert_exactly_one(menus[0], By.ID, '{}-wic1'.format(self.gvar['user']), self.fail, missing_message='{}-wic1 is missing from the list of clouds.'.format(self.gvar['user']))
        try:
            next((link for link in cloud_listing.find_elements_by_tag_name('a') if link.get_attribute('href') == '{0}/cloud/list/#{1}-wic1'.format(self.gvar['address'], self.gvar['user']))).click()
        except StopIteration:
            self.fail('Link to select {}-wic1 is missing.'.format(self.gvar['user']))
        # The link text below is not a hyphen but a minus sign (U+2212).
        self.assert_exactly_one(cloud_listing, By.LINK_TEXT, '−', self.fail, missing_message='Link to delete {}-wic1 is missing.'.format(self.gvar['user']))
        cloud_sections = [label.get_attribute('innerHTML') for label in self.driver.find_elements_by_xpath('//*[@class="menu"]/*[@id="{}-wic1"]//*[@class="tab"]/label'.format(self.gvar['user']))]
        self.assertEqual(cloud_sections, ['Settings', 'Metadata', 'Exclusions'])
        self.assert_exactly_one(menus[0], By.ID, 'add-cloud', self.fail, missing_message='Link to add a cloud is missing.')

    def test_add(self):
        add_button = wc.assert_exactly_one(self.driver, By.XPATH, '//*[@class="menu"]/*[@id="add-cloud"]', self.fail, missing_message='Link to add a cloud is missing.')
        wc.assert_exactly_one(add_button, By.LINK_TEXT, '+', self.fail).click()
        add_forms = [form for form in add_button.get_elements_by_tag_name('form') if form.get_attribute('name') == 'add_form']
        self.assertEqual(len(add_forms), 1)
        new_cloud_settings = {'cloud_name': '{}-wic4'.format(self.gvar['user']), 'cloud_type': 'openstack', **self.gvar['cloud_credentials'], 'enabled': True}
        wc.submit_form(add_forms[0], new_cloud_settings, self.fail)
    
    @unittest.skip
    def test_delete(self):
        raise NotImplementedError()

    @unittest.skip
    def test_settings(self):
        raise NotImplementedError()

    @unittest.skip
    def test_metadata(self):
        raise NotImplementedError()

    @unittest.skip
    def test_exclusions(self):
        raise NotImplementedError()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
