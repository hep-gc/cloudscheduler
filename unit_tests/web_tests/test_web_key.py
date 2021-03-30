import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
import web_tests.web_test_helpers as helpers

class TestWebKeyCommon(unittest.TestCase):
    """A class for the key tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.KeysPage(cls.driver)
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        helpers.get_homepage(self.driver)
        self.page.click_top_nav('Keys')

    # TODO: Remove skip when done developing tests
    #@unittest.skip("Working but takes too long to run for other tests")
    def test_web_key_add_create(self):
        # Adds a key by creating it
        key_name = self.gvar['user'] + '-wik4'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_create_key()
        self.page.type_key_name(key_name)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        helpers.wait_for_openstack_poller(cloud_name, '-vk', key_name, wait=20)
        self.page.click_top_nav('Keys')
        self.assertTrue(self.page.key_exists(key_name))

    # TODO: remove skip when done developing tests
    #@unittest.skip("Working but takes too long to run for other tests")
    def test_web_key_add_create_name_too_long(self):
        key_name = self.oversize['varchar_64'] + '1'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_create_key()
        self.page.type_key_name(key_name)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        helpers.wait_for_openstack_poller(cloud_name, '-vk', key_name, wait=20)
        self.page.click_top_nav('Keys')
        self.assertFalse(self.page.key_exists(key_name))

    def test_web_key_add_create_name_taken(self):
        key_name = self.gvar['user'] + '-wik1'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_create_key()
        self.page.type_key_name(key_name)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        self.assertTrue(self.page.key_error_message_displayed())

    # TODO: Remove skip when done developing tests
    #@unittest.skip("Working but takes too long to run for other tests")
    def test_web_key_add_upload(self):
        # Adds a key by uploading it
        key_name = self.gvar['user'] + '-wik3'
        cloud_name = self.gvar['user'] + '-wic1'
        key_file = open('web_tests/misc_files/' + key_name + '.pub', 'r')
        public_key = key_file.read()
        key_file.close()
        public_key = public_key.strip()
        self.page.click_upload_key()
        self.page.type_key_name(key_name)
        self.page.type_public_key(public_key)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        helpers.wait_for_openstack_poller(cloud_name, '-vk', key_name, wait=20)
        self.page.click_top_nav('Keys')
        self.assertTrue(self.page.key_exists(key_name))

    # TODO: remove skip when done developing tests
    #@unittest.skip("Working but takes too long to run for other tests")
    def test_web_key_add_upload_name_too_long(self):
        key_name = self.oversize['varchar_64'] + '2'
        cloud_name = self.gvar['user'] + '-wic1'
        key_file = open('web_tests/misc_files/invalid-web-test.pub', 'r')
        public_key = key_file.read()
        key_file.close()
        public_key = public_key.strip()
        self.page.click_upload_key()
        self.page.type_key_name(key_name)
        self.page.type_public_key(public_key)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        helpers.wait_for_openstack_poller(cloud_name, '-vk', key_name, wait=20)
        self.page.click_top_nav('Keys')
        self.assertFalse(self.page.key_exists(key_name))

    def test_web_key_add_upload_name_taken(self):
        key_name = self.gvar['user'] + '-wik1'
        cloud_name = self.gvar['user'] + '-wic1'
        key_file = open('web_tests/misc_files/invalid-web-test.pub', 'r')
        public_key = key_file.read()
        key_file.close()
        public_key = public_key.strip()
        self.page.click_upload_key()
        self.page.type_key_name(key_name)
        self.page.type_public_key(public_key)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        self.assertTrue(self.page.key_error_message_displayed())

    def test_web_key_find(self):
        # Finds the keys page
        pass

    def test_web_key_delete(self):
        # Removes a key from the keys page
        key_name = self.gvar['user'] + '-wik2'
        self.page.click_cloud_checkbox(key_name, self.gvar['user'] + '-wic1')
        self.page.click_cloud_checkbox(key_name, self.gvar['user'] + '-wic2')
        self.page.click_submit_changes()
        self.page.click_top_nav('Keys')
        self.assertFalse(self.page.key_exists(key_name))

    def test_web_key_update_remove_cloud(self):
        # Removes a key from one cloud, but not all
        key_name = self.gvar['user'] + '-wik1'
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_cloud_checkbox(key_name, cloud_name)
        self.page.click_submit_changes()
        self.page.click_top_nav('Keys')
        self.assertTrue(self.page.key_exists(key_name))
        self.assertTrue(self.page.cloud_box_checked(key_name, self.gvar['user'] + '-wic1'))
        self.assertFalse(self.page.cloud_box_checked(key_name, cloud_name))

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebKeySuperUserFirefox(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['keys'])
        super(TestWebKeySuperUserFirefox, cls).setUpClass()
        print("\nKey Tests (Super User):")

class TestWebKeySuperUserChromium(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['keys'], browser='chromium')
        super(TestWebKeySuperUserChromium, cls).setUpClass()
        print("\nKey Tests (Chromium) (Super User):")

class TestWebKeySuperUserOpera(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['keys'], browser='opera')
        super(TestWebKeySuperUserOpera, cls).setUpClass()
        print("\nKey Tests (Opera) (Super User):")

if __name__ == "__main__":
    unittest.main()
