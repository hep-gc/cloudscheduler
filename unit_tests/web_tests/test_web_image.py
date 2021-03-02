import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
from time import sleep

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
        self.page.click_top_nav('Images')

    def test_web_image_upload(self):
        self.page.click_upload_image()
        # TODO: fix hardcoding
        self.page.type_image_file_path('/home/centos/cloudscheduler/unit_tests/web_tests/eklassen-wii3.hdd')
        self.page.select_disk_format('Raw')
        self.page.add_upload_to_cloud(self.gvar['user'] + '-wic1')
        self.page.click_upload()
        wta.assertExists('image', self.gvar['user'] + '-wii3.hdd', group=self.gvar['base_group'], image_cloud=self.gvar['user'] + '-wic1')

    def test_web_image_find(self):
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
