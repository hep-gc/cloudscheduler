from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, ui
import unittest
import re
from time import sleep
import web_common

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
            cls.driver.get('{}/cloud/status'.format(cls.settings['address']))
            wait.until(expected_conditions.alert_is_present()).accept()
            # The internet says that driver.get() should automatically wait for the page to be loaded, but it does not seem to.
            wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'status-table')))
        except TimeoutException:
            cls.driver.quit()

    def test_nav(self):
        web_common.test_nav(self)

    def test_status_tables(self):
        status_tables = self.driver.find_elements_by_class_name('status-table')
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables
        job_headers = [header.get_attribute('innerHTML') for header in job_table.find_elements_by_tag_name('th')]
        self.assertEqual(job_headers, EXPECTED_JOB_HEADERS)
        vm_headers = []
        # Some headers have tables within them to position parent headers over children headers.
        for header in vm_table.find_elements_by_tag_name('th'):
            try:
                header.find_element_by_tag_name('table')
            except NoSuchElementException:
                vm_headers.append(header.get_attribute('innerHTML'))
        self.assertEqual(vm_headers, EXPECTED_VM_HEADERS)

    def test_system_table(self):
        try:
            system_table = self.driver.find_element_by_id('system-services')
        except NoSuchElementException:
            self.fail('Table with ID \'system-services\' is missing.')
        system_headers = [header.get_attribute('innerHTML') for header in system_table.find_elements_by_tag_name('th')]
        self.assertEqual(system_headers, EXPECTED_SYSTEM_HEADERS)
        system_rows = system_table.find_elements_by_tag_name('tr')
        self.assertEqual(len(system_rows), 3)
        system_labels = [cell.get_attribute('innerHTML') for cell in system_rows[2].find_elements_by_tag_name('td')]
        self.assertEqual(system_labels, EXPECTED_SYSTEM_LABELS)
        for cell in system_rows[1].find_elements_by_tag_name('td')[-4:]:
            self.assertEquals(cell.find_elements_by_tag_name('meter'), 1)

    def test_stop_refresh_button(self):
        system_divs = self.driver.find_elements_by_class_name('system-div')
        self.assertEqual(len(system_divs), 1)
        countdown = system_divs[0].find_element_by_id('CDTimer')
        stop_buttons = system_divs[0].find_elements_by_class_name('stop-symbol')
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
