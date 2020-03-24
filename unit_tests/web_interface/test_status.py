import web_common
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

EXPECTED_NAV_LINKS = [('/cloud/status/', 'Status'), ('/cloud/list/', 'Clouds'), ('/alias/list/', 'Aliases'), ('/group/defaults/', 'Defaults'), ('/images/', 'Images'), ('/keypairs/', 'Keys'), ('/user/list/', 'Users'), ('/group/list/', 'Groups'), ('/server/config/', 'Config'), ('/user/settings/', 'User Settings'), ('/settings/log-out', 'Log out')]
EXPECTED_JOB_HEADERS = ['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Held', 'Other', '&nbsp;', 'Foreign', '&nbsp;', 'Condor FQDN', 'Condor Status', 'Agent Status', 'Condor Cert', 'Worker Cert']
EXPECTED_VM_HEADERS = ['Group', 'Clouds', 'RT (μs)', '&nbsp;', 'VMs', 'Starting', 'Unreg.', 'Idle', 'Running', 'Retiring', 'Manual', 'Error', '&nbsp;', 'Slots', 'Busy', 'Idle', '&nbsp;', 'Used', 'Limit', 'RAM']
EXPECTED_SYSTEM_HEADERS = ['CS system services', '&nbsp;', 'CS system resources']
EXPECTED_SYSTEM_LABELS = ['status', 'main', 'database', 'rabbitmq', 'openstack', 'jobs', 'machines', 'timeseries', 'ec2', 'watch', 'VMdata', '<nobr>Cert Info</nobr>', '&nbsp;', 'LOAD', 'RAM', 'SWAP', 'DISK']

class TestStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = web_common.setup()
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.settings['web']['firefox_profile']))
        cls.driver.get('{}/cloud/status'.format(cls.settings['address']))
        cls.driver.switch_to.alert.accept()
        WebDriverWait(cls.driver, 20).until(expected_conditions.presence_of_element_located((By.ID, 'system-services')))

    def test_status_display(self):
        top_navs = self.driver.find_elements_by_class_name('top-nav')
        self.assertEqual(len(top_navs), 1)
        nav_links = [(re.match(cls.settings['address'] + r'([^?]+)', elem.get_attribute('href'))[1], elem.get_attribute('innerHTML')) for elem in top_navs[0].find_elements_by_tag_name('a')]
        self.assertEqual(nav_links, EXPECTED_NAV_LINKS)
        status_tables = self.driver.find_elements_by_class_name('status-table')
        system_table = self.driver.find_element_by_id('system-services')
        self.assertEqual(len(status_tables), 2)
        job_table, vm_table = status_tables
        job_headers = [elem.get_attribute('innerHTML') for elem in job_table.find_elements_by_tag_name('th')]
        self.assertEqual(job_headers, EXPECTED_JOB_HEADERS)
        # vm_headers = [elem.get_attribute('innerHTML') for elem in vm_table.find_elements_by_tag_name('th')]
        # self.assertEqual(vm_headers, EXPECTED_VM_HEADERS)
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
