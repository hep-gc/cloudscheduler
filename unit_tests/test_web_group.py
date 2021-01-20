import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestWebGroup(unittest.TestCase):
    "A class to test group operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile("/root/.mozilla/firefox/51zyh7r1.elisabethklassen-test"))
        cls.driver.get("https://csv2-dev.heprc.uvic.ca")
        cls.alert = cls.driver.switch_to.alert
        cls.alert.accept()

    def test_web_group_0001(self):
        WebDriverWait(TestWebGroup.driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Status")))
        self.status_button = TestWebGroup.driver.find_element_by_link_text('Status')
        self.status_button.click()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
