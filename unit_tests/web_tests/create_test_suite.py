import unittest
from .test_web_group import TestWebGroup

#IMPORTANT: All web tests must be added as suites here using `suite.addTest` in order for the `run_tests` script to pick them up
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebGroup))
    return suite
