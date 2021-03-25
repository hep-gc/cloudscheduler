import unittest
from .test_web_group import TestWebGroupSuperUser, TestWebGroupSuperUserChromium, TestWebGroupSuperUserOpera
from .test_web_user import TestWebUserSuperUser
from .test_web_cloud import TestWebCloudSuperUser, TestWebCloudRegularUser
from .test_web_alias import TestWebAliasSuperUser, TestWebAliasRegularUser
from .test_web_default import TestWebDefaultSuperUser, TestWebDefaultRegularUser
from .test_web_image import TestWebImageSuperUser, TestWebImageRegularUser
from .test_web_setting import TestWebSettingSuperUser, TestWebSettingRegularUser
from .test_web_config import TestWebConfigSuperUser
from .test_web_key import TestWebKeySuperUser
from .test_web_status import TestWebStatusSuperUser

#IMPORTANT: All web tests must be added to the `tests` array in the appropriate browser's test suite in order for the `run_tests` script to pick them up
def firefox_test_suite():
    tests = [
        TestWebGroupSuperUser
        #TestWebUserSuperUser,
        #TestWebCloudSuperUser, TestWebCloudRegularUser,
        #TestWebAliasSuperUser, TestWebAliasRegularUser,
        #TestWebDefaultSuperUser, TestWebDefaultRegularUser,
        #TestWebImageSuperUser, TestWebImageRegularUser,
        #TestWebSettingSuperUser, TestWebSettingRegularUser,
        #TestWebConfigSuperUser,
        #TestWebKeySuperUser,
        #TestWebStatusSuperUser
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

def chromium_test_suite():
    tests = [
        TestWebGroupSuperUserChromium
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

def opera_test_suite():
    tests = [
        TestWebGroupSuperUserOpera
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

