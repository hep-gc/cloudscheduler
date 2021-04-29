if __name__ == "__main__" or __name__ == "test_web_key":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers

class TestWebKeyCommon(unittest.TestCase):
    """A class for the key tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        helpers.skip_if_flag('keys accessible', cls.gvar['keys_accessible'], False)
        cls.page = pages.KeysPage(cls.driver, cls.gvar['address'])
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        self.page.get_homepage()
        self.page.click_top_nav('Keys')

    # TODO: Remove skip when done developing tests
    @unittest.skip("Working but takes too long to run for other tests")
    def test_web_key_add_create(self):
        # Adds a key by creating it
        key_name = self.gvar['user'] + '-wik4'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_create_key()
        self.page.type_key_name(key_name)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        helpers.wait_for_openstack_poller(cloud_name, ['-vk', key_name], wait=20)
        self.page.click_top_nav('Keys')
        self.assertTrue(self.page.key_exists(key_name))

    # TODO: remove skip when done developing tests
    @unittest.skip("Working but takes too long to run for other tests")
    def test_web_key_add_create_name_too_long(self):
        key_name = self.oversize['varchar_64'] + '1'
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_create_key()
        self.page.type_key_name(key_name)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        helpers.wait_for_openstack_poller(cloud_name, ['-vk', key_name], wait=20)
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
    @unittest.skip("Working but takes too long to run for other tests")
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
        helpers.wait_for_openstack_poller(cloud_name, ['-vk', key_name], wait=20)
        self.page.click_top_nav('Keys')
        self.assertTrue(self.page.key_exists(key_name))

    # TODO: remove skip when done developing tests
    @unittest.skip("Working but takes too long to run for other tests")
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
        helpers.wait_for_openstack_poller(cloud_name, ['-vk', key_name], wait=20)
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
        try:
            wtsc.setup(cls, 2, ['keys'], browser='firefox')
            super(TestWebKeySuperUserFirefox, cls).setUpClass()
            print("\nKey Tests (Firefox) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebKeySuperUserFirefox, cls).tearDownClass()
            raise

class TestWebKeyRegularUserFirefox(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['keys'], browser='firefox')
            super(TestWebKeyRegularUserFirefox, cls).setUpClass()
            print("\nKey Tests (Firefox) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebKeyRegularUserFirefox, cls).tearDownClass()
            raise

class TestWebKeySuperUserChromium(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['keys'], browser='chromium')
            super(TestWebKeySuperUserChromium, cls).setUpClass()
            print("\nKey Tests (Chromium) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebKeySuperUserChromium, cls).tearDownClass()
            raise

class TestWebKeyRegularUserChromium(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['keys'], browser='chromium')
            super(TestWebKeyRegularUserChromium, cls).setUpClass()
            print("\nKey Tests (Chromium) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebKeyRegularUserChromium, cls).tearDownClass()
            raise

class TestWebKeySuperUserOpera(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['keys'], browser='opera')
            super(TestWebKeySuperUserOpera, cls).setUpClass()
            print("\nKey Tests (Opera) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebKeySuperUserOpera, cls).tearDownClass()
            raise

class TestWebKeyRegularUserOpera(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['keys'], browser='opera')
            super(TestWebKeyRegularUserOpera, cls).setUpClass()
            print("\nKey Tests (Opera) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebKeyRegularUserOpera, cls).tearDownClass()
            raise

class TestWebKeySuperUserChrome(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['keys'], browser='chrome')
            super(TestWebKeySuperUserChrome, cls).setUpClass()
            print("\nKey Tests (Chrome) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebKeySuperUserChrome, cls).tearDownClass()
            raise

class TestWebKeyRegularUserChrome(TestWebKeyCommon):
    """A class to test key operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['keys'], browser='chrome')
            super(TestWebKeySuperUserChrome, cls).setUpClass()
            print("\nKey Tests (Chrome) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebKeyRegularUserChrome, cls).tearDownClass()
            raise

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebKeySuperUserFirefox, TestWebKeyRegularUserFirefox,
              TestWebKeySuperUserChromium, TestWebKeyRegularUserChromium,
              TestWebKeySuperUserOpera, TestWebKeyRegularUserOpera,
              TestWebKeySuperUserChrome, TestWebKeyRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
