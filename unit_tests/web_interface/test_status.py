from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import unittest
from time import sleep
import web_common as wc

EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', ' ', 'Foreign', ' ', 'Condor FQDN', 'Condor Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', ' ', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', ' ', 'Slots', 'Slot Cores', 'Busy', 'Idle', ' ', 'Native Cores', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', ' ', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['main', 'signals', 'timeseries', 'VMdata', 'watch', 'ec2', 'openstack', ' ', 'LOAD', 'RAM', 'SWAP', 'DISK']

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gvar = wc.load_web_settings('/cloud/status/')
        cls.driver = cls.gvar['driver']
        def raise_assertion_error(message):
            raise AssertionError(message)
        # Click the stop refresh button so that the page does not refresh in the middle of one of the tests.
        wc.assert_one(cls.driver, raise_assertion_error, (By.XPATH, '//*[contains(@class, "system-div")]//*[contains(@class, "refresh-button")]//*[contains(@class, "stop-symbol")]')).click()

    def test_nav(self):
        wc.assert_nav(self.driver, self.fail, self.gvar['address'])

    def test_status_tables(self):
        status_tables = self.driver.find_elements(By.CLASS_NAME, 'status-table')
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables
        self.assert_table_has_headers(job_table, EXPECTED_JOB_HEADERS)
        self.assert_table_has_headers(vm_table, EXPECTED_VM_HEADERS)

    def test_system_table(self):
        system_table = wc.assert_one(self.driver, self.fail, (By.ID, 'system-services'))
        self.assert_table_has_headers(system_table, EXPECTED_SYSTEM_HEADERS)
        system_rows = system_table.find_elements(By.TAG_NAME, 'tr')
        self.assertEqual(len(system_rows), 3)
        system_labels = [cell.text for cell in system_rows[2].find_elements(By.TAG_NAME, 'td')]
        self.assertEqual(system_labels, EXPECTED_SYSTEM_LABELS)
        indicator_row = system_rows[1]
        for cell in indicator_row.find_elements(By.TAG_NAME, 'td')[-4:]:
            wc.assert_one(cell, self.fail, (By.TAG_NAME, 'meter'))

    def test_stop_refresh_button(self):
        # The stop refresh button has already been clicked, so we reload the page to restart the countdown.
        self.driver.get(self.gvar['address'])
        system_div = wc.assert_one(self.driver, self.fail, (By.CLASS_NAME, 'system-div'))
        stop_button = wc.assert_one(system_div, self.fail, (By.CLASS_NAME, 'stop-symbol'))
        try:
            countdown = wc.assert_one(system_div, self.fail, (By.XPATH, './/*[(@id="CDTimer") and text()]'))
            try:
                before = int(countdown.text)
                stop_button.click()
                sleep(3)
                after = int(countdown.text)
            except ValueError:
                self.fail('Unable to parse the refresh countdown \'{}\' as an int.'.format(countdown.text))
        # Ensure that the stop button is clicked so that the page does not reload in the middle of other tests.
        except:
            stop_button.click()
            raise
        # It seems to take up to about a second for the button to realize it has been pressed.
        self.assertLessEqual(after - before, 1)

    def assert_table_has_headers(self, table, expected_headers):
        '''
        Assert that the table has exactly the list of headers specified, in the order specified.
        table is a selenium.webdriver.firefox.webelement.FirefoxWebElement, or similar for a different browser.
        expected_headers is a list of strs.
        '''
        
        th_elems = table.find_elements(By.TAG_NAME, 'th')
        if not th_elems:
            self.fail('Expected to find <th> tags in the table with open tag {}, but did not find any.'.format(wc.get_open_tag(table)))
        actual_headers = []
        # We want to check that many elements do *not* exist, and Selenium will wait the full wait time for each of them, so we decrease the wait time temporarily.
        self.driver.implicitly_wait(0.1)
        for header in th_elems:
            # Some headers may have tables within them to position parent headers over children headers. We want the headers inside these subtables, but not the tables themselves.
            try:
                header.find_element(By.TAG_NAME, 'table')
            except NoSuchElementException:
                actual_headers.append(header.text)
        self.driver.implicitly_wait(self.gvar['max_wait'])
        self.assertEqual(actual_headers, expected_headers)

    @classmethod
    def tearDownClass(cls):
        cls.gvar['driver'].quit()

if __name__ == '__main__':
    unittest.main()
