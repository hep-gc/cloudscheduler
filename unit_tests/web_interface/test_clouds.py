import web_common
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
import re
import os.path
from time import sleep
import unittest

EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', '&nbsp;', 'Foreign', '&nbsp;', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', '&nbsp;', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', '&nbsp;', 'Slots', 'Slot Cores', 'Busy', 'Idle', '&nbsp;', 'Native Cores', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', '&nbsp;', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['status', 'main', 'database', 'rabbitmq', 'openstack', 'jobs', 'machines', 'timeseries', 'ec2', 'watch', 'VMdata', '<nobr>Cert Info</nobr>', '&nbsp;', 'LOAD', 'RAM', 'SWAP', 'DISK']

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.settings = web_common.setup()
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.settings['web']['firefox_profile']))
        try:
            wait = ui.WebDriverWait(cls.driver, 20)
            cls.driver.get('{}/cloud/list'.format(cls.settings['address']))
            wait.until(expected_conditions.alert_is_present()).accept()
            # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
            wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'menu')))
        except TimeoutException:
            cls.driver.quit()

    def test_nav(self):
        web_common.test_nav(self)
    
    def test_menu(self):
        menus = self.driver.find_elements_by_class_name('menu')
        self.assertEqual(len(menus), 1)
        cloud_listing = self.assert_exists(menus[0].find_element_by_id, '{}-wic1'.format(self.settings['user']), '{}-wic1 is missing from the list of clouds.'.format(self.settings['user']))
        try:
            next((link for link in cloud_listing.find_elements_by_tag_name('a') if link.get_attribute('href') == '#{}-wic1'.format(self.settings['user']))).click()
        except StopIteration:
            self.fail('Link to select {}-wic1 is missing.'.format(self.settings['user']))
        self.assert_exists(cloud_listing.find_element_by_link_text, '-', 'Link to delete {}-wic1 is missing.'.format(self.settings['user']))
        cloud_options = [label.get_attriubte('innerHTML') for label in cloud_listing.find_elements_by_tag_name('label')]
        self.assertEqual(cloud_options, ['Settings', 'Metadata', 'Exclusions'])
        assert_exists(menu.find_element_by_id, 'add-cloud', 'Link to add a cloud is missing.')

    def assert_exists(self, finder, identifier, message):
        '''Assert that finder (a find_element[s]_by_* method) returns at least one element when passed idenifier (str).'''
        try:
            elements = finder(identifier)
        except NoSuchElementException:
            self.fail(message)
        if isinstance(elements, list) and not elements:
            self.fail(message)
        return elements

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
