import unittest
import sys
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
import web_tests.web_test_helpers as helpers

class TestWebCloudCommon(unittest.TestCase):
    """A class for the cloud tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.credentials = cls.gvar['cloud_credentials']
        cls.page = pages.CloudsPage(cls.driver)
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        helpers.get_homepage(self.driver)
        self.page.click_top_nav('Clouds')

    def test_web_cloud_add(self):
        # Adds a standard cloud
        cloud_name = self.gvar['user'] + '-wic3'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.side_button_exists(cloud_name))
        wta.assertExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_not_enabled(self):
        # Adds a cloud that is not enabled
        cloud_name = self.gvar['user'] + '-wic4'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.side_button_exists(cloud_name))
        wta.assertHasAttribute('cloud', cloud_name, 'enabled', '0', group=self.gvar['base_group'])

    def test_web_cloud_add_different_priority(self):
        # Adds a cloud with a non-default priority
        cloud_name = self.gvar['user'] + '-wic5'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('10')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.side_button_exists(cloud_name))
        wta.assertHasAttribute('cloud', cloud_name, 'cloud_priority', '10', group=self.gvar['base_group'])

    def test_web_cloud_add_without_name(self):
        # Tries to add a cloud without naming it
        cloud_name = self.gvar['user'] + '-wic3'
        self.page.click_add_button()
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_cloud_add_with_conflicting_name(self):
        # Tries to add a cloud with a name that's already being used
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasAttribute('cloud', cloud_name, 'enabled', '1', group=self.gvar['base_group'])

    def test_web_cloud_add_name_with_symbols(self):
        # Tries to add a cloud with symbols in its name
        cloud_name = 'inv@|id-web-te$t'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.type_cloud_name(cloud_name)
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_name_with_two_dashes(self):
        # Tries to add a cloud with two dashes in its name
        cloud_name = 'invalid--web--test'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_name_with_uppercase(self):
        # Tries to add a cloud with uppercase letters in its name
        cloud_name = 'INVALID-WEB-TEST'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_name_with_starting_ending_dash(self):
        # Tries to add a cloud with starting and ending dashes in its name
        cloud_name = '-invalid-web-test-'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.type_cloud_name(cloud_name)
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_name_too_long(self):
        # Tries to add a cloud with a name that's too long for the database
        cloud_name = self.oversize['varchar_32']
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.type_cloud_name(cloud_name)
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_priority_float(self):
        # Tries to add a cloud with a float value for priority
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('1.5')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_priority_string(self):
        # Tries to add a cloud with a string value for priority
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('invalid-web-test')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_priority_too_big(self):
        # Tries to add a cloud with a priority that's too big for the database
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority(str(self.oversize['int_11']))
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_without_url(self):
        # Tries to add a cloud without an authurl
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_url_too_long(self):
        # Tries to add a cloud with an authurl that's too long for the database
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.oversize['varchar_128'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_without_region(self):
        # Tries to add a cloud without a region
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_region_too_long(self):
        # Tries to add a cloud with a region that's too long for the database
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.oversize['varchar_32'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_project_too_long(self):
        # Tries to add a cloud with a project that's too long for the database
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.oversize['varchar_128'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_without_username(self):
        # Tries to add a cloud without a username
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_username_too_long(self):
        # Tries to add a cloud with a username that's too long for the database
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.oversize['varchar_20'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_without_password(self):
        # Tries to add a cloud without a password
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_without_user_domain_name(self):
        # Tries to add a cloud without a user domain name
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_user_domain_name_too_long(self):
        # Tries to add a cloud with a user domain name that's too long for the database
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name(self.oversize['varchar_20'])
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_without_project_domain_name(self):
        # Tries to add a cloud without a project domain name
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_add_project_domain_name_too_long(self):
        # Tries to add a cloud with a project domain name that's too long for the database
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name(self.oversize['varchar_20'])
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_find(self):
        # Finds the clouds page
        pass

    def test_web_cloud_find_settings(self):
        # Clicks on a cloud's Settings tab
        self.page.click_side_button(self.gvar['user'] + '-wic1')
        self.page.click_side_tab('Settings')

    def test_web_cloud_find_metadata(self):
        # Clicks on a cloud's Metadata tab
        self.page.click_side_button(self.gvar['user'] + '-wic1')
        self.page.click_side_tab('Metadata')

    def test_web_cloud_find_exclusions(self):
        # Clicks on a cloud's Exclusions tab
        self.page.click_side_button(self.gvar['user'] + '-wic1')
        self.page.click_side_tab('Exclusions')

    def test_web_cloud_update_enabled_status(self):
        # Disables an enabled cloud
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.click_update_cloud()
        self.assertFalse(self.page.enabled_box_checked())
        wta.assertHasAttribute('cloud', cloud_name, 'enabled', '0', group=self.gvar['base_group'])

    def test_web_cloud_update_priority(self):
        # Changes a cloud's priority
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_priority('15')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cloud_priority', '15', group=self.gvar['base_group'])

    def test_web_cloud_update_priority_float(self):
        # Tries to change a cloud's priority to a float
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_priority('3.5')
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cloud_priority', '3.5', group=self.gvar['base_group'])

    def test_web_cloud_update_priority_string(self):
        # Tries to change a cloud's priority to a string
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_priority('invalid-web-test')
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cloud_priority', '3.5', group=self.gvar['base_group'])

    def test_web_cloud_update_priority_too_big(self):
        # Tries to change a cloud's priority to an int that's too big for the database
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_priority(str(self.oversize['int_11']))
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cloud_priority', str(self.oversize['int_11']), group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume(self):
        # Changes a cloud's boot volume
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{"GBs": 10, "GBs_per_core": 5}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_invalid_string(self):
        # Tries to change a cloud's boot volume to an invalid string
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = 'invalid-web-test'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_empty_keypair(self):
        # Tries to change a cloud's boot volume to an invalid string
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_invalid_keypair(self):
        # Tries to change a cloud's boot volume to one with an invalid keypair
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{"invalid-web-test": 5}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_gbs_float(self):
        # Tries to change a cloud's boot volume to one with a float value for GBs
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{"GBs": 3.5}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_gbs_string(self):
        # Tries to change a cloud's boot volume to one with a string value for GBs
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{"GBs": "invalid-web-test"}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_gbs_per_core_float(self):
        # Tries to change a cloud's boot volume to one with a float value for GBs_per_core
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{"GBs_per_core": 3.5}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_gbs_per_core_string(self):
        # Tries to change a cloud's boot volume to one with a string value for GBs_per_core
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{"GBs_per_core": "invalid-web-test"}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_boot_volume_too_long(self):
        # Tries to change a cloud's boot volume to one that's too long for the database
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = self.oversize['varchar_64']
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, group=self.gvar['base_group'])

    def test_web_cloud_update_add_security_group(self):
        # Adds a cloud to a security group
        cloud_name = self.gvar['user'] + '-wic1'
        security_group = 'csv2-sa'
        self.page.click_side_button(cloud_name)
        self.page.add_security_group(security_group)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_security_groups', security_group, group=self.gvar['base_group'])

    @unittest.skip("Not working in production")
    def test_web_cloud_update_remove_security_group(self):
        # Removes a cloud from a security group
        cloud_name = self.gvar['user'] + '-wic1'
        security_group = 'default'
        self.page.click_side_button(cloud_name)
        self.page.remove_security_group(security_group)
        self.page.click_update_cloud()
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_security_groups', security_group, group=self.gvar['base_group'])

    def test_web_cloud_update_vm_keyname(self):
        # Changes a cloud's vm keyname
        cloud_name = self.gvar['user'] + '-wic1'
        key = self.gvar['user'] + '-wik1'
        self.page.click_side_button(cloud_name)
        self.page.select_vm_keyname(key)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_keyname', key, group=self.gvar['base_group'])

    def test_web_cloud_update_vm_network(self):
        # Changes a cloud's vm network
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.select_vm_network('private')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_network', 'private', group=self.gvar['base_group'])

    def test_web_cloud_update_vm_image(self):
        # Changes a cloud's vm image
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.select_vm_image('cirros-0.3.5')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_image', 'cirros-0.3.5', group=self.gvar['base_group'])

    def test_web_cloud_update_vm_flavor(self):
        # Changes a cloud's vm flavor
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.select_vm_flavor('s8')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_flavor', 's8', group=self.gvar['base_group'])

    def test_web_cloud_update_vm_keep_alive(self):
        # Changes a cloud's vm keep alive time
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_vm_keep_alive('300')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_keep_alive', '300', group=self.gvar['base_group'])

    def test_web_cloud_update_vm_keep_alive_float(self):
        # Tries to change a cloud's vm keep alive time to a float
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_vm_keep_alive('3.5')
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_keep_alive', '3.5', group=self.gvar['base_group'])

    def test_web_cloud_update_vm_keep_alive_string(self):
        # Tries to change a cloud's vm keep alive time to a string
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_vm_keep_alive('invalid-web-test')
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_keep_alive', 'invalid-web-test', group=self.gvar['base_group'])

    def test_web_cloud_update_vm_keep_alive_too_big(self):
        # Tries to change a cloud's vm keep alive time to an int that's too big for the database
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_vm_keep_alive(str(self.oversize['int_11']))
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_keep_alive', str(self.oversize['int_11']), group=self.gvar['base_group'])

    @unittest.skip("Needs Amazon cloud")
    def test_web_cloud_update_spot_price(self):
        # Changes a cloud's spot price
        pass

    @unittest.skip("Needs Amazon cloud")
    def test_web_cloud_update_spot_price_string(self):
        # Tries to change a cloud's spot price to a string
        pass

    def test_web_cloud_update_cores_softmax(self):
        # Changes a cloud's core softmax
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores_softmax('4')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cores_softmax', '4', group=self.gvar['base_group'])

    def test_web_cloud_update_cores_softmax_float(self):
        # Tries to change a cloud's core softmax to a float
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores_softmax('3.5')
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cores_softmax', '3.5', group=self.gvar['base_group'])

    def test_web_cloud_update_cores_softmax_string(self):
        # Tries to change a cloud's core softmax to a string
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores_softmax('invalid-web-test')
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cores_softmax', 'invalid-web-test', group=self.gvar['base_group'])

    def test_web_cloud_update_cores_softmax_too_big(self):
        # Tries to change a cloud's core softmax to an int that's too big for the database
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores_softmax(str(self.oversize['int_11']))
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cores_softmax', str(self.oversize['int_11']), group=self.gvar['base_group'])

    def test_web_cloud_update_cores_by_blank(self):
        # Changes a cloud's maximum number of cores by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores('4')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cores_ctl', '4', group=self.gvar['base_group'])

    def test_web_cloud_update_cores_by_blank_float(self):
        # Tries to change a cloud's maximum number of cores to a float by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores('3.5')
        self.page.click_update_cloud()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.cores_popup_exists())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cores_ctl', '3.5', group=self.gvar['base_group'])

    def test_web_cloud_update_cores_by_blank_string(self):
        # Tries to change a cloud's maximum number of cores to a string by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores('invalid-web-test')
        self.page.click_update_cloud()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.cores_popup_exists())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cores_ctl', 'invalid-web-test', group=self.gvar['base_group'])

    def test_web_cloud_update_cores_by_blank_too_big(self):
        # Tries to change a cloud's maximum number of cores to an int that's too big for the database by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores(str(self.oversize['int_11']))
        self.page.click_update_cloud()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.cores_popup_exists())
        wta.assertHasNotAttribute('cloud', cloud_name, 'cores_ctl', str(self.oversize['int_11']), group=self.gvar['base_group'])

    def test_web_cloud_update_cores_by_slider(self):
        # Changes a cloud's maximum number of cores by sliding the slider
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.slide_cores_slider(128)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cores_ctl', '128', group=self.gvar['base_group'], err=16)

    def test_web_cloud_update_cores_by_arrows(self):
        # Changes a cloud's maximum number of cores using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.increment_cores_by_arrows(16)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cores_ctl', '16', group=self.gvar['base_group'])

    @unittest.skip("Probably too slow to be worth running")
    def test_web_cloud_update_cores_by_arrows_too_big(self):
        # Tries to change a cloud's maximum number of cores to an int that's too big for the database using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.increment_cores_by_arrows(self.oversize['int_11'])
        self.page.click_update_cloud()
        wta.assertHasNotAttribute('cloud', cloud_name, 'cores_ctl', str(self.oversize['int_11']), group=self.gvar['base_group'])

    def test_web_cloud_update_ram_by_blank(self):
        # Changes a cloud's maximum RAM by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_ram('65536')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'ram_ctl', '65536', group=self.gvar['base_group'])

    def test_web_cloud_update_ram_by_blank_float(self):
        # Tries to change a cloud's maximum RAM to a float by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_ram('3.5')
        self.page.click_update_cloud()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.ram_popup_exists())
        wta.assertHasNotAttribute('cloud', cloud_name, 'ram_ctl', '3.5', group=self.gvar['base_group'])

    def test_web_cloud_update_ram_by_blank_string(self):
        # Tries to change a cloud's maximum RAM to a string by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_ram('invalid-web-test')
        self.page.click_update_cloud()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.ram_popup_exists())
        wta.assertHasNotAttribute('cloud', cloud_name, 'ram_ctl', 'invalid-web-test', group=self.gvar['base_group'])

    def test_web_cloud_update_ram_by_blank_too_big(self):
        # Tries to change a cloud's maximum RAM to an int that's too big for the database by typing it into the blank
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.type_ram(str(self.oversize['int_11']))
        self.page.click_update_cloud()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.ram_popup_exists())
        wta.assertHasNotAttribute('cloud', cloud_name, 'ram_ctl', str(self.oversize['int_11']), group=self.gvar['base_group'])

    def test_web_cloud_update_ram_by_slider(self):
        # Changes a cloud's maximum RAM by sliding the slider
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.slide_ram_slider(262144)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'ram_ctl', '262144', group=self.gvar['base_group'], err=48000)

    def test_web_cloud_update_ram_by_arrows(self):
        # Changes a cloud's maximum RAM using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.increment_ram_by_arrows(4096)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'ram_ctl', '4096', group=self.gvar['base_group'])

    @unittest.skip("Probably too slow to be worth running")
    def test_web_cloud_update_ram_by_arrows(self):
        # Tries to change a cloud's maximum RAM to an int that's too big for the database using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.increment_ram_by_arrows(self.oversize['int_11'])
        self.page.click_update_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'ram_ctl', str(self.oversize['int_11']), group=self.gvar['base_group'])

    def test_web_cloud_delete(self):
        # Deletes a cloud
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(cloud_name)
        self.page.click_delete_button()
        self.page.click_delete_modal()
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertNotExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_delete_cancel(self):
        # Tries to delete a cloud but cancels the modal
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.click_delete_button()
        self.page.click_delete_cancel()
        self.assertTrue(self.page.side_button_exists(cloud_name))
        wta.assertExists('cloud', cloud_name, group=self.gvar['base_group'])

    def test_web_cloud_metadata_add(self):
        # Adds metadata to a cloud
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim3.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_add_without_name(self):
        # Tries to add metadata to a cloud without a name
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.click_metadata_new()
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_add_name_with_symbols(self):
        # Tries to add metadata with symbols in its name
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = 'inv@|id-web-te$t.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_add_name_with_two_dashes(self):
        # Tries to add metadata with two dashes in its name
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = 'invalid--web--test.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_add_name_with_uppercase(self):
        # Tries to add metadata with uppercase letters in its name
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = 'INVALID-WEB-TEST.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_add_name_with_starting_ending_dash(self):
        # Tries to add metadata with starting and ending dashes in its name
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = '-invalid-web-test-.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_add_name_too_long(self):
        # Tries to add metadata with a name that's too long for the database
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.oversize['varchar_64']
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    def test_web_cloud_metadata_add_not_enabled(self):
        # Adds metadata to a cloud without enabling it
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim4.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_enabled()
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'enabled', '0', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_add_different_priority_by_typing(self):
        # Adds metadata to a cloud with a different priority by typing it in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim5.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata_priority('8')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '8', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_add_different_priority_by_typing_float(self):
        # Tries to add metadata to a cloud with a float value for its priority by typing it in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata_priority('8.5')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    def test_web_cloud_metadata_add_different_priority_by_typing_string(self):
        # Tries to metadata to a cloud with a string value priority by typing it in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata_priority('invalid-web-test')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_add_different_priority_by_typing_too_big(self):
        # Tries to add metadata to a cloud with a priority that's too big for the database by typing it in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata_priority(str(self.oversize['int_11']))
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.metadata_priority_popup_exists())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    def test_web_cloud_metadata_add_different_priority_by_arrows(self):
        # Adds metadata to a cloud with a different priority using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim6.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.increment_metadata_priority_by_arrows(16)
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '16', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    @unittest.skip("Probably too slow to be worth running")
    def test_web_cloud_metadata_add_different_priority_by_arrows_too_big(self):
        # Tries to add metadata to a cloud with a priority that's too big for the database using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.increment_priority_by_arrows(self.oversize['int_11'])
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    def test_web_cloud_metadata_add_different_mime_type(self):
        # Adds metadata to a cloud with a different MIME type
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim7.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.select_metadata_mime_type('ucernvm-config')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'mime_type', 'ucernvm-config', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    @unittest.skip("Not working (supposed to work?)")
    def test_web_cloud_metadata_add_mismatched_file_type(self):
        # Tries to add metadata to a cloud with a file that doesn't match its name
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata('invalid-unit-test')
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    def test_web_cloud_metadata_update_enabled_status(self):
        # Changes enabled metadata to not enabled
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.click_metadata_enabled()
        self.page.click_metadata_update()
        # TODO: implement checkbox clicked check method
        wta.assertHasAttribute('metadata', metadata_name, 'enabled', '0', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_update_priority_by_typing(self):
        # Changes metadata priority by typing in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority('8')
        self.page.click_metadata_update()
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '8', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_update_priority_by_typing_float(self):
        # Tries to change metadata priority to a float by typing it in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority('8.5')
        self.page.click_metadata_update()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', '8.5', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_update_priority_by_typing_string(self):
        # Tries to change metadata priority to a string by typing it in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority('invalid-web-test')
        self.page.click_metadata_update()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', 'invalid-web-test', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    @unittest.skip("Not working in production (issue 319)")
    def test_web_cloud_metadata_update_priority_by_typing_too_big(self):
        # Tries to change metadata priority to an int that's too big for the database by typing it in the blank
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority(str(self.oversize['int_11']))
        #self.assertTrue(self.page.error_message_displayed())
        self.assertTrue(self.page.metadata_priority_popup_exists())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', str(self.oversize['int_11']), group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_update_priority_by_arrow_keys(self):
        # Changes metadata priority using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.increment_metadata_priority_by_arrows(16)
        self.page.click_metadata_update()
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '16', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    @unittest.skip("Probably takes too long to be worth running")
    def test_web_cloud_metadata_update_priority_by_arrow_keys_too_big(self):
        # Tries to change metadata priority to an int that's too big for the database using the arrow keys
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.increment_metadata_priority_by_arrows(self.oversize['int_11'])
        self.page.click_metadata_update()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', str(self.oversize['int_11']), group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_update_mime_type(self):
        # Changes metadata mime type
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.select_metadata_mime_type('ucernvm-config')
        self.page.click_metadata_update()
        wta.assertHasAttribute('metadata', metadata_name, 'mime_type', 'ucernvm-config', group=self.gvar['base_group'], metadata_cloud=cloud_name)

    def test_web_cloud_metadata_update_contents(self):
        # Changes metadata text
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata('sample_key_2: sample_value_2')
        self.page.click_metadata_update()
        # Note: there appears to be no way to test that this has been updated
        self.assertFalse(self.page.error_message_displayed())

    @unittest.skip("Not working (supposed to work?)")
    def test_web_cloud_metadata_update_contents_mismatched(self):
        # Tries to change metadata text to something of the wrong file type
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata('invalid-web-test')
        self.page.click_metadata_update()
        # Note: there appears to be no way to test that this has not been updated
        self.assertTrue(self.page.error_message_displayed())

    def test_web_cloud_metadata_delete(self):
        # Deletes metadata from a cloud
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim2.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.click_metadata_delete()
        self.page.click_metadata_delete_modal()
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasNotAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    def test_web_cloud_metadata_delete_cancel(self):
        # Tries to delete metadata from a cloud but clicks cancel on the delete modal
        cloud_name = self.gvar['user'] + '-wic1'
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.click_metadata_delete()
        self.page.click_metadata_delete_cancel()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('cloud', cloud_name, 'metadata_names', metadata_name, group=self.gvar['base_group'])

    def test_web_cloud_exclusions_metadata(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Exclusions')
        self.page.click_metadata_exclusions()
        self.page.click_metadata_exclusions_checkbox('default.yaml.j2')
        self.page.click_update_metadata_exclusions()
        wta.assertHasAttribute('cloud', cloud_name, 'group_exclusions', 'default.yaml.j2', group=self.gvar['base_group'])

    def test_web_cloud_exclusions_flavor(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.click_side_tab('Exclusions')
        self.page.click_flavor_exclusions()
        self.page.click_flavor_exclusions_checkbox('m1')
        self.page.click_update_flavor_exclusions()
        wta.assertHasAttribute('cloud', cloud_name, 'flavor_exclusions', 'm1', group=self.gvar['base_group'])

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebCloudSuperUserFirefox(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['clouds'], browser='firefox')
        super(TestWebCloudSuperUserFirefox, cls).setUpClass()
        print("\nCloud Tests (Super User):")

class TestWebCloudRegularUserFirefox(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['clouds'], browser='firefox')
        super(TestWebCloudRegularUserFirefox, cls).setUpClass()
        print("\nCloud Tests (Regular User):")

class TestWebCloudSuperUserChromium(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['clouds'], browser='chromium')
        super(TestWebCloudSuperUserChromium, cls).setUpClass()
        print("\nCloud Tests (Chromium) (Super User):")

class TestWebCloudRegularUserChromium(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['clouds'], browser='chromium')
        super(TestWebCloudRegularUserChromium, cls).setUpClass()
        print("\nCloud Tests (Chromium) (Regular User):")

class TestWebCloudSuperUserOpera(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['clouds'], browser='opera')
        super(TestWebCloudSuperUserOpera, cls).setUpClass()
        print("\nCloud Tests (Opera) (Super User):")

class TestWebCloudRegularUserOpera(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['clouds'], browser='opera')
        super(TestWebCloudRegularUserOpera, cls).setUpClass()
        print("\nCloud Tests (Opera) (Regular User):")

class TestWebCloudSuperUserChrome(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['clouds', 'keys'], browser='chrome')
        super(TestWebCloudSuperUserChrome, cls).setUpClass()
        print("\nCloud Tests (Chrome) (Super User):")

class TestWebCloudRegularUserChrome(TestWebCloudCommon):
    """A class to test cloud operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['clouds', 'keys'], browser='chrome')
        super(TestWebCloudRegularUserChrome, cls).setUpClass()
        print("\nCloud Tests (Chrome) (Regular User):")

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebCloudSuperUserFirefox, TestWebCloudRegularUserFirefox,
              TestWebCloudSuperUserChromium, TestWebCloudRegularUserChromium,
              TestWebCloudSuperUserOpera, TestWebCloudRegularUserOpera,
              TestWebCloudSuperUserChrome, TestWebCloudRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
