from cloudscheduler.unit_tests.unit_test_common import ut_id
import common
import unittest
import selenium

JOB_TABLE_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', 'Foreign', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']

VM_TABLE_HEADERS = ['Group', 'Clouds', 'RT (μs)', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', 'Slots', 'Busy', 'Idle', 'Used', 'Limit', 'RAM']

class TestStatus(unittest.TestCase):
    def setUpClass():
        self.server_address = common.setup()

    def setUp(self):
        self.driver = selenium.webdriver.Firefox()
        self.driver.get('{}/cloud/status'.format(self.server_address))

    def test_status_display(self):
        status_tables = self.driver.find_elements_by_class_name('status-tables')
        system_services = self.driver.find_element_by_id_name('system-services')
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables
        job_headers = [elem.get_attribute('innerHTML') for elem in job_table.find_elements_by_tag_name('th')]
        self.assertEqual(job_headers, JOB_TABLE_HEADERS)

    def tearDown(self):
        self.driver.close()
