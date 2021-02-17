import unittest
from .test_web_group import TestWebGroup
from .test_web_user import TestWebUser
from .test_web_cloud import TestWebCloudSuperUser, TestWebCloudRegularUser
from .test_web_alias import TestWebAliasSuperUser, TestWebAliasRegularUser
from .test_web_default import TestWebDefaultSuperUser

#IMPORTANT: All web tests must be added as suites here using `suite.addTest` in order for the `run_tests` script to pick them up
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebGroup))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebUser))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebCloudSuperUser))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebCloudRegularUser))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebAliasSuperUser))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebAliasRegularUser))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebDefaultSuperUser))
    return suite
