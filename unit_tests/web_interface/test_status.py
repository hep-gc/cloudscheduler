import web_common
import unittest
import selenium

EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', 'Foreign', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', 'Slots', 'Busy', 'Idle', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['status', 'main', 'database', 'rabbitmq', 'openstack', 'jobs', 'machines', 'timeseries', 'ec2', 'watch', 'VMdata', 'Cert Info']

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_address = web_common.setup()['address']
        cls.driver = selenium.webdriver.Firefox()
        cls.driver.get('{}/cloud/status'.format(self.server_address))

    def test_status_display(self):
        status_tables = self.driver.find_elements_by_class_name('status-tables')
        system_table = self.driver.find_element_by_id_name('system-services')
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables

        job_headers = [elem.get_attribute('innerHTML') for elem in job_table.find_elements_by_tag_name('th')]
        self.assertEqual(job_headers, EXPECTED_JOB_HEADERS)
        vm_headers = [elem.get_attribute('innerHTML') for elem in vm_table.find_elements_by_tag_name('th')]
        self.assertEqual(vm_headers, EXPECTED_VM_HEADERS)
        system_headers = [elem.get_attribute('innerHTML') for elem in system_table.find_elements_by_tag_name('th')]
        self.assertEqual(system_headers, EXPECTED_SYSTEM_HEADERS)
        system_rows = system_table.find_elements_by_tag_name('tr')
        self.assertEqual(len(system_rows), 3)
        system_labels = [elem.get_attribute('innerHTML') for elem in system_rows[2].find_elements_by_tag_name('td')]
        self.assertEqual(system_labels, EXPECTED_SYSTEM_LABELS)
        refresh_buttons = self.driver.find_elements_by_class_name('refresh-button')
        self.assertEqual(len(refresh_buttons), 1)

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
