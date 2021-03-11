import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebStatusSuperUser(unittest.TestCase):
    """A class to test status operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['servers', 'status'])
        cls.page = pages.StatusPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        cls.cloud_name = cls.gvar['user'] + '-wic1'
        cls.group_name = cls.gvar['user'] + '-wig0'
        print("\nStatus Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Status')

    def test_web_status_find(self):
        pass

    def test_web_status_expand_job_group(self):
        self.page.click_jobs_group_expand(self.group_name)
        self.assertTrue(self.page.job_group_expanded(self.group_name))
        self.page.click_jobs_group_expand(self.group_name)

    def test_web_status_expand_vm_group(self):
        self.page.click_vms_group_expand(self.group_name)
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, self.cloud_name))
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, self.gvar['user'] + '-wic2'))
        self.page.click_vms_group_expand(self.group_name)

    def test_web_status_expand_vm_cloud(self):
        self.page.click_vms_cloud_expand(self.cloud_name)
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, self.cloud_name))
        self.page.click_vms_cloud_expand(self.cloud_name)

    def test_web_status_expand_vm_cloud_totals(self):
        cloud_name = 'Totals'
        self.page.click_vms_cloud_expand(cloud_name)
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, cloud_name))
        self.page.click_vms_cloud_expand(cloud_name)

    def test_web_status_plot_open(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.assertTrue(self.page.plot_open())
        self.page.click_close_plot()

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_jobs(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_jobs_idle(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_jobs_running(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_jobs_completed(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_jobs_held(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_jobs_other(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_jobs_foreign(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms_starting(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms_unregistered(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms_idle(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms_running(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms_retiring(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms_manual(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_vms_error(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_slots(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_slot_cores_busy(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_slot_cores_idle(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_native_cores_used(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_native_cores_limit(self):
        pass

    @unittest.skip("TODO: implement")
    def test_web_status_plot_open_ram(self):
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
