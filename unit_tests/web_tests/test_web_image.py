if __name__ == "__main__" or __name__ == "test_web_image":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_interactions as wti
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers


class TestWebImageCommon(unittest.TestCase):
    """A class for the image tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.ImagesPage(cls.driver, cls.gvar['address'])
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        self.page.get_homepage()
        self.page.click_top_nav('Images')

    @unittest.skip("skip to save time")
    def test_web_image_upload_filename(self):
        # Uploads an image to a cloud using a system file
        image_name = self.gvar['user'] + '-wii3.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))
        self.page.select_disk_format('Raw')
        self.page.add_upload_to_cloud(cloud_name)
        with wti.wait_for_page_load(self.driver, timeout=300):
            self.page.click_upload()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_exists(image_name))

        wta.assertExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    # Cindy test the checkboxes-------------------------------------------------
    @unittest.skip("skip to save time")
    def test_three_checkboxes(self):
        self.page.click_upload_image()
        is_no_conversion_checked = self.page.is_checkbox_selected("operation0")
        is_skip_sparsify_checked = self.page.is_checkbox_selected("operation1")
        is_no_compression_checked = self.page.is_checkbox_selected("operation2")

        self.assertFalse(is_no_conversion_checked)
        self.assertFalse(is_skip_sparsify_checked)
        self.assertFalse(is_no_compression_checked)

    def test_web_image_upload_filename_with_three_checkboxes(self):
        # Uploads an image to a cloud using a system file
        image_name = self.gvar['user'] + '-wii4.hdd'
        cloud_name = self.gvar['user'] + '-wic2'

        # test web image upload file_name ends with .qcow2------------------------------------------
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))

        self.page.click_checkbox("operation0")
        self.page.add_upload_to_cloud(cloud_name)
        with wti.wait_for_page_load(self.driver, timeout=1000):
            self.page.click_upload()
        self.page.click_top_nav('Images')

        self.assertTrue(self.page.image_exists(image_name+".qcow2"))
        print("\ntester-wii4.hdd.qcow2 file exists, and should be deleted via csv2-dev after test manually")
        wta.assertExists('image', image_name+".qcow2", group=self.gvar['base_group'], image_cloud=cloud_name)

        # test web image upload file_name ends with .compressed.qcow2-------------------------------
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))

        self.page.click_checkbox("operation0")
        self.page.click_checkbox("operation2")
        self.page.add_upload_to_cloud(cloud_name)
        with wti.wait_for_page_load(self.driver, timeout=1000):
            self.page.click_upload()
        self.page.click_top_nav('Images')

        self.assertTrue(self.page.image_exists(image_name+".compressed.qcow2"))
        print("\ntester-wii4.hdd.compressed.qcow2 file exists, and should be deleted via csv2-dev after test manually")
        wta.assertExists('image', image_name+".compressed.qcow2", group=self.gvar['base_group'], image_cloud=cloud_name)

        # test web image upload file_name ends with .reorganized.qcow2-------------------------------
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))

        self.page.click_checkbox("operation0")
        self.page.click_checkbox("operation1")
        self.page.add_upload_to_cloud(cloud_name)
        with wti.wait_for_page_load(self.driver, timeout=1000):
            self.page.click_upload()
        self.page.click_top_nav('Images')

        self.assertTrue(self.page.image_exists(image_name+".reorganized.qcow2"))
        print("\ntester-wii4.hdd.reorganized.qcow2 file exists, and should be deleted via csv2-dev after test manually")
        wta.assertExists('image', image_name+".reorganized.qcow2", group=self.gvar['base_group'], image_cloud=cloud_name)

        # test web image upload file_name ends with .reorganized.compressed.qcow2-------------------------------
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))

        self.page.click_checkbox("operation0")
        self.page.click_checkbox("operation1")
        self.page.click_checkbox("operation2")
        self.page.add_upload_to_cloud(cloud_name)
        with wti.wait_for_page_load(self.driver, timeout=1000):
            self.page.click_upload()
        self.page.click_top_nav('Images')

        self.assertTrue(self.page.image_exists(image_name+".reorganized.compressed.qcow2"))
        print("\ntester-wii4.hdd.reorganized.compressed.qcow2 file exists, and should be deleted via csv2-dev after test manually")
        wta.assertExists('image', image_name+".reorganized.compressed.qcow2", group=self.gvar['base_group'], image_cloud=cloud_name)


        image_name = self.gvar['user'] + '-wii4.hdd.qcow2'
        cloud_name = self.gvar['user'] + '-wic2'
        with wti.wait_for_page_load(self.driver, timeout=300):
            self.page.click_cloud_button(image_name, cloud_name)
            self.page.click_delete_ok()

        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_is_disabled_in_cloud(image_name, cloud_name))

        image_name = self.gvar['user'] + '-wii4.hdd.compressed.qcow2'
        cloud_name = self.gvar['user'] + '-wic2'
        with wti.wait_for_page_load(self.driver, timeout=300):
            self.page.click_cloud_button(image_name, cloud_name)
            self.page.click_delete_ok()

        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_is_disabled_in_cloud(image_name, cloud_name))

        image_name = self.gvar['user'] + '-wii4.hdd.reorganized.qcow2'
        cloud_name = self.gvar['user'] + '-wic2'
        with wti.wait_for_page_load(self.driver, timeout=300):
            self.page.click_cloud_button(image_name, cloud_name)
            self.page.click_delete_ok()

        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_is_disabled_in_cloud(image_name, cloud_name))

        image_name = self.gvar['user'] + '-wii4.hdd.reorganized.compressed.qcow2'
        cloud_name = self.gvar['user'] + '-wic2'
        with wti.wait_for_page_load(self.driver, timeout=300):
            self.page.click_cloud_button(image_name, cloud_name)
            self.page.click_delete_ok()

        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_is_disabled_in_cloud(image_name, cloud_name))

    # Cindy test the checkboxes-------------------------------------------------

    @unittest.skip("skip to save time")
    def test_web_image_upload_url(self):
        # Uploads an image to a cloud using a URL
        image_name = 'test-os-image-raw.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_upload_image()
        self.page.click_from_url()
        self.page.type_image_url('http://elephant06.heprc.uvic.ca/' + image_name)
        self.page.select_disk_format('Raw')
        self.page.add_upload_to_cloud(cloud_name)
        with wti.wait_for_page_load(self.driver, timeout=300):
            self.page.click_upload()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_exists(image_name))
        wta.assertExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    @unittest.skip("skip to save time")
    def test_web_image_upload_cancel(self):
        # Tries to upload an image to a cloud but clicks cancel
        image_name = self.gvar['user'] + '-wii4.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_upload_image()
        self.page.type_image_file_path(helpers.misc_file_full_path(image_name))
        self.page.select_disk_format('Raw')
        self.page.add_upload_to_cloud(cloud_name)
        with wti.wait_for_page_load(self.driver, timeout=200):
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

    @unittest.skip("skip to save time")
    def test_web_image_download(self):
        # Clicks the image download link
        # Note that Selenium cannot test if files are downloaded
        image_name = self.gvar['user'] + '-wii1.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_download_image(image_name)
        self.page.click_download_ok()

    @unittest.skip("skip to save time")
    def test_web_image_download_cancel(self):
        # Tries to click the download link but clicks cancel
        image_name = self.gvar['user'] + '-wii1.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_download_image(image_name)
        self.page.click_download_cancel()

    @unittest.skip("skip to save time")
    def test_web_image_delete(self):
        # Deletes an image from a cloud
        image_name = self.gvar['user'] + '-wii2.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        with wti.wait_for_page_load(self.driver, timeout=300):
            self.page.click_cloud_button(image_name, cloud_name)
            self.page.click_delete_ok()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_is_disabled_in_cloud(image_name, cloud_name))
        wta.assertNotExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    @unittest.skip("skip to save time")
    def test_web_image_delete_cancel(self):
        # Tries to delete an image from a cloud but clicks cancel
        image_name = self.gvar['user'] + '-wii1.hdd'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_cloud_button(image_name, cloud_name)
        self.page.click_delete_cancel()
        self.page.click_top_nav('Images')
        self.assertTrue(self.page.image_exists(image_name))
        wta.assertExists('image', image_name, group=self.gvar['base_group'], image_cloud=cloud_name)

    @unittest.skip("skip to save time")
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
        try:
            wtsc.setup(cls, 2, ['images'], browser='firefox')
            super(TestWebImageSuperUserFirefox, cls).setUpClass()
            print("\nImage Tests (Super User):")
        except:
            print("Error in test setup")
            super(TestWebImageSuperUserFirefox, cls).tearDownClass()
            raise


class TestWebImageRegularUserFirefox(TestWebImageCommon):
    """A class to test image operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['images'], browser='firefox')
            super(TestWebImageRegularUserFirefox, cls).setUpClass()
            print("\nImage Tests (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebImageRegularUserFirefox, cls).tearDownClass()
            raise


class TestWebImageSuperUserChromium(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['images'], browser='chromium')
            super(TestWebImageSuperUserChromium, cls).setUpClass()
            print("\nImage Tests (Chromium) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebImageSuperUserChromium, cls).tearDownClass()
            raise


class TestWebImageRegularUserChromium(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['images'], browser='chromium')
            super(TestWebImageRegularUserChromium, cls).setUpClass()
            print("\nImage Tests (Chromium) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebImageRegularUserChromium, cls).tearDownClass()
            raise


class TestWebImageSuperUserOpera(TestWebImageCommon):
    """A class to test image operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['images'], browser='opera')
            super(TestWebImageSuperUserOpera, cls).setUpClass()
            print("\nImage Tests (Opera) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebImageSuperUserOpera, cls).tearDownClass()
            raise


class TestWebImageRegularUserOpera(TestWebImageCommon):
    """A class to test image operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['images'], browser='opera')
            super(TestWebImageRegularUserOpera, cls).setUpClass()
            print("\nImage Tests (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebImageRegularUserOpera, cls).tearDownClass()
            raise


class TestWebImageSuperUserChrome(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['images'], browser='chrome')
            super(TestWebImageSuperUserChrome, cls).setUpClass()
            print("\nImage Tests (Chrome) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebImageSuperUserChrome, cls).tearDownClass()
            raise


class TestWebImageRegularUserChrome(TestWebImageCommon):
    """A class to test image operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['images'], browser='chrome')
            super(TestWebImageRegularUserChrome, cls).setUpClass()
            print("\nImage Tests (Chrome) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebImageRegularUserChrome, cls).tearDownClass()
            raise


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [TestWebImageSuperUserFirefox, TestWebImageRegularUserFirefox,
             TestWebImageSuperUserChromium, TestWebImageRegularUserChromium,
             TestWebImageSuperUserOpera, TestWebImageRegularUserOpera,
             TestWebImageSuperUserChrome, TestWebImageRegularUserChrome]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
