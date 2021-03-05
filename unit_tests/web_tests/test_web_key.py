import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
import web_tests.web_test_helpers as helpers

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

    def test_web_key_add_upload(self):
        # Adds a key by uploading it
        key_name = self.gvar['user'] + '-wik3'
        cloud_name = self.gvar['user'] + '-wic1'
        key_file = open('web_tests/misc_files/' + key_name + '.pub', 'r')
        public_key = key_file.read()
        key_file.close()
        self.page.click_upload_key()
        self.page.type_key_name(key_name)
        self.page.type_public_key(public_key)
        self.page.add_upload_to_cloud(cloud_name)
        self.page.click_submit()
        helpers.wait_for_openstack_poller(cloud_name, '-vk', key_name, wait=20)
        #count = 0
        #while subprocess.run(['cloudscheduler', 'cloud', 'update', '-cn', self.gvar['user'] + '-wic1', '-vk', key_name, '-s', 'unit-test']).returncode != 0 and count<20:
        #    print(count)
        #    count += 1
        #    sleep(15)
        self.page.click_top_nav('Keys')
        self.assertTrue(self.page.key_exists(key_name))

    def test_web_key_find(self):
        # Finds the keys page
        pass

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
