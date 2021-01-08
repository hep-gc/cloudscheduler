import unittest
from selenium import webdriver

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
        self.driver.find_element_by_name("q").send_keys("cloudscheduler")
        self.driver.find_element_by_name("q").submit()
        #TODO - get submit to work by clicking the search button
        #self.driver.find_element_by_id("hplogo").click()
        #self.driver.find_element_by_name("btnK").click()

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
