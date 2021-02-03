import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions as wta
import web_tests.web_test_page_objects as pages

class TestWebCloudSuperUser(unittest.TestCase):
    """A class to test cloud operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['clouds'])
        cls.credentials = cls.gvar['cloud_credentials']
        cls.page = pages.CloudsPage(cls.driver)
        print("\nCloud Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
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
        wta.assertAdded('cloud', cloud_name, self.gvar['base_group'])

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
        wta.assertAddedWithAttribute('cloud', cloud_name, 'enabled', '0', self.gvar['base_group'])

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
        wta.assertAddedWithAttribute('cloud', cloud_name, 'cloud_priority', '10', self.gvar['base_group'])

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
        wta.assertHasAttribute('cloud', cloud_name, 'enabled', '1', self.gvar['base_group'])

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
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

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
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

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
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

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
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

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
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

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
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_find(self):
        # Finds the clouds page
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
