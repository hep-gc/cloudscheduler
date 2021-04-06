import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
import web_tests.web_test_helpers as helpers

class TestWebImageCommon(unittest.TestCase):
    """A class for the image tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.ImagesPage(cls.driver)
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        helpers.get_homepage(self.driver)
        self.page.click_top_nav('Images')

    def test_web_image_upload_filename(self):
        # Uploads an image to a cloud using a system file
        image_name = self.gvar['user'] + '-wii3.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))
        self.page.select_disk_format('Raw')
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_upload()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_exists(image_name))
        wta.assertExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    def test_web_image_upload_url(self):
        # Uploads an image to a cloud using a URL
        image_name = 'test-os-image-raw.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_upload_image()
        self.page.click_from_url()
        self.page.type_image_url('http://elephant06.heprc.uvic.ca/' + image_name)
        self.page.select_disk_format('Raw')
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_upload()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_exists(image_name))
        wta.assertExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    def test_web_image_upload_cancel(self):
        # Tries to upload an image to a cloud but clicks cancel
        image_name = self.gvar['user'] + '-wii4.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))
        self.page.select_disk_format('Raw')
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_cancel_upload()
        self.page.click_top_nav('Images')
        self.assertFalse(self.page.image_exists(image_name))
        wta.assertNotExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    @unittest.skip("Requires different kinds of clouds")
    def test_web_image_add_to_cloud(self):
        # Transfers an image to another cloud
        image_name = self.gvar['user'] + '-wii1.hdd'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_cloud_button(image_name, cloud_name)
        wta.assertExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    def test_web_image_find(self):
        # Finds the images page
        pass

    def test_web_image_download(self):
        # Clicks the image download link
        # Note that Selenium cannot test if files are downloaded
        image_name = self.gvar['user'] + '-wii1.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_download_image(image_name)
        self.page.click_download_ok()

    def test_web_image_download_cancel(self):
        # Tries to click the download link but clicks cancel
        image_name = self.gvar['user'] + '-wii1.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_download_image(image_name)
        self.page.click_download_cancel()

    def test_web_image_delete(self):
        # Deletes an image from a cloud
        image_name = self.gvar['user'] + '-wii2.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_cloud_button(image_name, cloud_name)
        self.page.click_delete_ok()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_is_disabled_in_cloud(image_name, cloud_name))
        wta.assertNotExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    def test_web_image_delete_cancel(self):
        # Tries to delete an image from a cloud but clicks cancel
        image_name = self.gvar['user'] + '-wii1.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_cloud_button(image_name, cloud_name)
        self.page.click_delete_cancel()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_exists(image_name))
        wta.assertExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    def test_web_image_search(self):
        # Searches for an image
        non_matching_image = self.page.find_non_matching_image(self.gvar['user'])
        self.page.type_in_search_bar(self.gvar['user'])
        self.assertTrue(self.page.image_exists(self.gvar['user'] + '-wii1.hdd'))
        self.assertFalse(self.page.image_exists(non_matching_image))

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebImageSuperUserFirefox(TestWebImageCommon):
    """A class to test image operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['images'], browser='firefox')
        super(TestWebImageSuperUserFirefox, cls).setUpClass()
        print("\nImage Tests (Super User):")

class TestWebImageRegularUser(TestWebImageCommon):
    """A class to test image operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['images'], browser='firefox')
        super(TestWebImageRegularUserFirefox, cls).setUpClass()
        print("\nImage Tests (Regular User):")

class TestWebImageSuperUserChromium(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['images'], browser='chromium')
        super(TestWebImageSuperUserChromium, cls).setUpClass()
        print("\nImage Tests (Chromium) (Super User):")

class TestWebImageRegularUserChromium(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['images'], browser='chromium')
        super(TestWebImageRegularUserChromium, cls).setUpClass()
        print("\nImage Tests (Chromium) (Regular User):")

class TestWebImageSuperUserOpera(TestWebImageCommon):
    """A class to test image operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['images'], browser='opera')
        super(TestWebImageSuperUserOpera, cls).setUpClass()
        print("\nImage Tests (Opera) (Super User):")

class TestWebImageRegularUserOpera(TestWebImageCommon):
    """A class to test image operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['images'], browser='opera')
        super(TestWebImageRegularUserOpera, cls).setUpClass()
        print("\nImage Tests (Regular User):")

class TestWebImageSuperUserChrome(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['images'], browser='chrome')
        super(TestWebImageSuperUserChrome, cls).setUpClass()
        print("\nImage Tests (Chrome) (Super User):")

class TestWebImageRegularUserChrome(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, ['images'], browser='chrome')
        super(TestWebImageRegularUserChrome, cls).setUpClass()
        print("\nImage Tests (Chrome) (Regular User):")

if __name__ == "__main__":
    unittest.main()
