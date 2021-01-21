import sys
import unittest
#import subprocess
import web_tests.create_test_suite

def main(gvar):
    #setup to run tests
    #subprocess.run(["python3", "-m", "unittest", "discover", "-s", "'web_tests'"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="/home/centos/cloudscheduler/unit_tests")
    #unittest.main()
    #web_tests.create_test_suite.test_suite().run(unittest.TextTestResult(sys.stdout, True, 1))
    runner = unittest.TextTestRunner()
    runner.run(web_tests.create_test_suite.test_suite())
    print()

if __name__ == "__main__":
    main(None)
