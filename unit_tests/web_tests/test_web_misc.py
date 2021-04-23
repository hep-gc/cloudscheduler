import unittest
import sys
import web_tests.web_test_setup_cleanup as wtsc
import web_tests.web_test_assertions_v2 as wta
import web_tests.web_test_page_objects as pages
import web_tests.web_test_helpers as helpers

class TestWebMiscCommon(unittest.TestCase):
    """A class for the miscellaneous tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.StatusPage(cls.driver)

    def setUp(self):
        helpers.get_homepage(self.driver)

    def test_web_misc_find(self):
        pass

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
        wtsc.setup(cls, 2, [], browser='firefox')
        super(TestWebMiscSuperUserFirefox, cls).setUpClass()
        print("\nMiscellaneous Tests (Firefox) (Super User):")

class TestWebMiscRegularUserFirefox(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, [], browser='firefox')
        super(TestWebMiscRegularUserFirefox, cls).setUpClass()
        print("\nMiscellaneous Tests (Firefox) (Regular User):")

class TestWebMiscSuperUserChromium(TestWebMiscCommon):
    """A class to test miscellaneous operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, [], browser='chromium')
        super(TestWebMiscSuperUserChromium, cls).setUpClass()
        print("\nMiscellaneous Tests (Chromium) (Super User):")

class TestWebMiscRegularUserChromium(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, [], browser='chromium')
        super(TestWebMiscRegularUserChromium, cls).setUpClass()
        print("\nMiscellaneous Tests (Chromium) (Regular User):")

class TestWebMiscSuperUserOpera(TestWebMiscCommon):
    """A class to test miscellaneous operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, [], browser='opera')
        super(TestWebMiscSuperUserOpera, cls).setUpClass()
        print("\nMiscellaneous Tests (Opera) (Super User):")

class TestWebMiscRegularUserOpera(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, [], browser='opera')
        super(TestWebMiscRegularUserOpera, cls).setUpClass()
        print("\nMiscellaneous Tests (Opera) (Regular User):")

class TestWebMiscSuperUserChrome(TestWebMiscCommon):
    """A class to test miscellaneous operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 2, [], browser='chrome')
        super(TestWebMiscSuperUserChrome, cls).setUpClass()
        print("\nMiscellaneous Tests (Chrome) (Super User):")

class TestWebMiscRegularUserChrome(TestWebMiscRegularUser):
    """A class to test miscellaneous operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        wtsc.setup(cls, 1, [], browser='chrome')
        super(TestWebMiscRegularUserChrome, cls).setUpClass()
        print("\nMiscellaneous Tests (Chrome) (Regular User):")

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebMiscSuperUserFirefox, TestWebMiscRegularUserFirefox,
              TestWebMiscSuperUserChromium, TestWebMiscRegularUserChromium,
              TestWebMiscSuperUserOpera, TestWebMiscRegularUserOpera,
              TestWebMiscSuperUserChrome, TestWebMiscRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
