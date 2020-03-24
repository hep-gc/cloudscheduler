import web_common
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import re
import os.path
from time import sleep
import unittest

EXPECTED_NAV_LINKS = [('/cloud/status/', 'Status'), ('/cloud/list/', 'Clouds'), ('/alias/list/', 'Aliases'), ('/group/defaults/', 'Defaults'), ('/images/', 'Images'), ('/keypairs/', 'Keys'), ('/user/list/', 'Users'), ('/group/list/', 'Groups'), ('/server/config/', 'Config'), ('/user/settings/', 'User Settings'), ('/settings/log-out', 'Log out')]
EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', '&nbsp;', 'Foreign', '&nbsp;', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', '&nbsp;', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', '&nbsp;', 'Slots', 'Slot Cores', 'Busy', 'Idle', '&nbsp;', 'Native Cores', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', '&nbsp;', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['status', 'main', 'database', 'rabbitmq', 'openstack', 'jobs', 'machines', 'timeseries', 'ec2', 'watch', 'VMdata', '<nobr>Cert Info</nobr>', '&nbsp;', 'LOAD', 'RAM', 'SWAP', 'DISK']

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = web_common.setup()
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.settings['web']['firefox_profile']), service_log_path=os.path.expanduser('~/cloudscheduler/unit_tests/geckodriver.log'))
        try:
            cls.driver.get('{}/cloud/status'.format(cls.settings['address']))
            cls.driver.switch_to.alert.accept()
            # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
            WebDriverWait(cls.driver, 20).until(expected_conditions.presence_of_element_located((By.ID, 'system-services')))
        finally:
            cls.driver.quit()

    def test_nav(self):
        top_nav = self.driver.find_element_by_class_name('top-nav')
        nav_links = [(re.match(self.settings['address'] + r'([^?]+)', elem.get_attribute('href'))[1], elem.get_attribute('innerHTML')) for elem in top_nav.find_elements_by_tag_name('a')]
        self.assertEqual(nav_links, EXPECTED_NAV_LINKS)

    def test_status_tables(self):
        status_tables = self.driver.find_elements_by_class_name('status-table')
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables
        job_headers = [header.get_attribute('innerHTML') for header in job_table.find_elements_by_tag_name('th')]
        self.assertEqual(job_headers, EXPECTED_JOB_HEADERS)
        vm_headers = [header.get_attribute('innerHTML') for header in vm_table.find_elements_by_tag_name('th')]
        self.assertEqual(vm_headers, EXPECTED_VM_HEADERS)

    def test_system_table(self):
        system_table = self.driver.find_element_by_id('system-services')
        system_headers = [header.get_attribute('innerHTML') for header in system_table.find_elements_by_tag_name('th')]
        self.assertEqual(system_headers, EXPECTED_SYSTEM_HEADERS)
        system_rows = system_table.find_elements_by_tag_name('tr')
        self.assertEqual(len(system_rows), 3)
        system_labels = [cell.get_attribute('innerHTML') for cell in system_rows[2].find_elements_by_tag_name('td')]
        self.assertEqual(system_labels, EXPECTED_SYSTEM_LABELS)
        meter_counts = [len(cell.find_elements_by_tag_name('meter')) for cell in system_rows[1].find_elements_by_tag_name('td')]
        self.assertEqual(meter_counts, [1] * 4)

    def test_stop_refresh_button(self):
        system_div = self.driver.find_element_by_class('system-div')
        countdown = system_div.find_element_by_id('CDTimer')
        stop_buttons = system_div.find_elements_by_class_name('stop-symbol')
        self.assertEqual(len(stop_buttons), 1)
        before = int(countdown.get_attribute('innerHTML'))
        stop_buttons[0].click()
        sleep(3)
        after = int(countdown.get_attribute('innerHTML'))
        # It seems to take up to about a second for the button to realize it has been pressed.
        self.assertLessEqual(after - before, 1)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
