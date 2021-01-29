import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import web_tests.web_test_interactions as wti
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_javascript_interactions as wtjsi
import web_tests.web_test_assertions as wta
import web_tests.web_test_xpath_selectors as wtxs

class TestWebGroup(unittest.TestCase):
    """A class to test group operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls)
        print("\nGroup Tests:")
        
    def setUp(self):
        wti.get_homepage(self.driver)
        wti.click_nav_button(self.driver, 'Groups')

    def test_web_group_find(self):
        pass

    def test_web_group_add_without_user(self):
        group_name = self.gvar['user'] + '-wig7'
        wti.click_nav_button(self.driver, '+')
        wti.fill_blank(self.driver, 'new_group', group_name)
        self.driver.find_element_by_id('new_group').submit()
        self.assertTrue(WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, group_name))))
        wta.assertAdded('group', group_name)

    def test_web_group_add_checkbox(self):
        group_name = self.gvar['user'] + '-wig5'
        user_name = self.gvar['user'] + '-wiu2'
        wti.click_nav_button(self.driver, '+')
        wti.fill_blank(self.driver, "new_group", group_name)
        wti.click_by_xpath(self.driver, wtxs.user_checkbox('add_group', user_name))
        self.driver.find_element_by_id("new_group").submit()
        self.assertTrue(WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, group_name))))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    @unittest.skip("Not working in production")
    def test_web_group_add_search_bar(self):
        group_name = self.gvar['user'] + '-wig6'
        user_name = self.gvar['user'] + '-wiu2'
        wti.click_nav_button(self.driver, '+')
        wti.fill_blank(self.driver, "new_group", group_name)
        wti.fill_blank(self.driver, "search-users-", user_name)
        self.driver.find_element_by_id("new_group").submit()
        self.assertTrue(WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, group_name))))
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_delete(self):
        group_name = TestWebGroup.gvar['user'] + '-wig4'
        # JavaScript click is used here because of an issue where Selenium
        # cannot click on an item through the padding of another item.
        wtjsi.javascript_click_nav_button(self.driver, group_name)
        wti.click_nav_button(self.driver, '−')
        wti.click_by_xpath(self.driver, wtxs.delete_button(group_name))
        WebDriverWait(self.driver, 5)
        with self.assertRaises(TimeoutException):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, group_name)))
        wta.assertDeleted('group', group_name)

    @unittest.skip("Not working in production")
    def test_web_group_user_add_search_bar(self):
        group_name = self.gvar['user'] + '-wig1'
        user_name = self.gvar['user'] + '-wiu2'
        wtjsi.javascript_click_nav_button(self.driver, group_name)
        wti.fill_blank(self.driver, 'search-users-' + group_name, user_name)
        self.driver.find_element_by_name(group_name).submit()
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_user_add_checkbox(self):
        group_name = self.gvar['user'] + '-wig2'
        user_name = self.gvar['user'] + '-wiu1'
        wtjsi.javascript_click_nav_button(self.driver, group_name)
        wti.click_by_xpath(self.driver, wtxs.user_checkbox(group_name, user_name))
        self.driver.find_element_by_name(group_name).submit()
        wta.assertHasAttribute('user', user_name, 'user_groups', group_name)

    def test_web_group_user_remove(self):
        group_name = self.gvar['user'] + '-wig1'
        user_name = self.gvar['user'] + '-wiu1'
        wtjsi.javascript_click_nav_button(self.driver, group_name)
        wti.click_by_xpath(self.driver, wtxs.user_checkbox(group_name, user_name))
        self.driver.find_element_by_name(group_name).submit()
        wta.assertHasNotAttribute('user', user_name, 'user_groups', group_name)
        

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
