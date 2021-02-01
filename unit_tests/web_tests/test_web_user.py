import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions as wta
import web_tests.web_test_page_objects as pages

class TestWebUser(unittest.TestCase):
    """A class to test user operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2)
        cls.page = pages.UsersPage(cls.driver)
        print("\nUser Tests:")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Users')

    def test_web_user_find(self):
        # Finds the users page
        pass

    def test_web_user_add_with_group(self):
        user_name = self.gvar['user'] + '-wiu4'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_user_name(user_name)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(user_name))
        self.assertTrue(self.page.box_checked(group_name))
        wta.assertAddedWithAttribute('user', user_name, 'user_groups', group_name)

    def test_web_user_add_without_group(self):
        user_name = self.gvar['user'] + '-wiu5'
        self.page.click_add_button()
        self.page.type_user_name(user_name)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(user_name))
        wta.assertAddedWithAttribute('user', user_name, 'user_groups', 'None')

    def test_web_user_add_superuser(self):
        user_name = self.gvar['user'] + '-wiu6'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_user_name(user_name)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_superuser_checkbox()
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(user_name))
        self.assertTrue(self.page.box_checked(group_name))
        wta.assertAddedWithAttribute('user', user_name, 'is_superuser', '1')

    def test_web_user_add_regular_user(self):
        user_name = self.gvar['user'] + '-wiu7'
        group_name = self.gvar['user'] + '-wig3'
        self.page.click_add_button()
        self.page.type_user_name(user_name)
        self.page.type_password(self.gvar['user_secret'])
        self.page.click_group_checkbox(group_name)
        self.page.click_add_user()
        self.assertTrue(self.page.side_button_exists(user_name))
        self.assertTrue(self.page.box_checked(group_name))
        wta.assertAddedWithAttribute('user', user_name, 'is_superuser', '0')

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
