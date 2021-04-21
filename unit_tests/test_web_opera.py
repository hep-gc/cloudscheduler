import sys
import web_tests.create_test_suite as tests
import web_tests.csv2_runner as csv2_runner

def main(gvar):
    # setup to run Opera tests
    runner = csv2_runner.Csv2TestRunner(verbosity=2, gvar=gvar)
    suite = tests.opera_test_suite()
    runner.run(suite)
    print()

if __name__ == "__main__":
    main(None)
