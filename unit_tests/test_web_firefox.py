import sys
import unittest
import web_tests.create_test_suite as tests

def main(gvar):
    #setup to run tests
    runner = unittest.TextTestRunner(verbosity=2)
    suite = tests.firefox_test_suite()
    runner.run(suite)
    #if unittest allows surfacing error numbers, uncomment and add assignments for skip/error
    #gvar['ut_count'][0] = suite.countTestCases()
    print()

if __name__ == "__main__":
    main(None)
