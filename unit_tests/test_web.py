import sys
import unittest
#import subprocess
import web_tests.create_test_suite

def main(gvar):
    #setup to run tests
    runner = unittest.TextTestRunner(verbosity=2)
    suite = web_tests.create_test_suite.test_suite()
    runner.run(suite)
    #if unittest allows surfacing error numbers, uncomment and add assignments for skip/error
    #gvar['ut_count'][0] = suite.countTestCases()
    print()

if __name__ == "__main__":
    main(None)
