# Framework Notes

This document is another, hopefully more comprehensive, set of notes on the comparative merits of the various testing frameworks. It draws on the notes in the [README](/web_tests/README.md) and the original [notes document](/web_tests/notes.md). 

Note: this document is a work in progress. To view the original analysis document, look [here](/web_tests/README.md).

## Selenium and Unittest

Selenium and Unittest uses Selenium WebDriver to drive the browser and unittest to build the test framework. Selenium WebDriver is a commonly used driver protocol, and unittest is a default python testing framework.

### Setup

This testing framework requires the Selenium bindings for Python, the unittest framework, and the drivers for each browser.

Selenium requires a few different steps for installation. The Python bindings for Selenium, which allow Python to run drivers via WebDriver, can be installed from `pip` using the command `pip install selenium`. The driver installations are discussed below.

Unittest comes bundled with Python3 and needs no additional installation.

A test written in this framework is required to be a method within a class extending the `unittest.TestCase` class. The method must start with `test_` - other methods will not be run by the unittest framework. 

Selenium also requires a different driver for each browser. Each driver has its own setup requirements.

#### Geckodriver

Geckodriver is the Firefox driver. It can be downloaded from the [geckodriver GitHub](https://github.com/mozilla/geckodriver/releases) and turned into an executable via `tar`. It needs to be placed on the path to work.

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

TODO: Notes on the maintainability of tests go here, including:

- editing tests

- adding new tests

- explaining the tests for new employees

- ease of running tests

- combining tests with current testing framework

### Results

The Selenium and unittest tests were fairly slow in comparison to the other two frameworks, executing a sample set of tests in roughly thirty-one seconds. 

The results are fairly nondescript - a series of dots showing successful tests, or letters for failed or erroring tests. This can be improved by running the tests with the `-v` flag. 

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

Selenium and Behave uses Selenium WebDriver to drive the browser and behave to build the test framework. Selenium WebDriver is a commonly used driver protocol, and behave is a gherkin testing framework in python.

### Setup

This testing framework requires the Selenium bindings for Python, the behave module, and the drivers for each browser.

Selenium requires a few different steps for installation. The Python bindings for Selenium, which allow Python to run drivers via WebDriver, can be installed from `pip` using the command `pip install selenium`. The driver installations are discussed below.

Behave can be installed via pip, with the command `pip install behave`.

Behave tests have a particular directory setup requirement. All tests are written as feature files, a type of near-English gherkin file with the extension `.feature`, and must be in a directory called `features`. All of the code implementations of the steps in the feature files must be in a directory called `steps` within the `features` directory. These files must have the `.py` extension. 

Behave configurations, including setup and takedown methods, must be in a file called `environment.py`, in the `features` directory.

#### Geckodriver

Geckodriver is the Firefox driver. It can be downloaded from the [geckodriver GitHub](https://github.com/mozilla/geckodriver/releases) and turned into an executable via `tar`. It needs to be placed on the path to work.

#### Chromedriver

Chromedriver is the Chrome, Chromium, and Canary driver. It can be installed via `yum` (and, presumably, similar package managers).

### Writing Tests

Behave tests are written in two parts. In the `.feature` file in the `features` directory, the test should be written in the gherkin syntax:
```
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

TODO: Notes on the maintainability of tests go here, including:

- editing tests

- adding new tests

- explaining the tests for new employees

- ease of running tests

- combining tests with current testing framework

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

## Testcafe

Testcafe is a self-contained web testing solution written and implemented entirely in JavaScript.

### Setup

This framework requires the testcafe package.

Testcafe is a fairly simple setup. It can be installed from `npm` (which may or may not be on the machine already - if not, it can be installed via the default package manager) using the command `npm install -g testcafe`.

A test written in this framework is required to be part of a fixture and to be a function called `test`.

### Writing Tests

A test written in Testcafe will require the following lines at the beginning:
```javascript
import { Selector } from 'testcafe';

fixture `<fixture name>`
    .page `<url-of-start-page>`;
```

Tests are written in JavaScript, unlike the majority of the codebase, and are `test()` methods. 

### Maintainability

TODO: Notes on the maintainability of tests go here, including:

- editing tests

- adding new tests

- explaining the tests for new employees

- ease of running tests

- combining tests with current testing framework

### Results

The Testcafe tests were fairly quick, running a set of sample tests in roughly sixteen seconds. However, the Testcafe tests, unlike the other two, did not spin up a new browser in between tests.

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