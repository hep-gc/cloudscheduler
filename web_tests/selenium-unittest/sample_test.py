import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class SampleTest(unittest.TestCase):
    """A class to do a few small, simple tests as a trial run for selenium and
       unittest."""

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_canary(self):
        """The proverbial canary in the coal mine - if this fails, the setup is incorrect."""
        self.assertTrue(True)

    def test_find_element(self):
        """Navigates to google and finds the search bar."""
        self.driver.get("https://google.com")
        self.assertTrue(self.driver.find_element_by_name("q"))

    def test_type_in_element(self):
        """Navigates to google and types in the search bar."""
        self.driver.get("https://google.com")
        self.search_bar = self.driver.find_element_by_name("q")
        self.search_bar.send_keys("cloudscheduler")

    def test_submit(self):
        """Navigates to google, types in the search bar, and searches."""
        self.driver.get("https://google.com")
        self.search_bar = self.driver.find_element_by_name("q")
        self.search_bar.send_keys("cloudscheduler")
        self.search_bar.submit()
        #TODO - get submit to work by clicking the search button
        #self.driver.find_element_by_id("hplogo").click()
        #self.driver.find_element_by_name("btnK").click()

    #def test_submit_button(self):
    #    TODO: This doesn't work for some reason.
    #    """Navigates to google, types in the search bar, and searches with the search button."""
    #    self.driver.get("https://google.com")
    #    self.search_bar = self.driver.find_element_by_name("q")
    #    self.search_bar.send_keys("cloudscheduler")
    #    self.search_bar.send_keys(Keys.TAB)
    #    self.driver.find_element_by_class_name("RNmpXc").click()
    
    def test_other_website(self):
        """Navigates to DuckDuckGo and searches."""
        self.driver.get("https://duckduckgo.com")
        self.search_bar = self.driver.find_element_by_name("q")
        self.search_bar.send_keys("cloudscheduler")
        self.driver.find_element_by_id("search_button_homepage").click()

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
