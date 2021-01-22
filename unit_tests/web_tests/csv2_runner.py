import unittest

class csv2TestResult(unittest.TextTestResult):
    def addError(test, err, gvar):
         unittest.TextTestResult(test, err)
         gvar['ut_count'] += 1
         gvar['ut_failed'] += 1

    def addFailure(test, err, gvar):
         
