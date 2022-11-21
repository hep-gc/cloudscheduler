if __name__ == "__main__" or __name__ == "test_web_status":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_interactions as wti
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers

class TestWebStatusCommon(unittest.TestCase):
    """A class for the status tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls, user_type=''):
        cls.page = pages.StatusPage(cls.driver, cls.gvar['address'])
        cls.oversize = cls.gvar['oversize']
        cls.cloud_name = cls.gvar['user'] + '-wic1'
        cls.group_name = cls.gvar['user'] + '-wig0'
        cls.user = cls.gvar['user'] + '-wiu2'
        cls.alias = 'None'
        cls.user_type = user_type
        if user_type == 'regular':
            cls.user = cls.gvar['user'] + '-wiu1'

    def setUp(self):
        self.page.get_homepage()
        self.page.click_top_nav('Status')

    def __setAliasView(self):
        self.page.click_top_nav('User Settings')
        self.page.click_side_button(self.user)
        self.page.click_jobs_by_alias_checkbox()
        self.page.click_update_user()
        self.page.click_top_nav('Status')

    def test_web_status_find(self):
        # Finds the status page
        pass

    '''
    def test_web_status_expand_job_group(self):
        # Expands the by-group menu for jobs
        self.page.click_jobs_group_expand(self.group_name)
        self.assertTrue(self.page.job_group_expanded(self.group_name))
        self.page.click_jobs_group_expand(self.group_name)
    
    
    def test_web_status_expand_vm_group(self):
        # Expands the by-group menu for vms
        self.page.click_vms_group_expand(self.group_name)
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, self.cloud_name))
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, self.gvar['user'] + '-wic2'))
        self.page.click_vms_group_expand(self.group_name)

    def test_web_status_expand_vm_cloud(self):
        # Expands the by-cloud menu for vms
        self.page.click_vms_cloud_expand(self.cloud_name)
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, self.cloud_name))
        self.page.click_vms_cloud_expand(self.cloud_name)

    def test_web_status_expand_vm_cloud_totals(self):
        # Expands the by0cloud menu for vm totals
        cloud_name = 'Totals'
        self.page.click_vms_cloud_expand(cloud_name)
        self.assertTrue(self.page.vm_cloud_expanded(self.group_name, cloud_name))
        self.page.click_vms_cloud_expand(cloud_name)

    def test_web_status_plot_open(self):
        # Opens the plot
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.assertTrue(self.page.plot_open())
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_without_target_alias(self):
        # Opens the plot with a jobs box
        self.page.click_job_data_box(self.group_name, 'Jobs')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_total'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_with_target_alias(self):
        self.__setAliasView()
        self.page.click_job_data_box(self.group_name, 'Jobs', self.alias)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.alias + ' jobs'))
        self.page.click_close_plot()
        # reset back to origin
        self.__setAliasView()

    def test_web_status_plot_open_jobs_idle_without_target_alias(self):
        # Opens the plot with an idle jobs box
        self.page.click_job_data_box(self.group_name, 'Idle')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_idle_total'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_idle_with_target_alias(self):
        self.__setAliasView()
        self.page.click_job_data_box(self.group_name, 'Idle', self.alias)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.alias + ' jobs_idle'))
        self.page.click_close_plot()
        self.__setAliasView()

    def test_web_status_plot_open_jobs_running_without_target_alias(self):
        # Opens the plot with a running jobs box
        self.page.click_job_data_box(self.group_name, 'Running')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_running_total'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_running_with_target_alias(self):
        self.__setAliasView()
        self.page.click_job_data_box(self.group_name, 'Running', self.alias)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.alias + ' jobs_running'))
        self.page.click_close_plot()
        self.__setAliasView()

    def test_web_status_plot_open_jobs_completed_without_target_alias(self):
        # Opens the plot with a completed jobs box
        self.page.click_job_data_box(self.group_name, 'Completed')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_completed_total'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_completed_with_target_alias(self):
        self.__setAliasView()
        self.page.click_job_data_box(self.group_name, 'Completed', self.alias)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.alias + ' jobs_completed'))
        self.page.click_close_plot()
        self.__setAliasView()

    def test_web_status_plot_open_jobs_held_without_target_alias(self):
        # Opens the plot with a held jobs box
        self.page.click_job_data_box(self.group_name, 'Held')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_held_total'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_held_with_target_alias(self):
        self.__setAliasView()
        self.page.click_job_data_box(self.group_name, 'Held', self.alias)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.alias + ' jobs_held'))
        self.page.click_close_plot()
        self.__setAliasView()

    def test_web_status_plot_open_jobs_other_without_target_alias(self):
        # Opens the plot with an other jobs box
        self.page.click_job_data_box(self.group_name, 'Other')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_other_total'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_other_with_target_alias(self):
        self.__setAliasView()
        self.page.click_job_data_box(self.group_name, 'Other', self.alias)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.alias + ' jobs_other'))
        self.page.click_close_plot()
        self.__setAliasView()

    def test_web_status_plot_open_jobs_foreign_without_target_alias(self):
        # Opens the plot with a foreign jobs box
        self.page.click_job_data_box(self.group_name, 'Foreign')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' jobs_foreign_total'))
        self.page.click_close_plot()

    def test_web_status_plot_open_jobs_foreign_with_target_alias(self):
        self.__setAliasView()
        self.page.click_job_data_box(self.group_name, 'Foreign', self.alias)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.alias + ' jobs_foreign'))
        self.page.click_close_plot()
        self.__setAliasView()

    def test_web_status_plot_open_rt(self):
        # Opens the plot with an RT box
        self.page.click_rt_data_box(self.group_name, self.cloud_name)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' communication_rt'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms(self):
        # Opens the plot with a VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_starting(self):
        # Opens the plot with a starting VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Starting')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_starting'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_unregistered(self):
        # Opens the plot with an unregistered VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Unregistered')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_unregistered'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_idle(self):
        # Opens the plot with an idle VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Idle')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_idle'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_running(self):
        # Opens the plot with a running VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Running')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_running'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_retiring(self):
        # Opens the plot with a retiring VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Retiring')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_retiring'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_manual(self):
        # Opens the plot with a manual VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Manual')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_manual'))
        self.page.click_close_plot()

    def test_web_status_plot_open_vms_error(self):
        # Opens the plot with an in-error VMs box
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Error')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_in_error'))
        self.page.click_close_plot()

    def test_web_status_plot_open_slots(self):
        # Opens the plot with a slots box
        self.page.click_slot_data_box(self.group_name, self.cloud_name, 'Slots')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' slot_count'))
        self.page.click_close_plot()

    def test_web_status_plot_open_slot_cores_busy(self):
        # Opens the plot with a busy slot cores box
        self.page.click_slot_data_box(self.group_name, self.cloud_name, 'Busy')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' slot_core_count'))
        self.page.click_close_plot()

    def test_web_status_plot_open_slot_cores_idle(self):
        # Opens the plot with an idle slot cores box
        self.page.click_slot_data_box(self.group_name, self.cloud_name, 'Idle')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' slot_idle_core_count'))
        self.page.click_close_plot()

    def test_web_status_plot_open_native_cores_used(self):
        # Opens the plot with a native cores used box
        self.page.click_native_cores_data_box(self.group_name, self.cloud_name, 'Used')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' cores_native'))
        self.page.click_close_plot()

    def test_web_status_plot_open_native_cores_limit(self):
        # Opens the plot with a native cores limit box
        self.page.click_native_cores_data_box(self.group_name, self.cloud_name, 'Limit')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' cores_limit'))
        self.page.click_close_plot()

    def test_web_status_plot_open_ram(self):
        # Opens the plot with a RAM box
        self.page.click_ram_data_box(self.group_name, self.cloud_name)
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' ram_native'))
        self.page.click_close_plot()

    def test_web_status_plot_open_foreign_vms(self):
        # Opens the plot with a foreign VMs box
        self.page.click_foreign_data_box(self.group_name, self.cloud_name, 'VMs')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' Foreign_VMs'))
        self.page.click_close_plot()

    def test_web_status_plot_open_foreign_cores(self):
        # Opens the plot with a foreign cores box
        self.page.click_foreign_data_box(self.group_name, self.cloud_name, 'Cores')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' cores_foreign'))
        self.page.click_close_plot()

    def test_web_status_plot_open_foreign_ram(self):
        # Opens the plot with a foreign RAM box
        self.page.click_foreign_data_box(self.group_name, self.cloud_name, 'RAM')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' ram_foreign'))
        self.page.click_close_plot()

    def test_web_status_plot_open_global_vms(self):
        # Opens the plot with a global VMs box
        self.page.click_global_data_box(self.group_name, self.cloud_name, 'VMs')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' VMs_native_foreign'))
        self.page.click_close_plot()

    def test_web_status_plot_open_global_cores(self):
        # Opens the plot with a global cores box
        self.page.click_global_data_box(self.group_name, self.cloud_name, 'Cores')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' cores_native_foreign'))
        self.page.click_close_plot()

    def test_web_status_plot_open_global_ram(self):
        # Opens the plot with a global RAM box
        self.page.click_global_data_box(self.group_name, self.cloud_name, 'RAM')
        self.assertTrue(self.page.plot_open())
        self.assertTrue(self.page.plot_has_legend(self.group_name + ' ' + self.cloud_name + ' ram_native_foreign'))
        self.page.click_close_plot()

    def test_web_status_plot_open_main(self):
        # Opens the plot for the main poller
        if self.user_type == 'regular':
            pass
        else:
            self.page.click_bottom_icon('main')
            self.assertTrue(self.page.plot_open())
            self.assertTrue(self.page.plot_has_legend('main'))
            self.page.click_close_plot()

    def test_web_status_plot_open_signals(self):
        # Opens the plot for the signal poller
        if self.user_type == 'regular':
            pass
        else:
            self.page.click_bottom_icon('signals')
            self.assertTrue(self.page.plot_open())
            self.assertTrue(self.page.plot_has_legend('signals'))
            self.page.click_close_plot()

    def test_web_status_plot_open_timeseries(self):
        # Opens the plot for the timeseries poller
        if self.user_type == 'regular':
            pass
        else:
            self.page.click_bottom_icon('timeseries')
            self.assertTrue(self.page.plot_open())
            self.assertTrue(self.page.plot_has_legend('timeseries'))
            self.page.click_close_plot()

    def test_web_status_plot_open_vmdata(self):
        # Opens the plot for the VM data poller
        if self.user_type == 'regular':
            pass
        else:
            self.page.click_bottom_icon('VMdata')
            self.assertTrue(self.page.plot_open())
            self.assertTrue(self.page.plot_has_legend('VMdata'))
            self.page.click_close_plot()

    def test_web_status_plot_open_watch(self):
        # Opens the plot for the open watch poller
        if self.user_type == 'regular':
            pass
        else:
            self.page.click_bottom_icon('watch')
            self.assertTrue(self.page.plot_open())
            self.assertTrue(self.page.plot_has_legend('watch'))
            self.page.click_close_plot()

    @unittest.skip("Ec2 status icon was removed")
    def test_web_status_plot_open_ec_two(self):
        # Opens the plot for the ec2 poller
        if self.user_type == 'regular':
            pass
        else:
            self.page.click_bottom_icon('ec2')
            self.assertTrue(self.page.plot_open())
            self.assertTrue(self.page.plot_has_legend('ec2'))
            self.page.click_close_plot()

    def test_web_status_plot_open_openstack(self):
        # Opens the plot for the openstack poller
        if self.user_type == 'regular':
            pass
        else:
            self.page.click_bottom_icon('openstack')
            self.assertTrue(self.page.plot_open())
            self.assertTrue(self.page.plot_has_legend('openstack'))
            self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_one(self):
        # Sets the plot's time range to the last hour
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 1 hour')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(1, 'hours', 10))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_minutes_five(self):
        # Sets the plot's time range to the last five minutes
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 5 minutes')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(5, 'minutes', 0.5))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_minutes_fifteen(self):
        # Sets the plot's time range to the last fifteen minutes
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 15 minutes')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(15, 'minutes', 2))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_minutes_thirty(self):
        # Sets the plot's time range to the last thirty minutes
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 30 minutes')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(30, 'minutes', 5))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_three(self):
        # Sets the plot's time range to the last three hours
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 3 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(3, 'hours', 30))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_six(self):
        # Sets the plot's time range to the last six hours
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 6 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(6, 'hours', 60))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_twelve(self):
        # Sets the plot's time range to the last twelve hours
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 12 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(12, 'hours', 120))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_hours_twenty_four(self):
        # Sets the plot's time range to the last twenty-four hours
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 24 hours')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(24, 'hours', 180))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_seven(self):
        # Sets the plot's time range to the last seven days
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 7 days')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(7, 'days', 24))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_thirty(self):
        # Sets the plot's time range to the last thirty days
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 30 days')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(30, 'days', 168))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_sixty(self):
        # Sets the plot's time range to the last sixty days
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 60 days')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(60, 'days', 168))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_days_ninety(self):
        # Sets the plot's time range to the last ninety days
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 90 days')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(90, 'days', 336))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_months_six(self):
        # Sets the plot's time range to the last six months
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 6 months')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(6, 'months', 31))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_years_one(self):
        # Sets the plot's tiime range to the last year
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 1 year')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(1, 'years', 62))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_years_two(self):
        # Sets the plot's time range to the last two years
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 2 years')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(2, 'years', 93))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_years_five(self):
        # Sets the plot's time range to the last five years
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Last 5 years')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(5, 'years', 186))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_previous_day(self):
        # Sets the plot's time range to the previous day
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Yesterday')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(2, 'days', 3))
        self.assertTrue(self.page.last_time_on_plot_before_now_within(1, 'days', 3))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_day_before_yesterday(self):
        # Sets the plot's time range to the day before yesterday
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Day before yesterday')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(3, 'days', 3))
        self.assertTrue(self.page.last_time_on_plot_before_now_within(2, 'days', 3))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_day_last_week(self):
        # Sets the plot's time range to this day last week
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('This day last week')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(193, 'hours', 180))
        self.assertTrue(self.page.last_time_on_plot_before_now_within(7, 'days', 3))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_previous_week(self):
        # Sets the plot's time range to the week before
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Previous week')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(14, 'days', 24))
        self.assertTrue(self.page.last_time_on_plot_before_now_within(7, 'days', 24))
        self.page.click_close_plot()

    '''
    def test_web_status_plot_open_time_previous_month(self):
        # Sets the plot's time range to the month before
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Previous month')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(2, 'months', 7))
        self.assertTrue(self.page.last_time_on_plot_before_now_within(1, 'months', 7))
        self.page.click_close_plot()

    def test_web_status_plot_open_time_previous_year(self):
        # Sets the plot's time range to the year before
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        self.page.select_plot_range('Previous year')
        self.assertTrue(self.page.first_time_on_plot_before_now_within(2, 'years', 62))
        self.assertTrue(self.page.last_time_on_plot_before_now_within(1, 'years', 62))
        self.page.click_close_plot()

    def test_web_status_plot_hide_line(self):
        # Hides the line in the plot graph
        print("in test_web_status_plot_hide_line function")
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs')
        print("click_vm_data_box good")
        self.page.click_plot_legend_item(self.group_name + ' ' + self.cloud_name + ' VMs')
        print("click_plot_legend_item good")
        self.assertFalse(self.page.plot_has_line())
        print("plot_has_line is True")
        self.page.click_close_plot()
        print("test_web_status_plot_hide_line done")

    '''
    def test_web_status_vm_overlay_open(self):
        # Clicks on the vm overlay
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.assertTrue(self.page.vm_overlay_open())
        self.page.click_vm_overlay_close()

    def test_web_status_vm_overlay_zero_vms(self):
        # Clicks on the vm overlay
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'Error', right_click=True)
        self.assertFalse(self.page.vm_overlay_open())

    def test_web_status_vm_overlay_select(self):
        # Clicks on the vm overlay and selects a vm
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_checkbox(1)
        self.assertTrue(self.page.vm_selected(1))
        self.page.click_vm_overlay_close()

    def test_web_status_vm_overlay_manual(self):
        # Clicks on the vm overlay and sets a vm to manual control
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_checkbox(1)
        self.page.click_vm_operation_button('Manual Control')
        self.page.click_vm_overlay_close()
        self.page.get_homepage()
        self.assertGreater(self.page.vms_in_state(self.group_name, self.cloud_name, 'Manual'), 0)

    def test_web_status_vm_overlay_system(self):
        # Clicks on the vm overlay and sets a vm to system control
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_checkbox(1)
        self.page.click_vm_operation_button('Manual Control')
        self.page.click_vm_overlay_close()
        self.page.get_homepage()
        manual_control = self.page.vms_in_state(self.group_name, self.cloud_name, 'Manual')
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_checkbox(1)
        self.page.click_vm_operation_button('System Control')
        self.page.click_vm_overlay_close()
        self.page.get_homepage()
        self.assertLess(self.page.vms_in_state(self.group_name, self.cloud_name, 'Manual'), manual_control)

    def test_web_status_vm_overlay_retire(self):
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_checkbox(2)
        self.page.click_vm_operation_button('Retire VMs')
        self.page.click_vm_overlay_close()
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.assertFalse(self.page.vm_overlay_column_is(2, 'Retire', 0) and self.page.vm_overlay_column_is(2, 'Terminate', 0))
        self.page.click_vm_overlay_close()
        self.page.get_homepage()
        #self.assertGreater(self.page.vms_in_state(self.group_name, self.cloud_name, 'Retiring'), 0)

    def test_web_status_vm_overlay_kill(self):
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        vms = self.page.vms_in_state(self.group_name, self.cloud_name, 'VMs')
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_checkbox(3)
        self.page.click_vm_operation_button('Kill VMs')
        self.page.click_vm_overlay_close()
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.assertFalse(self.page.vm_overlay_column_is(3, 'Terminate', 0))
        self.page.click_vm_overlay_close()

    def test_web_status_vm_overlay_filter_cores(self):
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_filter_checkbox('2')
        self.page.click_vm_filter_checkbox('4')
        self.page.click_vm_filter_checkbox('8')
        rows = self.page.vm_overlay_rows()
        self.assertNotEqual(rows, 0)
        for i in range(1, rows+1):
            self.assertTrue(self.page.vm_overlay_column_is(i, 'Cores', 1))

    def test_web_status_vm_overlay_filter_cores_none(self):
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_filter_checkbox('1')
        self.assertEqual(self.page.vm_overlay_rows(), 0)
        self.page.click_vm_overlay_close()

    def test_web_status_vm_overlay_filter_state(self):
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_filter_checkbox('Starting')
        self.page.click_vm_filter_checkbox('Idle')
        self.page.click_vm_filter_checkbox('Running')
        self.page.click_vm_filter_checkbox('Retiring')
        self.page.click_vm_filter_checkbox('Manual')
        self.page.click_vm_filter_checkbox('Error')
        rows = self.page.vm_overlay_rows()
        self.assertNotEqual(rows, 0)
        for i in range(1, rows+1):
            self.assertTrue(self.page.vm_overlay_column_is(i, 'Poller Status', 'unregistered'))
        self.page.click_vm_overlay_close()

    def test_web_status_vm_overlay_filter_state_none(self):
        self.page.wait_until_vms_not_zero(self.group_name, self.cloud_name, 3)
        self.page.click_vm_data_box(self.group_name, self.cloud_name, 'VMs', right_click=True)
        self.page.click_vm_filter_checkbox('Starting')
        self.page.click_vm_filter_checkbox('Unregistered')
        self.page.click_vm_filter_checkbox('Idle')
        self.page.click_vm_filter_checkbox('Running')
        self.page.click_vm_filter_checkbox('Retiring')
        self.page.click_vm_filter_checkbox('Manual')
        self.assertEqual(self.page.vm_overlay_rows(), 0)
        self.page.click_vm_overlay_close()
    '''
    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebStatusSuperUserFirefox(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Firefox, with a super user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['servers', 'status', 'jobs'], browser='firefox')
            super(TestWebStatusSuperUserFirefox, cls).setUpClass()
            print("\nStatus Tests (Super User):")
        except:
            print("Error in test setup")
            super(TestWebStatusSuperUserFirefox, cls).tearDownClass()
            raise
   
class TestWebStatusRegularUserFirefox(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Firefox, with a regular user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['servers', 'status', 'jobs'], browser='firefox')
            super(TestWebStatusRegularUserFirefox, cls).setUpClass(user_type='regular')
            print("\nStatus Tests (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebStatusRegularUserFirefox, cls).tearDownClass()
            raise

class TestWebStatusSuperUserChromium(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Chromium, with a super user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['servers', 'status', 'jobs'], browser='chromium')
            super(TestWebStatusSuperUserChromium, cls).setUpClass()
            print("\nStatus Tests (Chromium) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebStatusSuperUserChromium, cls).tearDownClass()
            raise
   
class TestWebStatusRegularUserChromium(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Chromium, with a regular user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['servers', 'status', 'jobs'], browser='chromium')
            super(TestWebStatusRegularUserChromium, cls).setUpClass(user_type='regular')
            print("\nStatus Tests (Chromium) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebStatusRegularUserChromium, cls).tearDownClass()
            raise

class TestWebStatusSuperUserOpera(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Opera, with a super user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['servers', 'status', 'jobs'], browser='opera')
            super(TestWebStatusSuperUserOpera, cls).setUpClass()
            print("\nStatus Tests (Opera) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebStatusSuperUserOpera, cls).tearDownClass()
            raise
   
class TestWebStatusRegularUserOpera(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Opera, with a regular user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['servers', 'status', 'jobs'], browser='opera')
            super(TestWebStatusRegularUserOpera, cls).setUpClass(user_type='regular')
            print("\nStatus Tests (Opera) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebStatusRegularUserOpera, cls).tearDownClass()
            raise

class TestWebStatusSuperUserChrome(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Chrome, with a super user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['servers', 'status', 'jobs'], browser='chrome')
            super(TestWebStatusSuperUserChrome, cls).setUpClass()
            print("\nStatus Tests (Chrome) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebStatusSuperUserChrome, cls).tearDownClass()
            raise
   
class TestWebStatusRegularUserChrome(TestWebStatusCommon):
    """A class to test status operations via the web interface, in Chrome, with a regular user."""
    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['servers', 'status', 'jobs'], browser='chrome')
            super(TestWebStatusRegularUserChrome, cls).setUpClass(user_type='regular')
            print("\nStatus Tests (Chrome) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebStatusRegularUserChrome, cls).tearDownClass()
            raise

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebStatusSuperUserFirefox, TestWebStatusRegularUserFirefox,
              TestWebStatusSuperUserChromium, TestWebStatusRegularUserChromium,
              TestWebStatusSuperUserOpera, TestWebStatusRegularUserOpera,
              TestWebStatusSuperUserChrome, TestWebStatusRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
