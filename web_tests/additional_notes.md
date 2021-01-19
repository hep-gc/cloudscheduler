# Framework Notes

This document is another, hopefully more comprehensive, set of notes on the comparative merits of the various testing frameworks. It draws on the notes in the [README](/web_tests/README.md) and the original [notes document](/web_tests/notes.md). 

Note: this document is a work in progress. To view the original analysis document, look [here](/web_tests/README.md).

## Selenium and Unittest

Selenium and Unittest uses Selenium WebDriver to drive the browser and unittest to build the test framework. Selenium WebDriver is a commonly used driver protocol, and unittest is a default python testing framework.

### Setup

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

TODO: Notes on the test results go here, including:

- speed of tests

- detail and readability of output

- ease of parsing output

## Selenium and Behave

Selenium and Behave uses Selenium WebDriver to drive the browser and behave to build the test framework. Selenium WebDriver is a commonly used driver protocol, and behave is a gherkin testing framework in python.

### Setup

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

TODO: Notes on the test results go here, including:

- speed of tests

- detail and readability of output

- ease of parsing output

## Testcafe

Testcafe is a self-contained web testing solution written and implemented entirely in JavaScript.

### Setup

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

TODO: Notes on the test results go here, including:

- speed of tests

- detail and readability of output

- ease of parsing output