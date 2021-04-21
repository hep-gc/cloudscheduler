import unittest

# The classes in this module piggyback off of the existing TextTestRunner and
# TextTestResult classes, but add functionality to pass error numbers back to
# the run_tests script.

class Csv2TestRunner(unittest.TextTestRunner):
    def __init__(self, stream=None, descriptions=True, verbosity=1, failfast=False, buffer=False, resultclass=None, warnings=None, *, tb_locals=False, gvar=None):
        super(Csv2TestRunner, self).__init__(stream=stream, descriptions=descriptions, verbosity=verbosity, failfast=failfast, buffer=buffer, resultclass=resultclass, warnings=warnings, tb_locals=tb_locals)
        self.gvar = gvar

    def _makeResult(self):
        if self.gvar:
            return Csv2TestResult(self.stream, self.descriptions, self.verbosity, gvar=self.gvar)
        else:
            return unittest.TextTestResult(self.stream, self.descriptions, self.verbosity)

class Csv2TestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity, gvar):
        super(Csv2TestResult, self).__init__(stream=stream, descriptions=descriptions, verbosity=verbosity)
        self.gvar = gvar

    def addError(self, test, err):
        super(Csv2TestResult, self).addError(test, err)
        self.gvar['ut_count'][0] += 1
        self.gvar['ut_failed'] += 1

    def addFailure(self, test, err):
        super(Csv2TestResult, self).addFailure(test, err)
        self.gvar['ut_count'][0] += 1
        self.gvar['ut_failed'] += 1

    def addSuccess(self, test):
        super(Csv2TestResult, self).addSuccess(test)
        self.gvar['ut_count'][0] += 1

    def addSkip(self, test, reason):
        super(Csv2TestResult, self).addSkip(test, reason)
        self.gvar['ut_count'][0] += 1
        self.gvar['ut_skipped'] += 1

    def addExpectedFailure(self, test, err):
        super(Csv2TestResult, self).addExpectedFailure(test, err)
        self.gvar['ut_count'][0] += 1

    def addUnexpectedSuccess(self, test):
        super(Csv2TestResult, self).addUnexpectedSuccess(test)
        self.gvar['ut_count'][0] += 1
        self.gvar['ut_failed'] += 1

    def addSubTest(self, test, subtest, outcome):
        super(Csv2TestResult, self).addSubTest(test, subtest, outcome)
        self.gvar['ut_count'][0] += 1
        if outcome:
            self.gvar['ut_failed'] += 1
