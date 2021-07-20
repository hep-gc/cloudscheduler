if __name__ == "__main__" or __name__ == "test_web_misc":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers

class TestWebMiscCommon(unittest.TestCase):
    """A class for the miscellaneous tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.StatusPage(cls.driver, cls.gvar['address'])

    def setUp(self):
        self.page.get_homepage()

    def test_web_misc_logout(self):
        helpers.skip_if_browsers(self.gvar['browser'], ['firefox'])
        self.page.click_top_nav('Log out')
        self.assertTrue(self.page.page_blank())
        self.page.get_homepage_login(self.user, self.gvar['user_secret'])
        self.page.click_top_nav_with_login('Status', self.user, self.gvar['user_secret'])

    def test_web_misc_unauthorized(self):
        helpers.skip_if_browsers(self.gvar['browser'], ['chromium', 'opera', 'chrome'])
        self.page.click_top_nav('Log out')
        self.page.dismiss_login_prompt()
        self.assertTrue(self.page.error_page_displayed('Unauthorized'))
        self.page.get_homepage_login(self.user, self.gvar['user_secret'])
        self.page.click_top_nav_with_login('Status', self.user, self.gvar['user_secret'])

    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebMiscRegularUser(TestWebMiscCommon):
    """A class for the miscellaneous tests that should be done for regular users only."""

    def test_web_misc_no_header_group(self):
        self.assertFalse(self.page.top_nav_exists('Groups'))

    def test_web_misc_no_header_user(self):
        self.assertFalse(self.page.top_nav_exists('Users'))

    def test_web_misc_no_header_config(self):
        self.assertFalse(self.page.top_nav_exists('Config'))

class TestWebMiscSuperUserFirefox(TestWebMiscCommon):
    """A class to test miscellaneous operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, [], browser='firefox')
            super(TestWebMiscSuperUserFirefox, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu2'
            print("\nMiscellaneous Tests (Firefox) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebMiscSuperUserFirefox, cls).tearDownClass()
            raise

class TestWebMiscRegularUserFirefox(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, [], browser='firefox')
            super(TestWebMiscRegularUserFirefox, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu1'
            print("\nMiscellaneous Tests (Firefox) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebMiscRegularUserFirefox, cls).tearDownClass()
            raise

class TestWebMiscSuperUserChromium(TestWebMiscCommon):
    """A class to test miscellaneous operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, [], browser='chromium')
            super(TestWebMiscSuperUserChromium, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu2'
            print("\nMiscellaneous Tests (Chromium) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebMiscSuperUserChromium, cls).tearDownClass()
            raise

class TestWebMiscRegularUserChromium(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, [], browser='chromium')
            super(TestWebMiscRegularUserChromium, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu1'
            print("\nMiscellaneous Tests (Chromium) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebMiscRegularUserChromium, cls).tearDownClass()
            raise

class TestWebMiscSuperUserOpera(TestWebMiscCommon):
    """A class to test miscellaneous operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, [], browser='opera')
            super(TestWebMiscSuperUserOpera, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu2'
            print("\nMiscellaneous Tests (Opera) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebMiscSuperUserFirefox, cls).tearDownClass()
            raise

class TestWebMiscRegularUserOpera(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, [], browser='opera')
            super(TestWebMiscRegularUserOpera, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu1'
            print("\nMiscellaneous Tests (Opera) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebMiscRegularUserOpera, cls).tearDownClass()
            raise

class TestWebMiscSuperUserChrome(TestWebMiscCommon):
    """A class to test miscellaneous operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, [], browser='chrome')
            super(TestWebMiscSuperUserChrome, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu2'
            print("\nMiscellaneous Tests (Chrome) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebMiscSuperUserChrome, cls).tearDownClass()
            raise

class TestWebMiscRegularUserChrome(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, [], browser='chrome')
            super(TestWebMiscRegularUserChrome, cls).setUpClass()
            cls.user = cls.gvar['user'] + '-wiu1'
            print("\nMiscellaneous Tests (Chrome) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebMiscRegularUserChrome, cls).tearDownClass()
            raise

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebMiscSuperUserFirefox, TestWebMiscRegularUserFirefox,
              TestWebMiscSuperUserChromium, TestWebMiscRegularUserChromium,
              TestWebMiscSuperUserOpera, TestWebMiscRegularUserOpera,
              TestWebMiscSuperUserChrome, TestWebMiscRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
