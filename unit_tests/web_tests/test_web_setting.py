import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebSetting(unittest.TestCase):
    """A class to test user settings operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['settings'])
        cls.page = pages.SettingsPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        cls.user = cls.gvar['user'] + '-wiu2'
        print("\nUser Settings Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('User Settings')

    def test_web_setting_find(self):
        pass

    @unittest.skip("Doesn't currently work with Firefox profile setup")
    def test_web_setting_update_password(self):
        # Updates the current user's password
        self.page.click_side_button(self.user)
        self.page.type_password(self.gvar['user'] + '-password')
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())
        wtsc.get_homepage(self.driver)
        alert = driver.switch_to.alert
        alert.accept()
        self.page.click_top_nav('User Settings')
        self.page.type_password(self.gvar['user_secret'])
        wtsc.get_homepage(self.driver)
        alert = driver.switch_to.alert
        alert.accept()

    def test_web_setting_update_global_view_on_status_page(self):
        # Update's the current user's "enabled global view on status page" setting
        self.page.click_side_button(self.user)
        self.page.click_global_view_checkbox()
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_setting_update_jobs_by_target_alias_on_status_page(self):
        # Updates the current user's "enabled jobs by target alias on status page" setting
        self.page.click_side_button(self.user)
        self.page.click_jobs_by_alias_checkbox()
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_setting_update_foreign_global_vm_on_status_page(self):
        # Updates the current user's "enabled foreign/global VM information on status page" setting
        self.page.click_side_button(self.user)
        self.page.click_foreign_global_vms_checkbox()
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_setting_update_slot_detail_on_status_page(self):
        # Updates the current user's "enabled slot detail on status page" setting
        self.page.click_side_button(self.user)
        self.page.click_slot_detail_checkbox()
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_setting_update_slot_flavor_info_on_status_page(self):
        # Updates the current user's "enabled slot flavor info on status page" setting
        self.page.click_side_button(self.user)
        self.page.click_slot_flavor_info_checkbox()
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_setting_update_status_refresh_interval_by_blank(self):
        # Updates the current user's status page refresh interval by typing it in the blank
        self.page.click_side_button(self.user)
        self.page.type_status_refresh('20')
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_setting_update_status_refresh_interval_by_arrow_keys(self):
        # Updates the current user's status page refresh interval using the arrow keys
        self.page.click_side_button(self.user)
        self.page.increment_status_refresh_by_arrows(40)
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    def test_web_setting_update_default_group(self):
        # Updates the current user's default group
        self.page.click_side_button(self.user)
        self.page.select_default_group(self.gvar['user'] + '-wig2')
        self.page.click_update_user()
        self.assertFalse(self.page.error_message_displayed())

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
