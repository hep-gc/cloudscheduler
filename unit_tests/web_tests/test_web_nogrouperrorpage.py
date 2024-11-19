if __name__ == "__main__":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers

class TestWebNoGroupErrorPageCommon(unittest.TestCase):
    """A class for the page tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.StatusPage(cls.driver, cls.gvar['address'])

    def setUp(self):
        # need to log in as user with no group here
        nogroup_user = {}
        nogroup_user['username'] = None
        nogroup_user['user_secret'] = None
        # log out from tester
        self.page.get_homepage()
        self.page.click_top_nav('Log out')
        self.assertTrue(self.page.page_blank())
        self.page.get_homepage_login(nogroup_user['username'], nogroup_user['user_secret'])

    # all tests start logged out 

    def test_web_nogrouperrorpage_login_redirected(self):
        # Tests that when logging in as a user with no group, 
        # you do not land on the status page
        assert True

    def test_web_nogrouperrorpage_login_page_content_present(self):
        # Tests whether the content of the no group error page is present
        assert True
        
    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebNoGroupErrorPageSuperUserFirefox(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds'], browser='firefox')
            super(TestWebNoGroupErrorPageSuperUserFirefox, cls).setUpClass()
            print("\nPage Tests (Super User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageSuperUserFirefox, cls).tearDownClass()
            raise

class TestWebNoGroupErrorPageRegularUserFirefox(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds'], browser='firefox')
            super(TestWebNoGroupErrorPageRegularUserFirefox, cls).setUpClass()
            print("\nPage Tests (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageRegularUserFirefox, cls).tearDownClass()
            raise

class TestWebNoGroupErrorPageSuperUserChromium(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds'], browser='chromium')
            super(TestWebNoGroupErrorPageSuperUserChromium, cls).setUpClass()
            print("\nPage Tests (Chromium) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageSuperUserChromium, cls).tearDownClass()
            raise

class TestWebNoGroupErrorPageRegularUserChromium(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds'], browser='chromium')
            super(TestWebNoGroupErrorPageRegularUserChromium, cls).setUpClass()
            print("\nPage Tests (Chromium) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageRegularUserChromium, cls).tearDownClass()
            raise

class TestWebNoGroupErrorPageSuperUserOpera(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds'], browser='opera')
            super(TestWebNoGroupErrorPageSuperUserOpera, cls).setUpClass()
            print("\nPage Tests (Opera) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageSuperUserOpera, cls).tearDownClass()
            raise

class TestWebNoGroupErrorPageRegularUserOpera(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds'], browser='opera')
            super(TestWebNoGroupErrorPageRegularUserOpera, cls).setUpClass()
            print("\nPage Tests (Opera) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageRegularUserOpera, cls).tearDownClass()
            raise

class TestWebNoGroupErrorPageSuperUserChrome(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds', 'keys'], browser='chrome')
            super(TestWebNoGroupErrorPageSuperUserChrome, cls).setUpClass()
            print("\nPage Tests (Chrome) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageSuperUserChrome, cls).tearDownClass()
            raise

class TestWebNoGroupErrorPageRegularUserChrome(TestWebNoGroupErrorPageCommon):
    """A class to test cloud operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds', 'keys'], browser='chrome')
            super(TestWebNoGroupErrorPageRegularUserChrome, cls).setUpClass()
            print("\nPage Tests (Chrome) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebNoGroupErrorPageRegularUserChrome, cls).tearDownClass()
            raise

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebNoGroupErrorPageSuperUserFirefox, TestWebNoGroupErrorPageRegularUserFirefox,
              TestWebNoGroupErrorPageSuperUserChromium, TestWebNoGroupErrorPageRegularUserChromium,
              TestWebNoGroupErrorPageSuperUserOpera, TestWebNoGroupErrorPageRegularUserOpera,
              TestWebNoGroupErrorPageSuperUserChrome, TestWebNoGroupErrorPageRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)