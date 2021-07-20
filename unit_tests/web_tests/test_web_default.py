if __name__ == "__main__" or __name__ == "test_web_default":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers

class TestWebDefaultCommon(unittest.TestCase):
    """A class for the default tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.DefaultsPage(cls.driver, cls.gvar['address'])
        cls.group_name = cls.gvar['user'] + '-wig1'
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        self.page.get_homepage()
        self.page.switch_default_group(self.group_name)
        self.page.click_top_nav('Defaults')

    def test_web_default_find(self):
        pass

    def test_web_default_update_htcondor_fqdn(self):
        # Changes a group's htcondor fqdn
        group_name = self.gvar['user'] + '-wig2'
        self.page.switch_default_group(group_name)
        self.page.click_side_button(group_name)
        self.page.click_side_tab('Settings')
        self.page.type_htcondor_fqdn('csv2-dev2.heprc.uvic.ca')
        self.page.click_update_group()
        wta.assertHasAttribute('group', group_name, 'htcondor_fqdn', 'csv2-dev2.heprc.uvic.ca', group=group_name, defaults=True)

    def test_web_default_update_htcondor_fqdn_invalid(self):
        # Tries to change a group's htcondor fqdn to an invalid fqdn
        group_name = self.gvar['user'] + '-wig2'
        self.page.switch_default_group(group_name)
        self.page.click_side_button(group_name)
        self.page.click_side_tab('Settings')
        self.page.type_htcondor_fqdn('invalid-web-test')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', group_name, 'htcondor_fqdn', 'invalid-web-test', group=group_name, defaults=True)

    def test_web_default_update_htcondor_fqdn_too_long(self):
        # Tries to change a group's htcondor fqdn to one too long for the database
        group_name = self.gvar['user'] + '-wig2'
        self.page.switch_default_group(group_name)
        self.page.click_side_button(group_name)
        self.page.click_side_tab('Settings')
        self.page.type_htcondor_fqdn(self.oversize['varchar_128'])
        self.page.click_update_group()
        # Error message commented out in all length tests because the message isn't bold (and therefore is indistinguishable from a success message)
        # TODO: look into this
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', group_name, 'htcondor_fqdn', self.oversize['varchar_128'], group=group_name, defaults=True)

    def test_web_default_update_htcondor_container_hostname(self):
        # Changes a group's htcondor container hostname
        group_name = self.gvar['user'] + '-wig2'
        self.page.switch_default_group(group_name)
        self.page.click_side_button(group_name)
        self.page.click_side_tab('Settings')
        self.page.type_htcondor_container_hostname(self.gvar['user'] + '-host')
        self.page.click_update_group()
        wta.assertHasAttribute('group', group_name, 'htcondor_container_hostname', self.gvar['user'] + '-host', group=group_name, defaults=True)

    def test_web_default_update_htcondor_container_hostname_too_long(self):
        # Tries to change a group's htcondor container hostname to one too long for the database
        group_name = self.gvar['user'] + '-wig2'
        self.page.switch_default_group(group_name)
        self.page.click_side_button(group_name)
        self.page.click_side_tab('Settings')
        self.page.type_htcondor_container_hostname(self.oversize['varchar_128'])
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', group_name, 'htcondor_container_hostname', self.oversize['varchar_128'])

    def test_web_default_update_htcondor_other_submitters(self):
        # Changes a group's htcondor submitters
        group_name = self.gvar['user'] + '-wig2'
        self.page.switch_default_group(group_name)
        self.page.click_side_button(group_name)
        self.page.click_side_tab('Settings')
        self.page.type_htcondor_other_submitters(self.gvar['user'] + '-wiu1')
        self.page.click_update_group()
        wta.assertHasAttribute('group', group_name, 'htcondor_other_submitters', self.gvar['user'] + '-wiu1', group=group_name, defaults=True)

    def test_web_default_update_htcondor_other_submitters_too_long(self):
        # Tries to change a group's htcondor submitters to a string too long for the database
        group_name = self.gvar['user'] + '-wig2'
        self.page.switch_default_group(group_name)
        self.page.click_side_button(group_name)
        self.page.click_side_tab('Settings')
        self.page.type_htcondor_other_submitters(self.oversize['varchar_128'])
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', group_name, 'htcondor_other_submitters', self.oversize['varchar_128'], group=group_name, defaults=True)

    def test_web_default_update_job_cpus(self):
        # Changes a group's default job cpus
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_cpus('8')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'job_cpus', '8', group=self.group_name, defaults=True)

    def test_web_default_update_job_cpus_float(self):
        # Tries to change a group's default job cpus to a float
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_cpus('8.5')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_cpus', '8.5', group=self.group_name, defaults=True)

    def test_web_default_update_job_cpus_string(self):
        # Tries to change a group's default job cpus to a string
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_cpus('invalid-web-test')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_cpus', 'invalid-web-test', group=self.group_name, defaults=True)

    def test_web_default_update_job_cpus_too_big(self):
        # Tries to change a group's default job cpus to an int too long for the database
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_cpus(str(self.oversize['int_11']))
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_cpus', str(self.oversize['int_11']), group=self.group_name, defaults=True)

    def test_web_default_update_job_ram(self):
        # Changes a group's default RAM
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_ram('1024')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'job_ram', '1024', group=self.group_name, defaults=True)

    def test_web_default_update_job_ram_float(self):
        # Tries to change a group's default RAM to a float
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_ram('1024.5')
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_ram', '1024.5', group=self.group_name, defaults=True)

    def test_web_default_update_job_ram_string(self):
        # Tries to change a group's default RAM to a string
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_ram('invalid-web-test')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_ram', 'invalid-web-test', group=self.group_name, defaults=True)

    def test_web_default_update_job_ram_too_big(self):
        # Tries to change a group's default RAM to an int too big for the database
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_ram(str(self.oversize['int_11']))
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_ram', str(self.oversize['int_11']), group=self.group_name, defaults=True)

    def test_web_default_update_job_disk(self):
        # Changes a group's default disk size
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_disk('4')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'job_disk', '4', group=self.group_name, defaults=True)

    def test_web_default_update_job_disk_float(self):
        # Tries to change a group's default disk size to a float
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_disk('8.5')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_disk', '4.5', group=self.group_name, defaults=True)

    def test_web_default_update_job_disk_string(self):
        # Tries to change a group's default disk size to a string
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_disk('invalid-web-test')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_disk', 'invalid-web-test', group=self.group_name, defaults=True)

    def test_web_default_update_job_disk_too_big(self):
        # Tries to change a group's default disk size to an int too big for the database
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_disk(str(self.oversize['int_11']))
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_disk', str(self.oversize['int_11']), group=self.group_name, defaults=True)

    def test_web_default_update_job_swap(self):
        # Changes a group's default SWAP
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_swap('2')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'job_swap', '2', group=self.group_name, defaults=True)

    def test_web_default_update_job_swap_float(self):
        # Tries to change a group's default SWAP to a float
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_swap('2.5')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_swap', '2.5', group=self.group_name, defaults=True)

    def test_web_default_update_job_swap_string(self):
        # Tries to change a group's default SWAP to a string
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_swap('invalid-web-test')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_swap', 'invalid-web-test', group=self.group_name, defaults=True)

    def test_web_default_update_job_swap_too_big(self):
        # Tries to change a group's default SWAP to an int too big for the database
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_job_swap(str(self.oversize['int_11']))
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'job_swap', str(self.oversize['int_11']), group=self.group_name, defaults=True)

    def test_web_default_update_vm_keyname(self):
        # Update's a group's default vm keyname
        helpers.skip_if_flag('keys accessible', self.gvar['keys_accessible'], False)
        keyname = self.gvar['user'] + '-wik1'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.select_vm_keyname(keyname)
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'vm_keyname', keyname, group=self.group_name, defaults=True)

    def test_web_default_update_vm_image(self):
        # Updates a group's default vm image
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.select_vm_image('cirros-0.3.5')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'vm_image', 'cirros-0.3.5', group=self.group_name, defaults=True)

    def test_web_default_update_vm_flavor(self):
        # Updates a group's default vm flavor
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.select_vm_flavor('s8')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'vm_flavor', 's8', group=self.group_name, defaults=True)

    def test_web_default_update_vm_network(self):
        # Updates a group's default vm network
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.select_vm_network('private')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'vm_network', 'private', group=self.group_name, defaults=True)

    def test_web_default_update_vm_keep_alive(self):
        # Updates a group's default vm keep alive time
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_vm_keep_alive('2048')
        self.page.click_update_group()
        wta.assertHasAttribute('group', self.group_name, 'vm_keep_alive', '2048', group=self.group_name, defaults=True)

    def test_web_default_update_vm_keep_alive_float(self):
        # Tries to update a group's default vm keep alive time to a float
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_vm_keep_alive('2048.5')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'vm_keep_alive', '2048.5', group=self.group_name, defaults=True)

    def test_web_default_update_vm_keep_alive_string(self):
        # Tries to update a group's default vm keep alive time to a string
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_vm_keep_alive('invalid-web-test')
        self.page.click_update_group()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'vm_keep_alive', 'invalid-web-test', group=self.group_name, defaults=True)

    def test_web_default_update_vm_keep_alive_too_big(self):
        # Tries to update a group's default vm keep alive time to an int too big for the database
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Settings')
        self.page.type_vm_keep_alive(str(self.oversize['int_11']))
        self.page.click_update_group()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('group', self.group_name, 'vm_keep_alive', str(self.oversize['int_11']), group=self.group_name, defaults=True)

    def test_web_default_metadata_add(self):
        # Adds metadata to a group
        metadata_name = self.gvar['user'] + '-wim3.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertExists('metadata', metadata_name, group=self.group_name)

    @unittest.skip("Not working in production (issue 319)")
    def test_web_default_metadata_add_without_name(self):
        # Tries to add metadata to a group without a name
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())

    @unittest.skip("Not working in production (issue 319)")
    def test_web_default_metadata_add_name_with_symbols(self):
        # Tries to add metadata with symbols in its name
        metadata_name = 'inv@|id-web-te$t.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    @unittest.skip("Not working in production (issue 319)")
    def test_web_default_metadata_add_name_with_two_dashes(self):
        # Tries to add metadata with two dashes in its name
        metadata_name = 'invalid--web--test.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    @unittest.skip("Not working in production (issue 319)")
    def test_web_default_metadata_add_name_with_uppercase(self):
        # Tries to add metadata with uppercase letters in its name
        metadata_name = 'INVALID-WEB-TEST.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    @unittest.skip("Not working in production (issue 319)")
    def test_web_default_metadata_add_name_with_starting_ending_dash(self):
        # Tries to add metadata with starting and ending dashes in its name
        metadata_name = '-invalid-web-test-.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    def test_web_default_metadata_add_name_too_long(self):
        # Tries to add metadata with a name too long for the database
        metadata_name = self.oversize['varchar_64']
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_add()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    def test_web_default_metadata_add_not_enabled(self):
        # Adds metadata to a group without enabling it
        metadata_name = self.gvar['user'] + '-wim4.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.click_metadata_enabled()
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'enabled', '0', group=self.group_name)

    def test_web_default_metadata_add_different_priority_by_typing(self):
        # Adds metadata to a group with a different priority by typing it in the blank
        metadata_name = self.gvar['user'] + '-wim5.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata_priority('8')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '8', group=self.group_name)

    def test_web_default_metadata_add_different_priority_by_typing_float(self):
        # Tries to add metadata to a cloud with a float value for its priority by typing it in the blank
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata_priority('8.5')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertNotExists('metadata', metadata_name, group= self.group_name)

    def test_web_default_metadata_add_different_priority_by_typing_string(self):
        # Tries to add metadata to a group with a string value priority by typing it in the blank
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata_priority('invalid-web-test')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    def test_web_default_metadata_add_different_priority_by_typing_too_big(self):
        # Tries to add metadata to a group with a priority too big for the database by typing it in the blank
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_priority(str(self.oversize['int_11']))
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        #self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    def test_web_default_metadata_add_different_priority_by_arrows(self):
        # Adds metadata to a group with a different priority using the arrow keys
        metadata_name = self.gvar['user'] + '-wim6.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.increment_metadata_priority_by_arrows(16)
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '16', group=self.group_name)

    @unittest.skip("Probably takes too long to be worth running")
    def test_web_default_metadata_add_different_priority_by_arrows_too_big(self):
        # Tries to add metadata to a group with a priority too big for the database using the arrow keys
        metadata_name = self.gvar['user'] + '-wim6.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.increment_metadata_priority_by_arrows(str(self.oversize['int_11']))
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', str(self.oversize['int_11']), group=self.group_name)

    def test_web_default_metadata_add_different_mime_type(self):
        # Adds metadata to a group with a different MIME type
        metadata_name = self.gvar['user'] + '-wim7.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.select_metadata_mime_type('ucernvm-config')
        self.page.type_metadata('sample_key: sample_value')
        self.page.click_metadata_add()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertHasAttribute('metadata', metadata_name, 'mime_type', 'ucernvm-config', group=self.group_name)

    @unittest.skip("Not working (supposed to work?)")
    def test_web_default_metadata_add_mismatched_file_type(self):
        # Tries to add metadata to a group with a file that doesn't match its name
        metadata_name = self.gvar['user'] + '-wim8.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata_new()
        self.page.type_metadata_name(metadata_name)
        self.page.type_metadata('invalid-unit-test')
        self.page.click_metadata_add()
        self.assertTrue(self.page.error_message_displayed())
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    def test_web_default_metadata_update_enabled_status(self):
        # Changes enabled metadata to not enabled
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.click_metadata_enabled()
        self.page.click_metadata_update()
        # TODO: implement checkbox clicked check method
        wta.assertHasAttribute('metadata', metadata_name, 'enabled', '0', group=self.group_name)

    def test_web_default_metadata_update_priority_by_typing(self):
        # Changes metadata priority by typing in the blank
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority('8')
        self.page.click_metadata_update()
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '8', group=self.group_name)

    def test_web_default_metadata_update_priority_by_typing_float(self):
        # Tries to change metadata priority to a float by typing it in the blank
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority('8.5')
        self.page.click_metadata_update()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', '8.5', group=self.group_name)

    def test_web_default_metadata_update_priority_by_typing_string(self):
        # Tries to change metadata priority to a string by typing it in the blank
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority('invalid-web-test')
        self.page.click_metadata_update()
        self.assertTrue(self.page.metadata_priority_popup_exists())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', 'invalid-web-test', group=self.group_name)

    def test_web_default_metadata_update_priority_by_typing_too_big(self):
        # Tries to change metadata priority to an int too big for the database by typing it in the blank
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata_priority(str(self.oversize['int_11']))
        self.page.click_metadata_update()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', str(self.oversize['int_11']), group=self.group_name)

    def test_web_default_metadata_update_priority_by_arrow_keys(self):
        # Changes metadata priority using the arrow keys
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.increment_metadata_priority_by_arrows(16)
        self.page.click_metadata_update()
        wta.assertHasAttribute('metadata', metadata_name, 'priority', '16', group=self.group_name)

    @unittest.skip("Probably takes too long to be worth running")
    def test_web_default_metadata_update_priority_by_arrow_keys_too_big(self):
        # Tries to change metadata priority to an int too big for the database using the arrow keys
        metadata_name = self.gvar['user'] + 'wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.increment_metadata_priority_by_arrows(str(self.oversize['int_11']))
        self.page.click_metadata_update()
        #self.assertTrue(self.page.error_message_displayed())
        wta.assertHasNotAttribute('metadata', metadata_name, 'priority', str(self.oversize['int_11']), group=self.group_name)

    def test_web_default_metadata_update_mime_type(self):
        # Changes metadata mime type
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.select_metadata_mime_type('ucernvm-config')
        self.page.click_metadata_update()
        wta.assertHasAttribute('metadata', metadata_name, 'mime_type', 'ucernvm-config', group=self.group_name)

    def test_web_default_metadata_update_contents(self):
        # Changes metadata text
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata('sample_key_2: sample_value_2')
        self.page.click_metadata_update()
        # Note: there appears to be no way to test that this has been updated
        self.assertFalse(self.page.error_message_displayed())

    @unittest.skip("Not working (supposed to work?)")
    def test_web_default_metadata_update_contents_mismatched(self):
        # Tries to change metadata text to something of the wrong file type
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.type_metadata('invalid-web-test')
        self.page.click_metadata_update()
        # Note: there appears to be no way to test that this has not been updated
        self.assertTrue(self.page.error_message_displayed())

    def test_web_default_metadata_delete(self):
        # Deletes metadata from a group
        metadata_name = self.gvar['user'] + '-wim2.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.click_metadata_delete()
        self.page.click_metadata_delete_modal()
        self.assertFalse(self.page.metadata_tab_exists(metadata_name))
        wta.assertNotExists('metadata', metadata_name, group=self.group_name)

    def test_web_default_metadata_delete_cancel(self):
        # Tries to delete metadata from a group but clicks cancel
        metadata_name = self.gvar['user'] + '-wim1.yaml'
        self.page.click_side_button(self.group_name)
        self.page.click_side_tab('Metadata')
        self.page.click_metadata(metadata_name)
        self.page.click_metadata_delete()
        self.page.click_metadata_delete_cancel()
        self.assertTrue(self.page.metadata_tab_exists(metadata_name))
        wta.assertExists('metadata', metadata_name, group=self.group_name)

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebDefaultSuperUserFirefox(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['defaults', 'keys'], browser='firefox')
            super(TestWebDefaultSuperUserFirefox, cls).setUpClass()
            print("\nDefault Tests (Super User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultSuperUserFirefox, cls).tearDownClass()
            raise

class TestWebDefaultRegularUserFirefox(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['defaults', 'keys'], browser='firefox')
            super(TestWebDefaultRegularUserFirefox, cls).setUpClass()
            print("\nDefault Tests (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultRegularUserFirefox, cls).tearDownClass()
            raise

class TestWebDefaultSuperUserChromium(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['defaults', 'keys'], browser='chromium')
            super(TestWebDefaultSuperUserChromium, cls).setUpClass()
            print("\nDefault Tests (Chromium) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultSuperUserChromium, cls).tearDownClass()
            raise

class TestWebDefaultRegularUserChromium(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['defaults', 'keys'], browser='chromium')
            super(TestWebDefaultRegularUserChromium, cls).setUpClass()
            print("\nDefault Tests (Chromium) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultRegularUserChromium, cls).tearDownClass()
            raise

class TestWebDefaultSuperUserOpera(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['defaults', 'keys'], browser='opera')
            super(TestWebDefaultSuperUserOpera, cls).setUpClass()
            print("\nDefault Tests (Opera) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultSuperUserOpera, cls).tearDownClass()
            raise

class TestWebDefaultRegularUserOpera(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['defaults', 'keys'], browser='opera')
            super(TestWebDefaultRegularUserOpera, cls).setUpClass()
            print("\nDefault Tests (Opera) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultRegularUserOpera, cls).tearDownClass()
            raise

class TestWebDefaultSuperUserChrome(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['defaults', 'keys'], browser='chrome')
            super(TestWebDefaultSuperUserChrome, cls).setUpClass()
            print("\nDefault Tests (Chrome) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultSuperUserChrome, cls).tearDownClass()
            raise

class TestWebDefaultRegularUserChrome(TestWebDefaultCommon):
    """A class to test default operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['defaults', 'keys'], browser='chrome')
            super(TestWebDefaultRegularUserChrome, cls).setUpClass()
            print("\nDefault Tests (Chrome) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebDefaultRegularUserChrome, cls).tearDownClass()
            raise

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebDefaultSuperUserFirefox, TestWebDefaultRegularUserFirefox,
              TestWebDefaultSuperUserChromium, TestWebDefaultRegularUserChromium,
              TestWebDefaultSuperUserOpera, TestWebDefaultRegularUserOpera,
              TestWebDefaultSuperUserChrome, TestWebDefaultRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
