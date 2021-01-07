# Cloudscheduler Web Tests

Status: doing analysis of various frameworks

## Frameworks

This section is a list and description of the frameworks currently being tested.

### Selenium and Behave

A testing framework using [Selenium WebDriver](https://github.com/SeleniumHQ/selenium) as the driver and [Behave](https://github.com/behave/behave) (a Python implementation similar to Cucumber) as the test-writing framework.

### Selenium and Unittest

A testing framework using [Selenium WebDriver](https://github.com/SeleniumHQ/selenium) as the driver and [Unittest](https://docs.python.org/3.6/library/unittest.html#module-unittest) as the test-writing framework.

### TestCafe

A testing framework using [TestCafe](https://github.com/DevExpress/testcafe) as both the driver and the test-writing framework.

## Install Notes

This section is a list of notes on how I did the various installs, and will hopefully become a guide to how to set the tests up on another machine.

### Unittest

Unittest is bundled with Python3 - no install is necessary.

### Selenium

Do `pip install selenium` to get the Python Selenium bindings. Also do `pip install requests` and `pip install tox` to get the Selenium dependencies. Install [JDK](https://jdk.java.net/15/) from their website, following the instructions there (this install used JDK 15). Clone the [Selenium repo](https://github.com/SeleniumHQ/selenium), the [geckodriver repo](https://github.com/mozilla/geckodriver) and the [Bazelisk repo](https://github.com/bazelbuild/bazelisk).