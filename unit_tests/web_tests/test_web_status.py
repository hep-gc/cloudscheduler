import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebStatusSuperUser(unittest.TestCase):
    """A class to test status operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['status'])
        cls.page = pages.StatusPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        print("\nStatus Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Status')

    def test_web_status_find(self):
        pass

    def test_web_status_expand_job_group(self):
        group_name = self.gvar['user'] + '-wig0'
        self.page.click_jobs_group_expand(group_name)
        self.assertTrue(self.page.job_group_expanded(group_name))
        self.page.click_jobs_group_expand(group_name)

    def test_web_status_expand_vm_group(self):
        group_name = self.gvar['user'] + '-wig0'
        self.page.click_vms_group_expand(group_name)
        self.assertTrue(self.page.vm_cloud_expanded(group_name, self.gvar['user'] + '-wic1'))
        self.assertTrue(self.page.vm_cloud_expanded(group_name, self.gvar['user'] + '-wic2'))
        self.page.click_vms_group_expand(group_name)

    def test_web_status_expand_vm_cloud(self):
        cloud_name = self.gvar['user'] + '-wic1'
        group_name = self.gvar['user'] + '-wig0'
        self.page.click_vms_cloud_expand(cloud_name)
        self.assertTrue(self.page.vm_cloud_expanded(group_name, cloud_name))
        self.page.click_vms_cloud_expand(cloud_name)

    def test_web_status_expand_vm_cloud_totals(self):
        cloud_name = 'Totals'
        group_name = self.gvar['user'] + '-wig0'
        self.page.click_vms_cloud_expand(cloud_name)
        self.assertTrue(self.page.vm_cloud_expanded(group_name, cloud_name))
        self.page.click_vms_cloud_expand(cloud_name)

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
