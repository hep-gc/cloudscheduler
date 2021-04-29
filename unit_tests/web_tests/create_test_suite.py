import unittest
from . import test_web_group as group
from . import test_web_user as user
from . import test_web_cloud as cloud
from . import test_web_alias as alias
from . import test_web_default as default
from . import test_web_image as image
from . import test_web_setting as setting
from . import test_web_config as config
from . import test_web_key as key
from . import test_web_status as status
from . import test_web_misc as misc

#IMPORTANT: All web tests must be added to the `tests` array in the appropriate browser's test suite in order for the `run_tests` script to pick them up
def firefox_test_suite():
    tests = [
        group.TestWebGroupSuperUserFirefox,
        user.TestWebUserSuperUserFirefox,
        cloud.TestWebCloudSuperUserFirefox, cloud.TestWebCloudRegularUserFirefox,
        alias.TestWebAliasSuperUserFirefox, alias.TestWebAliasRegularUserFirefox,
        default.TestWebDefaultSuperUserFirefox, default.TestWebDefaultRegularUserFirefox,
        image.TestWebImageSuperUserFirefox, image.TestWebImageRegularUserFirefox,
        setting.TestWebSettingSuperUserFirefox, setting.TestWebSettingRegularUserFirefox,
        config.TestWebConfigSuperUserFirefox,
        key.TestWebKeySuperUserFirefox, key.TestWebKeyRegularUserFirefox,
        status.TestWebStatusSuperUserFirefox, status.TestWebStatusRegularUserFirefox,
        misc.TestWebMiscSuperUserFirefox, misc.TestWebMiscRegularUserFirefox
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

def chromium_test_suite():
    tests = [
        group.TestWebGroupSuperUserChromium,
        user.TestWebUserSuperUserChromium,
        cloud.TestWebCloudSuperUserChromium, cloud.TestWebCloudRegularUserChromium,
        alias.TestWebAliasSuperUserChromium, alias.TestWebAliasRegularUserChromium,
        default.TestWebDefaultSuperUserChromium, default.TestWebDefaultRegularUserChromium,
        image.TestWebImageSuperUserChromium, image.TestWebImageRegularUserChromium,
        setting.TestWebSettingSuperUserChromium, setting.TestWebSettingRegularUserChromium,
        config.TestWebConfigSuperUserChromium,
        key.TestWebKeySuperUserChromium, key.TestWebKeyRegularUserChromium,
        status.TestWebStatusSuperUserChromium, status.TestWebStatusRegularUserChromium,
        misc.TestWebMiscSuperUserChromium, misc.TestWebMiscRegularUserChromium
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

def opera_test_suite():
    tests = [
        group.TestWebGroupSuperUserOpera,
        user.TestWebUserSuperUserOpera,
        cloud.TestWebCloudSuperUserOpera, cloud.TestWebCloudRegularUserOpera,
        alias.TestWebAliasSuperUserOpera, alias.TestWebAliasRegularUserOpera,
        default.TestWebDefaultSuperUserOpera, default.TestWebDefaultRegularUserOpera,
        image.TestWebImageSuperUserOpera, image.TestWebImageRegularUserOpera,
        setting.TestWebSettingSuperUserOpera, setting.TestWebSettingRegularUserOpera,
        config.TestWebConfigSuperUserOpera,
        key.TestWebKeySuperUserOpera, key.TestWebKeyRegularUserOpera,
        status.TestWebStatusSuperUserOpera, status.TestWebStatusRegularUserOpera,
        misc.TestWebMiscSuperUserOpera, misc.TestWebMiscRegularUserOpera
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

def chrome_test_suite():
    tests = [
        group.TestWebGroupSuperUserChrome,
        user.TestWebUserSuperUserChrome,
        cloud.TestWebCloudSuperUserChrome, cloud.TestWebCloudRegularUserChrome,
        alias.TestWebAliasSuperUserChrome, alias.TestWebAliasRegularUserChrome,
        default.TestWebDefaultSuperUserChrome, default.TestWebDefaultRegularUserChrome,
        image.TestWebImageSuperUserChrome, image.TestWebImageRegularUserChrome,
        setting.TestWebSettingSuperUserChrome, setting.TestWebSettingRegularUserChrome,
        config.TestWebConfigSuperUserChrome,
        key.TestWebKeySuperUserChrome, key.TestWebKeyRegularUserChrome,
        status.TestWebStatusSuperUserChrome, status.TestWebStatusRegularUserChrome,
        misc.TestWebMiscSuperUserChrome, misc.TestWebMiscRegularUserChrome
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

# A small, sample test suite for testing the run_tests framework
# This suite should not be included in any tests - it only contains duplicates
def test_test_suite():
    tests = [
        status.TestWebStatusRegularUserFirefox
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite
