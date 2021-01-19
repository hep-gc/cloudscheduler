# Framework Notes

This document is another, hopefully more comprehensive, set of notes on the comparative merits of the various testing frameworks. It draws on the notes in the [README](/web_tests/README.md) and the original [notes document](/web_tests/notes.md). 

Note: this document is a work in progress. To view the original analysis document, look [here](/web_tests/README.md).

## Selenium and Unittest

Selenium and Unittest uses Selenium WebDriver to drive the browser and Unittest to build the test framework. Selenium WebDriver is a commonly used driver protocol, and Unittest is a default Python testing framework.

### Setup

This testing framework requires the Selenium bindings for Python, the Unittest framework, and the drivers for each browser.

Selenium requires a few different steps for installation. The Python bindings for Selenium, which allow Python to run drivers via WebDriver, can be installed from `pip` using the command `pip install selenium`. The driver installations are discussed below.

Unittest comes bundled with Python3 and needs no additional installation.

A test written in this framework is required to be a method within a class extending the `unittest.TestCase` class. The method must start with `test_` - other methods will not be run by the Unittest framework. 

Selenium also requires a different driver for each browser. Each driver has its own setup requirements.

#### Geckodriver

Geckodriver is the Firefox driver. It can be downloaded from the [Geckodriver GitHub](https://github.com/mozilla/geckodriver/releases) and turned into an executable via `tar`. It needs to be placed on the path to work.

#### Chromedriver

Chromedriver is the Chrome, Chromium, and Canary driver. It can be installed via `yum` (and, presumably, similar package managers).

### Writing Tests

At minimum, a test in this framework will require the following modules included at the top of each file: 
```python
import unittest
from selenium import webdriver
```

A test fixture is written as a class extending `unittest.TestCase`. Each test is a method that starts with `test_`. Tests are written as Python functions, and each one should contain a call to an `assert` method.

Unittest also has built-in `setUp` and `tearDown` functions for both test methods and test classes.

### Maintainability

Selenium and Unittest tests can be run with the command `python3 unittest -m`, or `python3 unittest -m discover -v`. This will automatically find all the test case files, import them, and run them. Specific test cases can be run using `python3 <filename>.py`, or groups all named in a certain style can be run with `python3 unittest -m discover -p <pattern_to_match>.py`. An individual test method can be run using `python3 unittest -m <module_name>.<class_name>.<method_name>`.

Adding tests to the Selenium and Unittest framework is fairly simple. The writer needs to create a new class extending `unittest.TestCase`. If the file is named to match the set pattern, it will be picked up automatically by `python3 unittest -m`. The file must be placed in the directory from which the tests are run.

Editing tests is, similarly, not a difficult process. A rational naming scheme can be used to make it easy to figure out which file a test would be in, and the test runner output gives the name of the function that is that particular test.

Of the three frameworks, Selenium and Unittest would be the least additional learning for someone looking to work on the web tests. Anyone working with Cloudscheduler would need to know Python, and anyone working with the unit tests would have used the Unittest module, meaning that Selenium is the only new portion of the tests that they would have to pick up.

Of the three systems, Selenium and Unittest would be the easiest to add to the existing test framework. Test Discovery should be able to find both the unit tests and the web tests if run from a directory containing both of them, making it relatively easy to run all of the tests in one command if desired.

### Results

The Selenium and Unittest tests were fairly slow in comparison to the other two frameworks, executing a sample set of tests in roughly thirty-one seconds. 

The results are fairly nondescript - a series of dots showing successful tests, or letters for failed or erroring tests. This can be improved by running the tests with the `-v` flag, which displays the name, location, docstring, and status of each test. 

Example (without `-v`):
```
.....
----------------------------------------------------------------------
Ran 5 tests in 45.750s

OK
```

Example (with `-v`):
```
test_canary (__main__.SampleTest)
The proverbial canary in the coal mine - if this fails, the setup is incorrect. ... ok
test_find_element (__main__.SampleTest)
Navigates to google and finds the search bar. ... ok
test_other_website (__main__.SampleTest)
Navigates to DuckDuckGo and searches. ... ok
test_submit (__main__.SampleTest)
Navigates to google, types in the search bar, and searches. ... ok
test_type_in_element (__main__.SampleTest)
Navigates to google and types in the search bar. ... ok

----------------------------------------------------------------------
Ran 5 tests in 39.143s

OK
```

The test framework prints a summary consisting of the number of tests run, the time taken, and whether the suite was successful or not.

## Selenium and Behave

Selenium and Behave uses Selenium WebDriver to drive the browser and Behave to build the test framework. Selenium WebDriver is a commonly used driver protocol, and Behave is a Gherkin testing framework in Python.

### Setup

This testing framework requires the Selenium bindings for Python, the Behave module, and the drivers for each browser.

Selenium requires a few different steps for installation. The Python bindings for Selenium, which allow Python to run drivers via WebDriver, can be installed from `pip` using the command `pip install selenium`. The driver installations are discussed below.

Behave can be installed via pip, with the command `pip install behave`.

Behave tests have a particular directory setup requirement. All tests are written as feature files, a type of near-English Gherkin file with the extension `.feature`, and must be in a directory called `features`. All of the code implementations of the steps in the feature files must be in a directory called `steps` within the `features` directory. These files must have the `.py` extension. 

Behave configurations, including setup and takedown methods, must be in a file called `environment.py`, in the `features` directory.

#### Geckodriver

Geckodriver is the Firefox driver. It can be downloaded from the [Geckodriver GitHub](https://github.com/mozilla/geckodriver/releases) and turned into an executable via `tar`. It needs to be placed on the path to work.

#### Chromedriver

Chromedriver is the Chrome, Chromium, and Canary driver. It can be installed via `yum` (and, presumably, similar package managers).

### Writing Tests

Behave tests are written in two parts. In the `.feature` file in the `features` directory, the test should be written in the Gherkin syntax:
```gherkin
Scenario: <description>
    Given <initial conditions>
    When <user takes an action>
    Then <result that should occur>
```

The files in the `steps` directory should start with the following:
```
from behave import *
from selenium import webdriver
```

Each step is a Python method prefaced with the keyword and then the plaintext string like so:
```python
@given('<initial conditions>')
def step_impl:
    pass
```

Steps can be in any file the writer chooses, so long as it is a `.py` file in the `steps` directory. There can, additionally, be as many `.feature` files as the writer chooses.

### Maintainability

Selenium and Behave tests can be run, simply, with the command `behave`. An individual feature file can be run with the command `behave <filename>.feature`. To run groups of tests, the tests should be tagged in the feature file by writing `@<tag>` before them. All tests with a particular tag can be run with `behave --tags=@<tag>`. Also, any feature files matching a pattern can be run with `behave -i <regex>`. A particular feature matching a name regex can be run with `behave -n <regex>`.

Adding tests to the framework is a mildly complex procedure. The test should first be written in a `.feature` file, then each step should be written in a `.py` file (although steps from other tests can be reused). However, assuming these files are placed in the correct place, Behave will automatically find and run the tests.

Editing tests is somewhat difficult. To find a test, one needs to find its plaintext string associated with the correct tag (`@given`, `@when`, or `@then`), which can be complicated by the "And" and "But" keywords, which take on the previous tag in the order. Realistically, editing tests requires switching back and forth between the feature files and the step files to find such information as where else a certain step is used.

Behave has a middling amount of additional learning required. The implementations of the code are written in Python, which anyone working on Cloudscheduler would know. However, anyone looking to work on the web tests would need to learn Selenium. They would also need to learn the Gherkin syntax, although Gherkin is fairly similar to plain English.

Selenium and Behave would be somewhat difficult to integrate with the existing test framework. Both are written in Python, so it is feasible that somehow one could be set up to use code from the other, but it would probably be a difficult procedure.

### Results

The Selenium and Behave tests were relatively quick, running a set of sample tests in roughly eighteen seconds.

The test results are fairly detailed - each plaintext step is printed to the screen as it is started. A successful step will turn green, a failed step will turn red, and a skipped step (usually due to a failure earlier in the test) will turn a darker grey. 

The test framework prints a summary with the number of features passed, failed, and skipped; the number of scenarios passed, failed, and skipped; the number of steps passed, failed, skipped, and undefined; and the time taken.

Example:
```
Feature: Sample tests # features/sample-test.feature:1
  A few small, simple tests as a trial run for selenium and behave.
  Scenario: We run a canary test           # features/sample-test.feature:4
    Given we have done the setup correctly # features/steps/sample-test.py:8 0.000s
    When we run a simple test              # features/steps/sample-test.py:12 0.000s
    Then it will pass                      # features/steps/sample-test.py:16 0.000s

  Scenario: We find Google            # features/sample-test.feature:9
    Given we have our browser set up  # features/steps/sample-test.py:20 3.320s
    When we navigate to Google        # features/steps/sample-test.py:24 2.845s
    Then there should be a search bar # features/steps/sample-test.py:28 0.019s

  Scenario: We interact with the search bar  # features/sample-test.feature:14
    Given we have our browser set up         # features/steps/sample-test.py:20 3.088s
    And we are on Google                     # features/steps/sample-test.py:33 2.850s
    When we type in the search bar           # features/steps/sample-test.py:37 0.142s
    Then we should be successful             # features/steps/sample-test.py:42 0.000s

  Scenario: We make a search         # features/sample-test.feature:20
    Given we have our browser set up # features/steps/sample-test.py:20 2.974s
    And we are on Google             # features/steps/sample-test.py:33 2.822s
    When we type in the search bar   # features/steps/sample-test.py:37 0.147s
    And we search                    # features/steps/sample-test.py:46 0.034s
    Then we should be successful     # features/steps/sample-test.py:42 0.000s

  Scenario: We make a search on DuckDuckGo  # features/sample-test.feature:27
    Given we have our browser set up        # features/steps/sample-test.py:20 3.181s
    And we are on DuckDuckGo                # features/steps/sample-test.py:50 0.873s
    When we type in the search bar          # features/steps/sample-test.py:37 0.094s
    And we search with the search button    # features/steps/sample-test.py:54 1.504s
    Then we should be successful            # features/steps/sample-test.py:42 0.000s

1 feature passed, 0 failed, 0 skipped
5 scenarios passed, 0 failed, 0 skipped
20 steps passed, 0 failed, 0 skipped, 0 undefined
Took 0m23.894s
```

## TestCafe

TestCafe is a self-contained web testing solution written and implemented entirely in JavaScript.

### Setup

This framework requires the TestCafe package.

TestCafe is a fairly simple setup. It can be installed from `npm` (which may or may not be on the machine already - if not, it can be installed via the default package manager) using the command `npm install -g testcafe`.

A test written in this framework is required to be part of a fixture and to be a function called `test`.

### Writing Tests

A test written in TestCafe will require the following lines at the beginning:
```javascript
import { Selector } from 'testcafe';

fixture `<fixture name>`;
```

Tests are written in JavaScript, unlike the majority of the codebase, and are `test()` methods. 

### Maintainability

TestCafe tests can be run with the command `testcafe <browser> <test-folder>`. An individual file can be run with the command `testcafe <browser> <filename>.js`. All tests named in a certain style can be run using `testcafe <browser> <pattern>`. An individual test can be run with `testcafe <browser> <filename>.js -t "<testname>"`.

Adding new TestCafe tests is not particularly difficult. The writer needs to create a fixture file, as above, and add tests as above. If these tests are placed in the correct folder, TestCafe should be able to find them.

Editing tests is a relatively simple process. Each test has the name that is displayed on the test framework written at the beginning of the test, and the fixture name is listed at the beginning of the tests, so they are fairly easy to find.

Of the three test frameworks, TestCafe has the highest amount of additional learning required for someone new to the test suite. TestCafe is written exclusively in JavaScript, meaning that anyone who wants to work with the web tests would be required to learn JavaScript, which is not commonly used elsewhere in the codebase. 

TestCafe would be virtually impossible to integrate with the current testing framework. As it is written in an entirely different language, the tests are completely incompatible with each other. The only obvious way to combine them would be a shell script designed to run both.

### Results

The TestCafe tests were fairly quick, running a set of sample tests in roughly sixteen seconds. However, the TestCafe tests, unlike the other two, did not spin up a new browser in between tests, which is possible in the others and would have presumably shortened their execution times.

The test results provide some information - each test's description, with a check mark or an X printed next to it.

The test framework prints a summary with the number of tests passed and the time taken to run them.

Example:
```
 Running tests in:
 - Firefox 78.0 / Linux 0.0

 Sample Tests
 ✓ Canary test
 ✓ Finding search bar
 ✓ Typing in the search bar
 ✓ Searching
 ✓ Accessing a different website


 5 passed (18s)
```