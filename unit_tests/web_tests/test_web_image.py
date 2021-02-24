import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebImageSuperUser(unittest.TestCase):
    """A class to test image operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['images']) #TODO: add images setup
        cls.page = pages.ImagesPage(cls.driver) #TODO: set up images page object
        cls.oversize = cls.gvar['oversize']
        print("\nImage Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)

    def test_web_image_find(self):
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
