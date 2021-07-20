# Web Test Templates

This file contains a set of templates for new testing files.

## test_web_page.py

This is a template for the testing file for a new page. "Page" is used in place of the page's name.

```python
if __name__ == "__main__":
    __package__ = 'cloudscheduler.unit_tests.web_tests'

import unittest
import sys
from . import web_test_setup_cleanup as wtsc
from . import web_test_assertions_v2 as wta
from . import web_test_page_objects as pages
from . import web_test_helpers as helpers

class TestWebPageCommon(unittest.TestCase):
    """A class for the page tests that should be repeated in all iterations."""

    @classmethod
    def setUpClass(cls):
        cls.page = pages.PagePage(cls.driver, cls.gvar['address'])
        cls.oversize = cls.gvar['oversize']

    def setUp(self):
        self.page.get_homepage()
        self.page.click_top_nav('Page')

    # tests go here
    # tests should be named test_web_page_<description>
        
    @classmethod
    def tearDownClass(cls):
        wtsc.cleanup(cls)

class TestWebPageSuperUserFirefox(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Firefox, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds'], browser='firefox')
            super(TestWebPageSuperUserFirefox, cls).setUpClass()
            print("\nPage Tests (Super User):")
        except:
            print("Error in test setup")
            super(TestWebPageSuperUserFirefox, cls).tearDownClass()
            raise

class TestWebPageRegularUserFirefox(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Firefox, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds'], browser='firefox')
            super(TestWebPageRegularUserFirefox, cls).setUpClass()
            print("\nPage Tests (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebPageRegularUserFirefox, cls).tearDownClass()
            raise

class TestWebPageSuperUserChromium(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Chromium, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds'], browser='chromium')
            super(TestWebPageSuperUserChromium, cls).setUpClass()
            print("\nPage Tests (Chromium) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebPageSuperUserChromium, cls).tearDownClass()
            raise

class TestWebPageRegularUserChromium(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Chromium, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds'], browser='chromium')
            super(TestWebPageRegularUserChromium, cls).setUpClass()
            print("\nPage Tests (Chromium) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebPageRegularUserChromium, cls).tearDownClass()
            raise

class TestWebPageSuperUserOpera(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Opera, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds'], browser='opera')
            super(TestWebPageSuperUserOpera, cls).setUpClass()
            print("\nPage Tests (Opera) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebPageSuperUserOpera, cls).tearDownClass()
            raise

class TestWebPageRegularUserOpera(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Opera, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds'], browser='opera')
            super(TestWebPageRegularUserOpera, cls).setUpClass()
            print("\nPage Tests (Opera) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebPageRegularUserOpera, cls).tearDownClass()
            raise

class TestWebPageSuperUserChrome(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Chrome, with a super user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 2, ['clouds', 'keys'], browser='chrome')
            super(TestWebPageSuperUserChrome, cls).setUpClass()
            print("\nPage Tests (Chrome) (Super User):")
        except:
            print("Error in test setup")
            super(TestWebPageSuperUserChrome, cls).tearDownClass()
            raise

class TestWebPageRegularUserChrome(TestWebPageCommon):
    """A class to test cloud operations via the web interface, in Chrome, with a regular user."""

    @classmethod
    def setUpClass(cls):
        try:
            wtsc.setup(cls, 1, ['clouds', 'keys'], browser='chrome')
            super(TestWebPageRegularUserChrome, cls).setUpClass()
            print("\nPage Tests (Chrome) (Regular User):")
        except:
            print("Error in test setup")
            super(TestWebPageRegularUserChrome, cls).tearDownClass()
            raise

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    tests = [ TestWebPageSuperUserFirefox, TestWebPageRegularUserFirefox,
              TestWebPageSuperUserChromium, TestWebPageRegularUserChromium,
              TestWebPageSuperUserOpera, TestWebPageRegularUserOpera,
              TestWebPageSuperUserChrome, TestWebPageRegularUserChrome ]
    suite = helpers.parse_command_line_arguments(sys.argv, tests, True)
    runner.run(suite)
```

## 