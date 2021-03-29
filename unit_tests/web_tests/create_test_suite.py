import unittest
import .test_web_group as group
import .test_web_user as user
import .test_web_cloud as cloud
import .test_web_alias as alias
import .test_web_default as default
import .test_web_image as image
import .test_web_setting as setting
import .test_web_config as config
import .test_web_key as key
import .test_web_status as status

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
        key.TestWebKeySuperUserFirefox,
        status.TestWebStatusSuperUserFirefox, status.TestWebStatusRegularUserFirefox
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
        key.TestWebKeySuperUserChromium,
        status.TestWebStatusSuperUserChromium, status.TestWebStatusRegularUserChromium
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
        key.TestWebKeySuperUserOpera,
        status.TestWebStatusSuperUserOpera, status.TestWebStatusRegularUserOpera
    ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite

