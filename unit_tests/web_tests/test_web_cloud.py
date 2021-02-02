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

    def test_web_cloud_find(self):
        # Finds the clouds page
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
