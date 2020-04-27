from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec, wait
import unittest
from time import sleep
import web_common as wc

EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', ' ', 'Foreign', ' ', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', ' ', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', ' ', 'Slots', 'Slot Cores', 'Busy', 'Idle', ' ', 'Native Cores', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', ' ', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['status', 'main', 'database', 'rabbitmq', 'openstack', 'jobs', 'machines', 'timeseries', 'ec2', 'watch', 'VMdata', 'Cert Info', ' ', 'LOAD', 'RAM', 'SWAP', 'DISK']

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.load_web_settings('/cloud/status/')
        cls.driver = cls.gvar['driver']

    def test_nav(self):
        wc.assert_nav(self.driver, self.fail, self.gvar['address'])

    def test_status_tables(self):
        try:
            status_tables = self.gvar['driver_wait'].until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'status-table')))
        except TimeoutException:
            self.fail('Expected to find two elements with class \'status-table\', but did not find any.')
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables
        self.assert_table_has_headers(job_table, EXPECTED_JOB_HEADERS)
        self.assert_table_has_headers(vm_table, EXPECTED_VM_HEADERS)

    def test_system_table(self):
        system_table = wc.assert_one(self.driver, self.fail, (By.ID, 'system-services'))
        self.assert_table_has_headers(system_table, EXPECTED_SYSTEM_HEADERS)
        try:
            system_rows = wait.WebDriverWait(system_table, self.gvar['max_wait']).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'tr')))
        except TimeoutException:
            self.fail('Expected the system table ({}) to have rows (<tr>), but did not find any.')
        self.assertEqual(len(system_rows), 3)
        system_labels = [cell.text for cell in system_rows[2].find_elements_by_tag_name('td')]
        self.assertEqual(system_labels, EXPECTED_SYSTEM_LABELS)
        indicator_row = system_rows[1]
        for cell in indicator_row.find_elements_by_tag_name('td')[-4:]:
            cell_wait = wait.WebDriverWait(cell, self.gvar['max_wait'])
            wc.assert_one(cell_wait, self.fail, (By.TAG_NAME, 'meter'))

    def test_stop_refresh_button(self):
        system_div = wc.assert_one(self.driver, self.fail, (By.CLASS_NAME, 'system-div'))
        system_div_wait = wait.WebDriverWait(system_div, self.gvar['max_wait'])
        # Search for an element that has an id of 'CDTimer' and has text in it. (Text is required because the element is empty when first loaded.)
        countdown = wc.assert_one(system_div_wait, self.fail, (By.XPATH, './/*[(@id="CDTimer") and text()]'))
        stop_button = wc.assert_one(system_div_wait, self.fail, (By.CLASS_NAME, 'stop-symbol'))
        try:
            before = int(countdown.text)
            stop_button.click()
            sleep(3)
            after = int(countdown.text)
        except ValueError as err:
            self.fail('Unable to parse the refresh countdown \'{}\' as an int.'.format(countdown.text))
        # It seems to take up to about a second for the button to realize it has been pressed.
        self.assertLessEqual(after - before, 1)

    def assert_table_has_headers(self, table, expected_headers):
        '''Assert that the table has exactly the list of headers specified, in the order specified.
        table is a selenium.webdriver.firefox.webelement.FirefoxWebElement, or similar for a different browser. expected_headers is a list of strs.'''
        try:
            th_elems = wait.WebDriverWait(table, self.gvar['max_wait']).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'th')))
        except TimeoutException:
            self.fail('Expected to find <th> tags in the table with open tag {}, but did not find any.'.format(wc.get_open_tag(table)))
        actual_headers = []
        for header in th_elems:
            # Some headers may have tables within them to position parent headers over children headers. We want the headers inside these subtables, but not the tables themselves.
            try:
                header.find_element_by_tag_name('table')
            except NoSuchElementException:
                actual_headers.append(header.text)
        self.assertEqual(actual_headers, expected_headers)

    @classmethod
    def tearDownClass(cls):
        cls.gvar['driver'].quit()

if __name__ == '__main__':
    unittest.main()
