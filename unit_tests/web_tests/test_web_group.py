import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import web_tests.web_test_interactions as wti
import web_tests.web_test_setup_cleanup as wtsc

class TestWebGroup(unittest.TestCase):
    """A class to test group operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls)
        print("\nGroup Tests:")

    def test_web_group_find(self):
        wti.click_nav_button(TestWebGroup.driver, 'Groups')

    def test_web_group_add_checkbox(self):
        wti.click_nav_button(TestWebGroup.driver, 'Groups')
        wti.click_nav_button(TestWebGroup.driver, '+')
        wti.fill_blank(TestWebGroup.driver, "new_group", TestWebGroup.gvar['user'] + '-wig5')
        self.button = TestWebGroup.driver.find_element_by_class_name("highlight2")
        wti.javascript_click(TestWebGroup.driver, self.button)
        TestWebGroup.driver.find_element_by_id("new_group").submit()
        self.assertTrue(WebDriverWait(TestWebGroup.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, TestWebGroup.gvar['user'] + '-wig5'))))

    def test_web_group_add_search_bar(self):
        wti.click_nav_button(TestWebGroup.driver, 'Groups')
        wti.click_nav_button(TestWebGroup.driver, '+')
        wti.fill_blank(TestWebGroup.driver, "new_group", TestWebGroup.gvar['user'] + '-wig6')
        wti.fill_blank(TestWebGroup.driver, "search-users-", TestWebGroup.gvar['user'] + '-wiu2')
        TestWebGroup.driver.find_element_by_id("new_group").submit()
        self.assertTrue(WebDriverWait(TestWebGroup.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, TestWebGroup.gvar['user'] + '-wig6'))))

    def test_web_group_delete(self):
        group_name = TestWebGroup.gvar['user'] + '-wig4'
        wti.click_nav_button(TestWebGroup.driver, 'Groups')
        wti.click_nav_button(TestWebGroup.driver, group_name)
        wti.click_nav_button(TestWebGroup.driver, '-')
        TestWebGroup.find_element_by_name(group_name).submit()

    def test_web_group_user_add_search_bar(self):
        group_name = TestWebGroup.gvar['user'] + '-wig1'
        wti.click_nav_button(TestWebGroup.driver, 'Groups')
        wti.click_nav_button(TestWebGroup.driver, group_name)
        wti.fill_blank(TestWebGroup.driver, 'search-users-' + group_name, TestWebGroup.gvar['user'] + '-wig2')

    def test_web_group_user_add_checkbox(self):
        self.skipTest("TODO: implement")

    def test_web_group_user_remove(self):
        self.skipTest("TODO: implement")

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
