import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebStatusSuperUser(unittest.TestCase):
    """A class to test status operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['status'])
        cls.page = pages.CloudsPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        print("\nStatus Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Status')

    def test_web_status_find(self):
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
