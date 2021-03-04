import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
from time import sleep

class TestWebKeySuperUser(unittest.TestCase):
    """A class to test key operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['keys'])
        cls.page = pages.KeysPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        print("\nKey Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Keys')

    def test_web_key_find(self):
        # Finds the keys page
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
