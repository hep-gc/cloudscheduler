import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions as wta
import web_tests.web_test_page_objects as pages

class TestWebCloudSuperUser(unittest.TestCase):
    """A class to test cloud operations via the web interface, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['clouds'])
        cls.credentials = cls.gvar['cloud_credentials']
        cls.page = pages.CloudsPage(cls.driver)
        print("\nCloud Tests (Super User):")

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Clouds')

    def test_web_cloud_add(self):
        # Adds a standard cloud
        cloud_name = self.gvar['user'] + '-wic3'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.side_button_exists(cloud_name))
        wta.assertAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_add_not_enabled(self):
        # Adds a cloud that is not enabled
        cloud_name = self.gvar['user'] + '-wic4'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.side_button_exists(cloud_name))
        wta.assertAddedWithAttribute('cloud', cloud_name, 'enabled', '0', self.gvar['base_group'])

    def test_web_cloud_add_different_priority(self):
        # Adds a cloud with a non-default priority
        cloud_name = self.gvar['user'] + '-wic5'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('10')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.side_button_exists(cloud_name))
        wta.assertAddedWithAttribute('cloud', cloud_name, 'cloud_priority', '10', self.gvar['base_group'])

    def test_web_cloud_add_without_name(self):
        # Tries to add a cloud without naming it
        cloud_name = self.gvar['user'] + '-wic3'
        self.page.click_add_button()
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())

    def test_web_cloud_add_with_conflicting_name(self):
        # Tries to add a cloud with a name that's already being used
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasAttribute('cloud', cloud_name, 'enabled', '1', self.gvar['base_group'])

    def test_web_cloud_add_without_url(self):
        # Tries to add a cloud without an authurl
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_add_without_region(self):
        # Tries to add a cloud without a region
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_add_without_username(self):
        # Tries to add a cloud without a username
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_add_without_password(self):
        # Tries to add a cloud without a password
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_user_domain_name('Default')
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_add_without_user_domain_name(self):
        # Tries to add a cloud without a user domain name
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_project_domain_name('default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_add_without_project_domain_name(self):
        # Tries to add a cloud without a project domain name
        cloud_name = self.gvar['user'] + '-wic6'
        self.page.click_add_button()
        self.page.type_cloud_name(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.type_priority('0')
        self.page.select_cloud_type('openstack')
        self.page.type_url(self.credentials['authurl'])
        self.page.type_region(self.credentials['region'])
        self.page.type_project(self.credentials['project'])
        self.page.type_username(self.credentials['username'])
        self.page.type_password(self.credentials['password'])
        self.page.type_user_domain_name('Default')
        self.page.click_add_cloud()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotAdded('cloud', cloud_name, self.gvar['base_group'])

    def test_web_cloud_find(self):
        # Finds the clouds page
        pass

    def test_web_cloud_find_settings(self):
        self.page.click_side_button(self.gvar['user'] + '-wic1')
        self.page.click_side_tab('Settings')

    def test_web_cloud_find_metadata(self):
        self.page.click_side_button(self.gvar['user'] + '-wic1')
        self.page.click_side_tab('Metadata')

    def test_web_cloud_find_exclusions(self):
        self.page.click_side_button(self.gvar['user'] + '-wic1')
        self.page.click_side_tab('Exclusions')

    def test_web_cloud_update_enabled_status(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.click_enabled_checkbox()
        self.page.click_update_cloud()
        self.assertFalse(self.page.enabled_box_checked())
        wta.assertHasAttribute('cloud', cloud_name, 'enabled', '0', self.gvar['base_group'])

    def test_web_cloud_update_priority(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_priority('15')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cloud_priority', '15', self.gvar['base_group'])

    def test_web_cloud_update_boot_volume(self):
        cloud_name = self.gvar['user'] + '-wic1'
        boot_volume = '{"GBs": 10, "GBs_per_core": 5}'
        self.page.click_side_button(cloud_name)
        self.page.type_boot_volume(boot_volume)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_boot_volume', boot_volume, self.gvar['base_group'])

    def test_web_cloud_update_add_security_group(self):
        cloud_name = self.gvar['user'] + '-wic1'
        security_group = 'csv2-sa'
        self.page.click_side_button(cloud_name)
        self.page.add_security_group(security_group)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_security_groups', security_group, self.gvar['base_group'])

    def test_web_cloud_update_remove_security_group(self):
        cloud_name = self.gvar['user'] + '-wic1'
        security_group = 'default'
        self.page.click_side_button(cloud_name)
        self.page.remove_security_group(security_group)
        self.page.click_update_cloud()
        wta.assertHasNotAttribute('cloud', cloud_name, 'vm_security_groups', security_group, self.gvar['base_group'])

    @unittest.skip("TODO: implement")
    def test_web_cloud_update_vm_keyname(self):
        pass

    def test_web_cloud_update_vm_network(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.select_vm_network('private')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_network', 'private', self.gvar['base_group'])

    def test_web_cloud_update_vm_image(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.select_vm_image('cirros-0.3.5')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_image', 'cirros-0.3.5', self.gvar['base_group'])

    def test_web_cloud_update_vm_flavor(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.select_vm_flavor('s8')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_flavor', 's8', self.gvar['base_group'])

    def test_web_cloud_update_vm_keep_alive(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_vm_keep_alive('300')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'vm_keep_alive', '300', self.gvar['base_group'])

    @unittest.skip("Needs Amazon cloud")
    def test_web_cloud_update_spot_price(self):
        pass

    def test_web_cloud_update_cores_softmax(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores_softmax('4')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cores_softmax', '4', self.gvar['base_group'])

    def test_web_cloud_update_cores_by_blank(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_cores('4')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cores_ctl', '4', self.gvar['base_group'])

    def test_web_cloud_update_cores_by_slider(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.slide_cores_slider(8)
        self.page.click_update_cloud()
        wta.assertHasNearAttribute('cloud', cloud_name, 'cores_ctl', '8', 3, self.gvar['base_group'])

    def test_web_cloud_update_cores_by_arrows(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.increment_cores_by_arrows(16)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'cores_ctl', '16', self.gvar['base_group'])

    def test_web_cloud_update_ram_by_blank(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.type_ram('65536')
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'ram_ctl', '65536', self.gvar['base_group'])

    def test_web_cloud_update_ram_by_slider(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.slide_ram_slider(131072)
        self.page.click_update_cloud()
        wta.assertHasNearAttribute('cloud', cloud_name, 'ram_ctl', '131072', 6000, self.gvar['base_group'])

    def test_web_cloud_update_ram_by_arrows(self):
        cloud_name = self.gvar['user'] + '-wic1'
        self.page.click_side_button(cloud_name)
        self.page.increment_ram_by_arrows(4096)
        self.page.click_update_cloud()
        wta.assertHasAttribute('cloud', cloud_name, 'ram_ctl', '4096', self.gvar['base_group'])

    def test_web_cloud_delete(self):
        cloud_name = self.gvar['user'] + '-wic2'
        self.page.click_side_button(cloud_name)
        self.page.click_delete_button()
        self.page.click_delete_modal()
        self.assertFalse(self.page.side_button_exists(cloud_name))
        wta.assertDeleted('cloud', cloud_name, self.gvar['base_group'])

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
