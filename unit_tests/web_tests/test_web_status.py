import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebStatusCommon(unittest.TestCase):
    """A class to test status operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.StatusPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        cls.cloud_name = cls.gvar['user'] + '-wic1'
        cls.group_name = cls.gvar['user'] + '-wig0'

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

    def test_web_status_plot_open_jobs(self):
        self.page.click_job_data_box(self.group_name, 'Jobs')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_idle(self):
        self.page.click_job_data_box(self.group_name, 'Idle')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_idle'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_running(self):
        self.page.click_job_data_box(self.group_name, 'Running')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_running'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_completed(self):
        self.page.click_job_data_box(self.group_name, 'Completed')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_completed'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_held(self):
        self.page.click_job_data_box(self.group_name, 'Held')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_held'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_other(self):
        self.page.click_job_data_box(self.group_name, 'Other')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_other'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_foreign(self):
        self.page.click_job_data_box(self.group_name, 'Foreign')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_foreign'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_starting(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Starting')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_starting'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_unregistered(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Unregistered')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_unregistered'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_idle(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Idle')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_idle'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_running(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Running')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_running'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_retiring(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Retiring')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_retiring'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_manual(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Manual')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_manual'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_error(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Error')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_in_error'))
        self.page.click_close_plot()

    def test_web_status_plot_open_slots(self):
        self.page.click_slot_data_box(self.group_name, self.cloud_name, 'Slots')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' slot_count'))
        self.page.click_close_plot()

    def test_web_status_plot_open_slot_cores_busy(self):
        self.page.click_slot_data_box(self.group_name, self.cloud_name, 'Busy')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' slot_core_count'))
        self.page.click_close_plot()

    def test_web_status_plot_open_slot_cores_idle(self):
        self.page.click_slot_data_box(self.group_name, self.cloud_name, 'Idle')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' slot_idle_core_count'))
        self.page.click_close_plot()

    def test_web_status_plot_open_native_cores_used(self):
        self.page.click_native_cores_data_box(self.group_name, self.cloud_name, 'Used')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' cores_native'))
        self.page.click_close_plot()

    def test_web_status_plot_open_native_cores_limit(self):
        self.page.click_native_cores_data_box(self.group_name, self.cloud_name, 'Limit')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' cores_limit'))
        self.page.click_close_plot()

    def test_web_status_plot_open_ram(self):
        self.page.click_ram_data_box(self.group_name, self.cloud_name)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' ram_native'))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_one(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 1 hour')
        self.assertTrue(self.page.first_time_on_plot_before_now(1, 'hours', 10))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_minutes_five(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 5 minutes')
        self.assertTrue(self.page.first_time_on_plot_before_now(5, 'minutes', 0.5))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_minutes_fifteen(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 15 minutes')
        self.assertTrue(self.page.first_time_on_plot_before_now(15, 'minutes', 2))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_minutes_thirty(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 30 minutes')
        self.assertTrue(self.page.first_time_on_plot_before_now(30, 'minutes', 5))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_three(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 3 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now(3, 'hours', 30))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_six(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 6 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now(6, 'hours', 60))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_twelve(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 12 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now(12, 'hours', 120))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_twenty_four(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 24 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now(24, 'hours', 180))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_seven(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 7 days')
        self.assertTrue(self.page.first_date_on_plot_before_now(7, 'days', 1))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_thirty(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 30 days')
        self.assertTrue(self.page.first_date_on_plot_before_now(30, 'days', 7))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_sixty(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 60 days')
        self.assertTrue(self.page.first_date_on_plot_before_now(60, 'days', 7))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_ninety(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 90 days')
        self.assertTrue(self.page.first_date_on_plot_before_now(90, 'days', 14))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_months_six(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 6 months')
        self.assertTrue(self.page.first_date_on_plot_before_now(6, 'months', 31))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_years_one(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 1 year')
        self.assertTrue(self.page.first_date_on_plot_before_now(1, 'years', 62))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_years_two(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 2 years')
        self.assertTrue(self.page.first_date_on_plot_before_now(2, 'years', 93))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_years_five(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 5 years')
        self.assertTrue(self.page.first_date_on_plot_before_now(5, 'years', 186))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_previous_day(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Yesterday')
        self.assertTrue(self.page.first_time_on_plot_before_now(2, 'days', 180))
        self.assertTrue(self.page.last_time_on_plot_before_now(1, 'days', 180))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_day_before_yesterday(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Day before yesterday')
        self.assertTrue(self.page.first_time_on_plot_before_now(3, 'days', 180))
        self.assertTrue(self.page.last_time_on_plot_before_now(2, 'days', 180))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_day_last_week(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('This day last week')
        self.assertTrue(self.page.first_time_on_plot_before_now(193, 'hours', 180))
        self.assertTrue(self.page.last_time_on_plot_before_now(7, 'days', 180))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_previous_week(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Previous week')
        self.assertTrue(self.page.first_date_on_plot_before_now(14, 'days', 1))
        self.assertTrue(self.page.last_date_on_plot_before_now(7, 'days', 1))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_previous_month(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Previous month')
        self.assertTrue(self.page.first_date_on_plot_before_now(2, 'months', 7))
        self.assertTrue(self.page.last_date_on_plot_before_now(1, 'months', 7))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_previous_year(self):
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Previous year')
        self.assertTrue(self.page.first_date_on_plot_before_now(2, 'years', 62))
        self.assertTrue(self.page.last_date_on_plot_before_now(1, 'years', 62))
        self.page.click_close_plot()

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebStatusSuperUser(TestWebStatusCommon):
    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['servers', 'status'])
        super(TestWebStatusSuperUser, cls).setUpClass()
        print("\nStatus Tests (Super User):")
   
class TestWebStatusRegularUser(TestWebStatusCommon):
    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['servers', 'status'])
        super(TestWebStatusRegularUser, cls).setUpClass()
        print("\nStatus Tests (Regular User):")

if __name__ == "__main__":
    unittest.main()
