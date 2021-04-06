import sys
import unittest
import web_tests.create_test_suite as tests

def main(gvar):
    # setup to run Chrome tests
    runner = unittest.TextTestRunner(verbosity=2)
    suite = tests.chrome_test_suite()
    runner.run(suite)
    print()

if __name__ == "__main__":
    main(None)
