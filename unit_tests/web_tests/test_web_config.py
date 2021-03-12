import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebConfigCommon(unittest.TestCase):
    """A class for the config tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.ConfigPage(cls.driver)
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        wtsc.get_homepage(self.driver)
        self.page.click_top_nav('Config')

    def test_web_config_find(self):
        # Finds the config page
        pass

    # All tests in this file should reverse themselves if they perform any saved
    # action
    # Tests are organized by file, because each one is unique
    # Currently, the tested files are:
    # condor_poller.py

    # Tests for condor_poller.py

    def test_web_config_update_condor_poller_batch_commit_size(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_batch_commit_size() 
        self.page.type_batch_commit_size('40')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_batch_commit_size(), '40')
        # reverse
        self.page.type_batch_commit_size(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_batch_commit_size_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_batch_commit_size('50.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_batch_commit_size(), '50.5')

    def test_web_config_update_condor_poller_batch_commit_size_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_batch_commit_size('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_batch_commit_size(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_batch_commit_size_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_batch_commit_size(str(self.oversize['int_11']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_batch_commit_size(), str(self.oversize['int_11']))

    def test_web_config_update_condor_poller_delete_cycle_interval(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_delete_cycle_interval() 
        self.page.type_delete_cycle_interval('5')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_delete_cycle_interval(), '5')
        # reverse
        self.page.type_delete_cycle_interval(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_delete_cycle_interval_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_delete_cycle_interval('1.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_delete_cycle_interval(), '1.5')

    def test_web_config_update_condor_poller_delete_cycle_interval_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_delete_cycle_interval('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_delete_cycle_interval(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_delete_cycle_interval_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_delete_cycle_interval(str(self.oversize['bigint_20']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertFalse(self.page.get_value_delete_cycle_interval(), str(self.oversize['bigint_20']))

    def test_web_config_update_condor_poller_log_level(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_text_log_level() 
        self.page.select_log_level('WARNING')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_text_log_level(), 'WARNING')
        # reverse
        self.page.select_log_level(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_retire_interval(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_retire_interval() 
        self.page.type_retire_interval('1024')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_retire_interval(), '1024')
        # reverse
        self.page.type_retire_interval(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_retire_interval_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_retire_interval('1200.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_retire_interval(), '1200.5')

    def test_web_config_update_condor_poller_retire_interval_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_retire_interval('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_retire_interval(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_retire_interval_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_retire_interval(str(self.oversize['int_11']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.driver.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_retire_interval(), str(self.oversize['int_11']))

    def test_web_config_update_condor_poller_retire_off(self):
        self.page.click_side_button('condor_poller.py')
        self.page.click_retire_off()
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        # TODO: Assertion?
        #self.assertEqual(self.page.get_value_batch_commit_size(), '40')
        # reverse
        self.page.click_retire_off()
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_command(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_command() 
        self.page.type_sleep_interval_command('16')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_sleep_interval_command(), '16')
        # reverse
        self.page.type_sleep_interval_command(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_command_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_command('15.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_command(), '15.5')

    def test_web_config_update_condor_poller_sleep_interval_command_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_command('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_command(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_sleep_interval_command_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_command(str(self.oversize['int_11']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_command(), str(self.oversize['int_11']))

    def test_web_config_update_condor_poller_sleep_interval_condor_gsi(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_condor_gsi() 
        self.page.type_sleep_interval_condor_gsi('4096')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_sleep_interval_condor_gsi(), '4096')
        # reverse
        self.page.type_sleep_interval_condor_gsi(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_condor_gsi_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_condor_gsi('3600.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_condor_gsi(), '3600.5')

    def test_web_config_update_condor_poller_sleep_interval_condor_gsi_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_condor_gsi('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_condor_gsi(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_sleep_interval_condor_gsi_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_condor_gsi(str(self.oversize['int_11']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_condor_gsi(), str(self.oversize['int_11']))

    def test_web_config_update_condor_poller_sleep_interval_job(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_job() 
        self.page.type_sleep_interval_job('16')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_sleep_interval_job(), '16')
        # reverse
        self.page.type_sleep_interval_job(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_job_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_job('15.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_job(), '15.5')

    def test_web_config_update_condor_poller_sleep_interval_job_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_job('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_job(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_sleep_interval_job_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_job(str(self.oversize['int_11']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_job(), str(self.oversize['int_11']))

    def test_web_config_update_condor_poller_sleep_interval_machine(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_machine() 
        self.page.type_sleep_interval_machine('16')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_sleep_interval_machine(), '16')
        # reverse
        self.page.type_sleep_interval_machine(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_machine_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_machine('15.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_machine(), '15.5')

    def test_web_config_update_condor_poller_sleep_interval_machine_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_machine('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_machine(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_sleep_interval_machine_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_machine(str(self.oversize['int_11']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_machine(), str(self.oversize['int_11']))

    def test_web_config_update_condor_poller_sleep_interval_worker_gsi(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_worker_gsi() 
        self.page.type_sleep_interval_worker_gsi('4096')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertEqual(self.page.get_value_sleep_interval_worker_gsi(), '4096')
        # reverse
        self.page.type_sleep_interval_worker_gsi(original)
        self.page.click_update_config()


    def test_web_config_update_condor_poller_sleep_interval_worker_gsi_float(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_worker_gsi('3600.5')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_worker_gsi(), '3600.5')

    def test_web_config_update_condor_poller_sleep_interval_worker_gsi_string(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_worker_gsi('invalid-web-test')
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_condor_gsi(), 'invalid-web-test')

    @unittest.skip("No apparent maximum size")
    def test_web_config_update_condor_poller_sleep_interval_worker_gsi_too_big(self):
        self.page.click_side_button('condor_poller.py')
        self.page.type_sleep_interval_worker_gsi(str(self.oversize['int_11']))
        self.page.click_update_config()
        self.assertTrue(self.page.error_message_displayed())
        self.page.click_top_nav('Config')
        self.assertNotEqual(self.page.get_value_sleep_interval_worker_gsi(), str(self.oversize['int_11']))

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebConfigSuperUser(TestWebConfigCommon):
    """A class to test config operations via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['config'])
        print("\nConfig Tests:")

if __name__ == "__main__":
    unittest.main()
