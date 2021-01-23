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
        cls.gvar = wtsc.setup()
        print(cls.gvar['firefox_profiles'][1])
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.gvar['firefox_profiles'][1]))
        cls.driver.get("https://csv2-dev.heprc.uvic.ca")
        cls.alert = cls.driver.switch_to.alert
        cls.alert.accept()
        print("Group Tests:")

    def test_web_group_find(self):
        wti.click_nav_button(TestWebGroup.driver, 'Groups')

    def test_web_group_add_checkbox(self):
        wti.click_nav_button(TestWebGroup.driver, 'Groups')
        wti.click_nav_button(TestWebGroup.driver, '+')
        wti.fill_blank(TestWebGroup.driver, "new_group", TestWebGroup.gvar['user'] + 'wig5')
        wti.click_by_value(TestWebGroup.driver, TestWebGroup.gvar['user'] + '-wiu2')
        TestWebGroup.driver.find_element_by_id("new_group").submit()
        wti.click_by_value(TestWebGroup.driver, "Add Group")
        assertTrue(WebDriverWait(TestWebGroup.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, TestWebGroup.gvar['user'] + '-wig5'))))

    def test_web_group_add_search_bar(self):
        wti.click_nav_button(TestWebGroup.driver, 'Groups')
        wti.click_nav_button(TestWebGroup.driver, '+')
        wti.fill_blank(TestWebGroup.driver, "new_group", TestWebGroup.gvar['user'] + '-wig6')
        wti.fill_blank(TestWebGroup.driver, "search-users-", TestWebGroup.gvar['user'] + '-wiu2')
        TestWebGroup.driver.find_element_by_id("new_group").submit()
        self.assertTrue(WebDriverWait(TestWebGroup.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, TestWebGroup.gvar['user'] + '-wig6'))))


    # TODO: clean up as part of tearDown
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        print("Unittest Teardown:")

if __name__ == "__main__":
    unittest.main()
