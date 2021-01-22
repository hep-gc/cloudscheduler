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

    def test_web_group_add(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
