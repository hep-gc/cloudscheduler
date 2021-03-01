import unittest
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages

class TestWebConfig(unittest.TestCase):
    """A class to test config operatiohns via the web interface."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, ['config'])
        cls.page = pages.ConfigPage(cls.driver)
        cls.oversize = cls.gvar['oversize']
        print("\nConfig Tests:")

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

    def test_web_config_update_condor_poller_batch_commit_size(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_batch_commit_size() 
        self.page.type_batch_commit_size('40')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.assertEqual(self.page.get_value_batch_commit_size(), '40')
        # reverse
        self.page.type_batch_commit_size(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_delete_cycle_interval(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_delete_cycle_interval() 
        self.page.type_delete_cycle_interval('5')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.assertEqual(self.page.get_value_delete_cycle_interval(), '5')
        # reverse
        self.page.type_delete_cycle_interval(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_log_level(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_text_log_level() 
        self.page.select_log_level('WARNING')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
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
        self.assertEqual(self.page.get_value_retire_interval(), '1024')
        # reverse
        self.page.type_retire_interval(original)
        self.page.click_update_config()

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
        self.assertEqual(self.page.get_value_sleep_interval_command(), '16')
        # reverse
        self.page.type_sleep_interval_command(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_condor_gsi(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_condor_gsi() 
        self.page.type_sleep_interval_condor_gsi('4096')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.assertEqual(self.page.get_value_sleep_interval_condor_gsi(), '4096')
        # reverse
        self.page.type_sleep_interval_condor_gsi(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_job(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_job() 
        self.page.type_sleep_interval_job('16')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.assertEqual(self.page.get_value_sleep_interval_job(), '16')
        # reverse
        self.page.type_sleep_interval_job(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_machine(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_machine() 
        self.page.type_sleep_interval_machine('16')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.assertEqual(self.page.get_value_sleep_interval_machine(), '16')
        # reverse
        self.page.type_sleep_interval_machine(original)
        self.page.click_update_config()

    def test_web_config_update_condor_poller_sleep_interval_worker_gsi(self):
        self.page.click_side_button('condor_poller.py')
        original = self.page.get_value_sleep_interval_worker_gsi() 
        self.page.type_sleep_interval_worker_gsi('4096')
        self.page.click_update_config()
        self.assertFalse(self.page.error_message_displayed())
        self.assertEqual(self.page.get_value_sleep_interval_worker_gsi(), '4096')
        # reverse
        self.page.type_sleep_interval_worker_gsi(original)
        self.page.click_update_config()

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

if __name__ == "__main__":
    unittest.main()
