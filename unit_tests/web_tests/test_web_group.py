import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import web_tests.web_test_common as wtc

class TestWebGroup(unittest.TestCase):
    """A class to test group operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile("/root/.mozilla/firefox/um1bq9sv.eklassen-wiu2/"))
        cls.driver.get("https://csv2-dev.heprc.uvic.ca")
        cls.alert = cls.driver.switch_to.alert
        cls.alert.accept()

    def test_web_group_find(self):
        wtc.click_nav_button(TestWebGroup.driver, 'Groups')

    def test_web_group_add_checkbox(self):
        wtc.click_nav_button(TestWebGroup.driver, 'Groups')
        wtc.click_nav_button(TestWebGroup.driver, '+')
        #TODO: fix hard-coding
        wtc.fill_blank(TestWebGroup.driver, "new_group", "eklassen-wig5")
        wtc.click_by_value(TestWebGroup.driver, "eklassen-wiu2")
        TestWebGroup.driver.find_element_by_id("new_group").submit()
        wtc.click_by_value(TestWebGroup.driver, "Add Group")
        assertTrue(WebDriverWait(TestWebGroup.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "eklassen-wig5"))))

    def test_web_group_add_search_bar(self):
        wtc.click_nav_button(TestWebGroup.driver, 'Groups')
        wtc.click_nav_button(TestWebGroup.driver, '+')
        #TODO: fix hard-coding
        wtc.fill_blank(TestWebGroup.driver, "new_group", "eklassen-wig6")
        wtc.fill_blank(TestWebGroup.driver, "search-users-", "eklassen-wiu2")
        TestWebGroup.driver.find_element_by_id("new_group").submit()
        self.assertTrue(WebDriverWait(TestWebGroup.driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "eklassen-wig6"))))


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
