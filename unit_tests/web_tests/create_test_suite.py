import unittest
from .test_web_group import TestWebGroup

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestWebGroup))
    return suite
