import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebConfig(unittest.TestCase):
    """A class to test config operatiohns via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['config'])
        cls.page = pages.ConfigPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        print("\nConfig Tests:")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Config')

    def test_web_config_find(self):
        # Finds the config page
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
