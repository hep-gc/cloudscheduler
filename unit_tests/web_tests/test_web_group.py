import unittest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import web_tests.web_test_interactions as wti
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions as wta
import web_tests.web_test_page_objects as pages

class TestWebGroup(unittest.TestCase):
    """A class to test group operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls)
        cls.page = pages.GroupsPage(cls.driver)
        print("\nGroup Tests:")
        
    def setUp(self):
        wti.get_homepage(self.driver)
        self.page.click_top_nav('Groups')

    def test_web_group_find(self):
        pass

    def test_web_group_add_without_user(self):
        group_name = self.gvar['user'] + '-wig7'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_add_group()
        self.assertTrue(self.page.side_button_exists(group_name))
        wta.assertAdded('group', group_name)

    def test_web_group_add_checkbox(self):
        group_name = self.gvar['user'] + '-wig5'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.side_button_exists(group_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    @unittest.skip("Not working in production")
    def test_web_group_add_search_bar(self):
        group_name = self.gvar['user'] + '-wig6'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_add_button()
        self.page.type_group_name(group_name)
        self.page.type_in_search_bar(user_name)
        self.page.click_add_group()
        self.assertTrue(self.page.side_button_exists(group_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_delete(self):
        group_name = self.gvar['user'] + '-wig4'
        self.page.click_side_button(group_name)
        self.page.click_delete_button()
        self.page.click_delete_modal()
        with self.assertRaises(TimeoutException):
            self.page.side_button_exists(group_name)
        wta.assertDeleted('group', group_name)

    @unittest.skip("Not working in production")
    def test_web_group_user_add_search_bar(self):
        group_name = self.gvar['user'] + '-wig1'
        user_name = self.gvar['user'] + '-wiu2'
        self.page.click_side_button(group_name)
        self.page.type_in_search_bar(user_name)
        self.page.click_update_group()
        self.assertTrue(self.page.box_checked(user_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_user_add_checkbox(self):
        group_name = self.gvar['user'] + '-wig2'
        user_name = self.gvar['user'] + '-wiu1'
        self.page.click_side_button(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_update_group()
        self.assertTrue(self.page.box_checked(user_name))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_user_remove(self):
        group_name = self.gvar['user'] + '-wig1'
        user_name = self.gvar['user'] + '-wiu1'
        self.page.click_side_button(group_name)
        self.page.click_user_checkbox(user_name)
        self.page.click_update_group()
        with self.assertRaises(TimeoutException):
            self.page.box_checked(user_name)
        wta.assertHasNotAttribute('user', user_name, 'user_groups', group_name) 

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
