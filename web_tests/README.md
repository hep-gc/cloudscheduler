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

Do `pip install selenium` to get the Python Selenium bindings. Also do `pip install requests` and `pip install tox` to get the Selenium dependencies. Install [JDK](https://jdk.java.net/15/) from their website, following the instructions there (this install used JDK 15). Clone the [Selenium repo](https://github.com/SeleniumHQ/selenium) and the [geckodriver repo](https://github.com/mozilla/geckodriver).

[Bazelisk](https://github.com/bazelbuild/bazelisk) (a Selenium dependency) can be cloned from the repository and compiled with go, if your machine has go, or downloaded via `npm` using the command `npm install -g @bazel/bazelisk`.

Running `bazel build grid`, as suggested in the Selenium build instructions may cause EACCES errors regarding renaming - these can be fixed by manually renaming the files (there are about eight of them). I may attempt to find a way to automate this, as all of the renames involve a file called BUILD (possibly with an extension) being renamed to _BUILD (with the same extension, if applicable).

You can get geckodriver as a download from the [geckodriver github](https://github.com/mozilla/geckodriver/releases/tag/v0.28.0). You will need to have Firefox installed.

If you are on a virtual machine using an x11 connection, you might get this error:
```
WebDriverException: Message: Process unexpectedly closed with status 1
```
To fix this, run `export DISPLAY=:1` with the `Xvfb :1 -screen 0 1024x768x24` command running in another window.
