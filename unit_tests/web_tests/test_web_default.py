import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions as wta
import web_tests.web_test_page_objects as pages

class TestWebDefaultSuperUser(unittest.TestCase):
    """A class to test default operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['defaults']) #TODO: add appropriate setup
        cls.page = pages.DefaultsPage(cls.driver)
        print("\nDefault Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Defaults')

    def test_web_default_find(self):
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()