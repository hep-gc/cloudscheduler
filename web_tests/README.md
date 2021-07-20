# Cloudscheduler Web Tests

This folder is for the web tests for cloudscheduler v2.

This document is an overview of the different testing frameworks currently under consideration for the web tests.

Note: this document is in the process of being rewritten. For progress on the new analysis document, look [here](/web_tests/additional_notes.md).

## General Setup Notes

Anything relevant to all the tests will be documented here. This includes features that were not tested that may be relevant and universal errors that are believed to be a result of running the tests on a virtual machine.

### Untested Features

Due to these tests being simplistic, in order to be able to try multiple frameworks easily, there are a lot of features that have not been sufficently tested. These include:

- switching tabs/windows

- multiple browsers (this was tested briefly, but is not currently in the test suite)

- complex click gestures (right-click, double-click, etc)

- condensing tests (many tests that use the same basic formula - these tests were essentially written independently)

- stubbing and mocking

- skipping tests

- complex selectors (select by text, etc)

- page models

- logins

### Universal Errors

All three of the frameworks tested, on a CentOS virtual machine using x11 forwarding via `xvfb`, would periodically get an error similar to the following (this one being from the Selenium-Unittest tests):
```
Traceback (most recent call last):
  File "sample-test.py", line 14, in setUp
    self.driver = webdriver.Firefox()
  File "/usr/lib/python2.7/site-packages/selenium/webdriver/firefox/webdriver.py", line 174, in __init__
    keep_alive=True)
  File "/usr/lib/python2.7/site-packages/selenium/webdriver/remote/webdriver.py", line 157, in __init__
    self.start_session(capabilities, browser_profile)
  File "/usr/lib/python2.7/site-packages/selenium/webdriver/remote/webdriver.py", line 252, in start_session
    response = self.execute(Command.NEW_SESSION, parameters)
  File "/usr/lib/python2.7/site-packages/selenium/webdriver/remote/webdriver.py", line 321, in execute
    self.error_handler.check_response(response)
  File "/usr/lib/python2.7/site-packages/selenium/webdriver/remote/errorhandler.py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
WebDriverException: Message: Process unexpectedly closed with status 1
```
This error is believed to be due to random failures in the x11 forwarding and was inconsistent. Rerunning the tests would usually get rid of it.

### Other Notes

There were five tests included in each of the test frameworks:

- a "canary" test - one that was obviously true and would only fail on a configuration error

- a "find object" test - one that went to Google and found the search bar

- a "type" test - one that went to Google and typed into the search bar

- a "search" test - one that went to Google, typed into the search bar, and searched using either the enter key or a submit method

- a "button search" test - one that went to DuckDuckGo (reasons in Selenium Universal Notes: Downsides), typed into the search bar, and searched using the search button

All three of the frameworks tested, according to their documentation, have browser support for Chrome/Chromium/Edge, Firefox, Internet Explorer, Safari, and Opera

## Selenium Universal Notes

[Selenium WebDriver](https://github.com/SeleniumHQ/selenium) is a widely-used WebDriver protocol.

### Benefits

Selenium is compatible with a large variety of languages and extensions and has been adapted, extended, and supported by a large variety of users.

### Downsides

Selenium is, comparatively, a large and complex install. The steps to get Selenium running are as follows:

- clone the [selenium repository](https://github.com/SeleniumHQ/selenium) from GitHub

- install the Python bindings and dependencies with `pip install selenium`, `pip install requests` and `pip install tox`

- get JDK from [their website](https://jdk.java.net/15/) or from your package manager (this install used `yum`)

- get Bazelisk using `npm install -g @bazel/bazelisk`

- if not already downloaded, get any browsers you need - this install used Firefox (and, temporarily, chromium)

- get any drivers you need - this install got geckodriver from [their GitHub](https://github.com/mozilla/geckodriver/releases/tag/v0.28.0) (and, temporarily, chromedriver via `yum`)

- run `bazelisk bazel build` in the selenium repository and deal with any rename requests as necessary (this install had roughly a dozen)

Selenium also appears to have an odd bug where it occasionally cannot detect elements that should be visible. As I currently cannot view tests as they are running, I cannot test whether this is actually a bug or poor writing in tests, but the TestCafe framework (below) didn't have the same difficulty. This bug showed up with the "Google Search" button on Google, both on Firefox and Chromium, but did not show up with the search button on DuckDuckGo.

## Selenium-Unittest Notes

[Unittest](https://docs.python.org/3.6/library/unittest.html#module-unittest) is a pre-installed Python testing framework. This implementation of it uses Selenium (above) to drive the browser.

The test file for Selenium and Unittest can be found [here](/web_tests/selenium-unittest/sample-test.py). The associated run command is `python sample-test.py`, run in the `selenium-unittest` directory.

### Benefits

Aside from the Selenium install, the Unittest install is essentially nonexistent - it comes bundled with Python3.

Unittest tests are, like the majority of the codebase, written in Python.

This implementation also inherits all the benefits of Selenium.

### Downsides

The unittest framework was the slowest of the three, running the tests in roughly thirty-one seconds.

This implementation also inherits all the downsides of Selenium.

## Selenium-Behave Notes

[Behave](https://github.com/behave/behave) is an external Gherkin language (similar to Cucumber) for Python tests. This implementation of it uses Selenium (above) to drive the browser.

The test files for Selenium and Behave can be found [here](/web_tests/selenium-behave/features/sample-test.feature) (for the feature/Gherkin file), [here](/web_tests/selenium-behave/features/steps/sample-test.py) (for the Python implementation of the Gherkin steps), and [here](/web_tests/selenium-behave/features/environment.py) (for the setup/teardown hooks). The associated run command is `behave`, run in the `selenium-behave` directory.

### Benefits

Aside from the Selenium install, the Behave install is fairly minimal - you only need to run `pip install behave`.

Behave creates incredibly readable tests - the feature files are written in nearly plain English, and the step files are broken down into short functions that, by necessity, have a plain English description of what they do attached to them. The step files are also, like the majority of the codebase, written in Python. Behave was my personal favourite of the three frameworks to write tests in.

Behave's design encourages, at least from my experience, the compartmentalization of tests and the sectioning off of commonly used steps to be reused. This is because it by design, splits tests into a string of small functions that often can be reused, especially in the setup steps.

The Behave tests ran fairly quickly, at roughly eighteen seconds.

This implementation also inherits all the benefits of Selenium.

### Downsides

This implementation also inherits all the downsides of Selenium.

## Testcafe Notes

[TestCafe](https://github.com/DevExpress/testcafe) is a newer browser driver. Tests are also written in TestCafe, in JavaScript.

The test file for TestCafe can be found [here](/web_tests/testcafe/sample-test.js). The associated run command is `testcafe firefox sample-test.js`, run from the `testcafe` directory.

### Benefits

The TestCafe install is very simple. You only need to run `npm install -g testcafe`.

The TestCafe tests were the fastest of all, running in roughly sixteen seconds.

### Downsides

TestCafe is written and extended exclusively in JavaScript, and all TestCafe tests must be written in JavaScript, making the tests somewhat more difficult to write and read.