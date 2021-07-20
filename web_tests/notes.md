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

You will need to include the line `import unittest` at the beginning of your spec files.

### Selenium

Do `pip install selenium` to get the Python Selenium bindings. Also do `pip install requests` and `pip install tox` to get the Selenium dependencies. Install [JDK](https://jdk.java.net/15/) from their website, following the instructions there (this install used JDK 15). Clone the [Selenium repo](https://github.com/SeleniumHQ/selenium) and the [geckodriver repo](https://github.com/mozilla/geckodriver).

[Bazelisk](https://github.com/bazelbuild/bazelisk) (a Selenium dependency) can be cloned from the repository and compiled with go, if your machine has go, or downloaded via `npm` using the command `npm install -g @bazel/bazelisk`.

Running `bazel build grid`, as suggested in the Selenium build instructions may cause EACCES errors regarding renaming - these can be fixed by manually renaming the files (there are about eight of them). I may attempt to find a way to automate this, as all of the renames involve a file called BUILD (possibly with an extension) being renamed to _BUILD (with the same extension, if applicable).

You can get geckodriver as a download from the [geckodriver github](https://github.com/mozilla/geckodriver/releases/tag/v0.28.0). You will need to have Firefox installed.

You can get chromium and chromedriver via `yum`. Chrome will not work on a CentOS machine, but will (obviously) work on other machines.

If you are on a virtual machine using an x11 connection, you might get this error:
```
WebDriverException: Message: Process unexpectedly closed with status 1
```
To fix this, run `export DISPLAY=:1` with the `Xvfb :1 -screen 0 1024x768x24` command running in another window.

Alternately, the screen can be created by prepending `xvfb-run` to the command that needs the screen. This will still generate the error. There's no way to escape it, you just have to rerun the tests if it appears.

You will need to include the line `from selenium import webdriver` at the beginning of your spec files, and possibly import other Selenium modules as necessary.

### Behave

To get behave, run `pip install behave` and put `from behave import *` at the beginning of your (python) spec files.

You'll also need to set up your directory with a `features` directory and a `features/steps` directory. The `features` directory needs at least one `*.feature` file and the `steps` directory needs at least one `*.py` file, although they don't have to have the same name.

## Framework Notes

### General Selenium Notes

Setup is pretty finicky.

Has an odd difficulty with pressing the "Google Search" button on Google - does not have this difficulty on DuckDuckGo.

### Selenium and Unittest

Setup was finicky, but that could be partly due to VM (and was pretty much entirely selenium - unittest was easy). Tests seem to be pretty flaky - how much of that is the VM and how much is Selenium is unknown at the moment.

Tests should be run with the `-v` flag to know what's going on.

Executes the tests in a little under thirty-one seconds.

### Selenium and Behave

Setup of behave was easy, but selenium setup was finicky, as mentioned above. Again, the tests seem to be flaky, but that could be the fault of the VM.

Behave is easier to read than unittest, both in code and in tests, but requires more files and a more specific setup structure. 

Executes the sample tests in a little over eighteen seconds.

### Testcafe

Setup was super easy. Flakiness continues, so I believe it is the fault of the VM. 

Difficult to read - also written in JavaScript, does not have a python option.

Executes the sample tests in roughly sixteen seconds. 
