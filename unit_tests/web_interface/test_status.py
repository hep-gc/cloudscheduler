from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common import expected_conditions as ec, wait
from selenium.webdriver.common.by import By
import unittest
from time import sleep
import web_common as wc

EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', '&nbsp;', 'Foreign', '&nbsp;', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', '&nbsp;', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', '&nbsp;', 'Slots', 'Slot Cores', 'Busy', 'Idle', '&nbsp;', 'Native Cores', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', '&nbsp;', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['status', 'main', 'database', 'rabbitmq', 'openstack', 'jobs', 'machines', 'timeseries', 'ec2', 'watch', 'VMdata', '<nobr>Cert Info</nobr>', '&nbsp;', 'LOAD', 'RAM', 'SWAP', 'DISK']

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.setup('/cloud/status/')
        cls.driver = cls.gvar['driver']
        cls.wait = cls.gvar['wait']

    def test_nav(self):
        wc.test_nav(self.driver, self.wait, self.fail)

    def test_status_tables(self):
        status_tables = self.wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'status-table')))
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables
        job_header_elems = wait.WebDriverWait(job_table, gvar['max_wait']).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'th')))
        job_headers = [header.get_attribute('innerHTML') for header in job_header_elems]
        self.assertEqual(job_headers, EXPECTED_JOB_HEADERS)
        vm_headers = []
        # Some headers have tables within them to position parent headers over children headers. We want the headers inside these subtables, but not the tables themselves.
        for header in wait.WebDriverWait(vm_table, gvar['max_wait']).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'th')):
            try:
                header.find_element_by_tag_name('table')
            except NoSuchElementException:
                vm_headers.append(header.get_attribute('innerHTML'))
        self.assertEqual(vm_headers, EXPECTED_VM_HEADERS)

    def test_system_table(self):
        system_table = wc.assert_exactly_one(self.driver, (By.ID, 'system-services'), None, self.fail)
        system_header_elems = wait.WebDriverWait(system_table, gvar['max_wait']).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'th')))
        system_headers = [header.get_attribute('innerHTML') for header in system_header_elems]
        self.assertEqual(system_headers, EXPECTED_SYSTEM_HEADERS)
        system_rows = wait.WebDriverWait(system_table, gavr['max_wait']).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'tr')))
        self.assertEqual(len(system_rows), 3)
        system_labels = [cell.get_attribute('innerHTML') for cell in system_rows[2].find_elements_by_tag_name('td')]
        self.assertEqual(system_labels, EXPECTED_SYSTEM_LABELS)
        for cell in system_rows[1].find_elements_by_tag_name('td')[-4:]:
            wc.assert_exactly_one(cell, (By.TAG_NAME, 'meter'), None, self.fail)

    def test_stop_refresh_button(self):
        system_div = wc.assert_exactly_one(self.driver, self.wait, self.fail, (By.CLASS_NAME, 'system-div'))
        countdown = wc.assert_exactly_one(system_div, self.wait, self.fail, (By.ID, 'CDTimer'))
        stop_button = wc.assert_exactly_one(system_div, self.wait, self.fail, (By.CLASS_NAME, 'stop-symbol'))
        try:
            before = int(countdown.get_attribute('innerHTML'))
            stop_button.click()
            sleep(3)
            after = int(countdown.get_attribute('innerHTML'))
        except ValueError:
            self.fail('Unable to parse refresh countdown as an int.')
        # It seems to take up to about a second for the button to realize it has been pressed.
        self.assertLessEqual(after - before, 1)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
