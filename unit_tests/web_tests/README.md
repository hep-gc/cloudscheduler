# Running the Web Tests

This document is the primary source of information on the web testing framework.

To run the tests, follow the [setup](#setup) instructions, then use the instructions at the beginning of [Running Tests](#running-tests) to run the tests.

To develop tests, start with the above, then read the remainder of the document to understand how the tests are designed and set up. This document also contains a list of [todos and possible future features](#future-features-todos) for developers.

Note that unless web tests are specifically excluded from the command, web tests will be run as part of the `run_tests` framework. In order to run the entirety of that framework, the web tests must be set up as in the [setup section](#setup).

## Setup

This section covers the steps to install the necessary web test components. [Python and Selenium](#python-and-selenium), [Testing Files](#testing-files), and [#Firefox and Geckodriver](#firefox-and-geckodriver) are needed for tests with any browser. [Chromium and Chromedriver](#chromium-and-chromedriver) and [Opera and OperaChromiumDriver](#opera-and-operachromiumdriver) are needed for tests in their respective browsers, and for the full `run_tests` script.

Additionally, all the setup in [Other Setup](#other-setup) should be completed for all the tests.

### Python and Selenium

The web tests require Python3 and the Python Selenium bindings to run.

Install `python3` using your default package manager. Selenium Webdriver for Python can then be installed via `pip3 install selenium`.

### Testing Files

The tests require four images in RAW format and two ssh keys for upload purposes.

Download a [CernVM image](http://cernvm.cern.ch/releases/production/cernvm4-micro-2020.07-1.hdd) and move it to the `misc_files` directory (unit_tests/web_tests/misc_files). Rename it `{user}-wii1.hdd`. Create three copies of it, called `{user}-wii2.hdd`, `{user}-wii3.hdd`, and `{user}-wii4.hdd`.

Create a public key using `ssh-keygen`. Name it `{user}-wik3` and put it in the `misc_files` directory. Do not use a passphrase. Create another public key in the same manner, naming it `invalid-web-test`.

### Firefox and Geckodriver

Geckodriver can be downloaded from [GitHub](https://github.com/mozilla/geckodriver/releases/tag/v0.28.0). Firefox comes preinstalled on Linux machines, or can be downloaded from [Mozilla](https://www.mozilla.org/en-CA/firefox/new/).

### Chromium and Chromedriver

Chromedriver and Chromium can be installed through the default package manager. 

Note that the tests have been set up and tested using Chromium, not Chrome, and so are not currently guaranteed to work seamlessly with Chrome. However, if the computer has Chrome installed, Chromedriver may look for and use the Chrome installation instead of the Chromium installation. It is unknown if this causes bugs - please update this README if this is tested.

### Opera and OperaChromiumDriver

Opera can be installed following the instructions [here](https://www.itzgeek.com/how-tos/linux/centos-how-tos/how-to-install-opera-browser-on-centos-7-rhel-7-fedora-28-27.html) or from their [web site](https://www.opera.com/download). OperaChromiumDriver, the driver for Opera versions 12 and later, can be downloaded from [Github](https://github.com/operasoftware/operachromiumdriver/releases).

### Other Setup

Like the unit tests, the web tests require a server configuration and cloud credentials. This can be created using the `cloudscheduler defaults set` command, or will be done automatically when the tests are first run.

The status tests require the system time to be set to the user time zone.

A GUI is needed for the web tests.

To modify the server at which the tests are addressed (not mandatory for original setup), the `unit-test` server url in `.csv2/unit-test/settings.yaml` must be modified accordingly, and the login credentials if necessary. The `server_url` variable in `web_test_helpers` should also be modified to match the new server.

## Adding Tests

New test modules should be named starting with `test_web_` (the modules starting with `web_test_` are helper modules). The test files should be named `test_web_<page>.py`. The common class, where the majority of tests are implemented, should be named `TestWeb<Page>Common`. The classes with the proper setups (see below) should be named `TestWeb<Page><UserType><Browser>`. Individual tests should be named `test_web_<page>_<action>_<details>`, where `<action>` is the name of the action using the `cloudscheduler` command. If suitably complex, `<action>` should ideally be formatted as `<object>_<action_on_object>_<details>`. Note that individual tests having names that start with `test` is currently the only breaking naming requirement.

All test files must be put in the `web_tests` directory, and each test file must be imported into `create_test_suite.py` and have its classes added to the lists of tests for their respective browsers. Note that the detailed classes (see below) should be the only ones put in here - the common classes (see below) do not have the proper setup to be run on their own and should not be included.

New tests should additionally follow all rules for Unittest test classes, as they are run using the Unittest framework.

New test classes should include the `web_test_setup_cleanup` module and call the `setup()` function as part of the `setUpClass()` function, passing it the test class it is being called as a part of. `setup()` currently automatically deletes all old test setups when run (via calling the `cleanup()` function). The `cleanup()` function should be called during the `tearDownClass()` function, again passing it the test class it is being called in. `cleanup()` is also called on error in the setup, and `cleanup_objects()` is called on a `KeyboardInterrupt` at any time during the tests (using a handler contained in this module). Neither function will attempt to delete any object it cannot find. 

New tests should include the `web_test_setup_cleanup`, `web_test_assertions_v2`, `web_test_page_objects`, and `web_test_helpers` modules. The other `web_test_*` modules are used in these modules, and should only be accessed via these modules. The `web_test_assertions` module is not and should not be used in any module, and should eventually be deleted. `web_test_helpers` is also included in `web_test_setup_cleanup`, but should not be used via that module. `web_test_helpers` is also used in the `web_test_page_objects` module. 

New tests that create objects should make sure to update the maximum item numbers in the calls to `delete_objects_by_type()` in `web_test_setup_cleanup.cleanup_objects()`.

Tests should be created in a common class that inherits `unittest.TestCase`, called `TestWeb<Page>Common`. Each different setup for these tests (ie different users, different browsers, etc) should have its own class, called `TestWeb<Page><Details>`. This class should inherit `TestWeb<Page>Common` and should override the `setUpClass` method (usually with a call to `super()` as well) to do the proper setup. All details not related to the setup or contingent on factors in that particular configuration should be put in the common class. All test classes for one page should be put in the same file, `test_web_<page>.py`. 

In rare cases, a certain setup may require a few tests to be different. These individual tests and no others should be overriden in the detailed class. However, all tests that can be put in the common class should be put in the common class, where they only need be edited once.

## Writing Tests

The `cls.gvar` variable, which is assigned in `web_test_setup_cleanup.setup()`, contains server and user information read from various `.yaml` configuration files. This includes  the user credentials for the sample users. It also contains a sub-dictionary called `oversize`, which contains a set of values that are oversize for the various types in the database. These can be accessed as `gvar['oversize']['<type_name>']` and are primarily used in database verification tests.

The `web_test_assertions_v2` module contains a set of functions that should be callable within a `TestCase` class and raise the proper errors on failure. These functions access the cloudscheduler database via the command line interface and can test if objects were properly created in the database. However, they are extremely slow compared to assertions using Selenium selectors, and therefore should be used only once per test. Additionally, objects without a `cloudscheduler` command (like config objects) cannot use these assertions - they should instead refresh the page and ensure that the data has persisted.

Each assertion in the `web_test_assertions_v2` module takes a list of arguments, most of which are optional. The four mandatory arguments (only two of which are taken by `assertExists` and `assertNotExists`) are `type`, the type of object being asserted; `name`, the name of the individual object the assertion is about; `attribute`, the name of the attribute in the database (found via the `list` command with the `-VC` option); and `attribute_name`, the name of the particular item of that attribute being asserted. There are also six optional arguments: `group`, a group name, which should be specified when an object exists within a particular group, and which defaults to `None`; `err`, the margin of error, which should be specified when a value will be within a range, and which defaults to `None`; `metadata_cloud`, the name of a cloud within which the metadata exists, which should be specified for cloud metadata, and which defaults to `None`; `defaults`, a true/false flag, which should be specified when the item is a group default, and which defaults to false; `name_field`, a true/false flag, which should be specified for objects for which there is no name flag, and which defaults to true; `settings`, a true/false flag, which should be specified when the item is a user setting, and which defaults to false; `server`, the name of the server default to use, which should be specified when the object can only be accessed by a server that is not the unit-test server, and which defaults to `unit-test`; `image_cloud`, which should be specified when the object is an image, and which defaults to `None`; and `is_retry`, a true/false flag, which should never be manually passed (it is only used within the functions).

By default, all actions will be performed within the `{user}-wig0` group (see Test Profiles, below). The base `Page` class (see [Page Objects](#page-objects)) contains a method for switching between these groups. Be aware that the active user must be in a particular group to switch to it.

Additional files the tests may need (for example, image files to upload) should be stored in the `misc_files` directory. These files will not be committed (unless they are markdown files, which they shouldn't be), and the current tests look in this folder for these files. This is also where test log files and test downloads are stored.

Test objects should, if possible, be named `{user}-wixn`, where `x` is the letter identifier (usually the first letter of the object name, but can be chosen to be anything as long as it's consistent) and `n` is the number of the individual object (starting at 1 - 0 is reserved for behind-the-scenes objects and will need to be deleted seperately). The `web_test_setup_cleanup.delete_by_type()` function assumes this naming pattern, although it takes an optional argument, `others`, which is a list of names of objects that do not fit this pattern. Despite this, objects should be named to follow the pattern unless there is a reason they cannot (for example, they are stored on the web and need to be used by many different test users).

Test files should perform actions on the page via [page objects](#page-objects). 

## Page Objects

The test files should access the page via the use of page objects. Each page on the csv2 website has one page class, stored in the `web_test_page_objects` module. 

A page object is essentially a class containing functions to perform all actions performable on the page it represents. It is an interface through which the test objects know how to locate, click, type, and perform actions on the page. One page object method should perform one specific click, type, location, or similar action - ie, while the same page object function may be used to click checkboxes adding a user to different groups, a different function should be used to click the superuser checkbox. Actions that are repeated a lot (such as the interaction functions in `web_test_interactions`) should be refactored into a common file, rather than being made a multipurpose function in the page object. Functions should also be named appropriately, so that someone scrolling through the test code without looking at the page objects file would know, in UI terms, what the test is attempting to do.

A new page object should inherit from the `Page` class, which will give it access to the driver and any website-wide components (such as the top navigation bar and error messages). Any interaction with that page should be done via methods implemented in that page class. 

Some page value modification methods take strings, while others take integers. Ensure the correct type is passed to each method.

The `web_test_interactions`, `web_test_javascript_interactions`, and `web_test_xpath_selectors` modules define the actions that the page objects should use. `web_test_interactions` and `web_test_javascript_interactions` have very similar functions (see below). Each method wraps Selenium's wait action, the find method, and the action taken (sometimes a series of actions) into a single function. `web_test_xpath_selectors` is a set of wrapper functions for various XPath locators. Some of these are described by an object they represent (ie `delete_button`, which is the button on the delete object modal) and some are described by how they find the object (ie `form_input_by_value`, which finds an input within a particular form based on its value attribute).

The `web_test_javascript_interactions` module contains a set of functions that operate similarly to the `web_test_interactions` functions, except for the fact that they use the JavaScript `execute_script` to do the click action. These should not be used without a justifiable reason (ie a Selenium glitch) that the other ones cannot be used, and this glitch should be documented in the comments above the use of the function. Currently, the only Selenium bug requiring the use of these is an inability to click on the side buttons on some pages due to overlapping padding.

Note that the use of Selenium's built-in `.submit()` method has been phased out. This is because the `submit` method only submits the form, and does not perform the `click` action on the button, meaning that some functionality is lost, which can cause improper behavior. The `web_test_xpath_selectors.form_submit_by_name` and `web_test_interactions.click_by_xpath` functions should be used instead.

The page objects additionally use some functions from the `web_test_helpers` module.

## Running Tests

The web tests do run with the `run_tests` script in the `unit_tests` folder. However, because failure and error numbers are not surfaced by `unittest`, the script does not add the numbers for the web tests to its error tallies.

Web tests can be run using `./run_tests web` from the `unit_tests` folder, and tests for a specific browser can be run using `./run_tests web_<browser>`. One can also run a particular class directly using `python3 -m unittest <filename>.<ClassName>`. While unittest does support running tests by file, the setup of the test fixtures does not allow that and will run duplicate tests, some of which will fail, and, thus, the `python3 -m unittest <filename>` syntax is not to be used. Each detailed class should be run individually, and common classes should never be run (see Adding Tests, above). Individual tests can be run with `python3 -m unittest <filename>.<ClassName>.<test_name>`. All tests should be run from the `unit_tests` folder to allow module imports to work properly. Note that individual test files, classes, and methods cannot currently be run with the `run_tests` script.

The tests should be run as a non-root user. Root users may experience problems with the Chromium browser tests, as Chromium is not designed to run as a root user.

Regardless of which browser the tests are run in, the setup requires the Firefox browser in order to run a headless setup mode. The tests will fail without valid Firefox and Geckodriver installations.

If tests are being set up with clouds, the setup script may display an error similar to: 

```
Error: CV-01749 cloud update, "{user}-wic1" failed - specified value in list of values does not exist: vm_security_groups=default, group_name={user}-wig0, cloud_name={user}-wic1.
Error connecting to the cloud. This may happen several times. Retrying...
```

A similar error occurs with the key setup and default setup, although the values that do not exist are slightly different (referring to the VM keyname instead of the security group).

This is expected behaviour - the setup requires resources from the cloud connection, and when it can access those resources is unpredictable, so the script will try, print that message on a failure, and continue trying until the setup is successful. Depending on where the cloud poller is in its process, it may take up to a dozen retries. The tests will continue to set up properly and run - this is not a setup error.

A small portion of the tests (currently the key add tests only) require the poller to be queried like in the setup. These tests may appear to hang for as long as five minutes. This is expected behaviour - the tests are not hanging infinitely, as there is a maxiumum wait assigned, and they will continue as expected.

The key tests will occasionally generate the following warning:
```
/usr/local/lib64/python3.6/site-packages/yaml/scanner.py:286: ResourceWarning: unclosed <socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 40206), raddr=('127.0.0.1', 41942)>
```

The exact cause of this warning is currently unknown. It does not impact the functionality of the tests, but it may be worth investigating.

## Debugging Tests

To create the test fixtures to manually inspect the tests, the `.setup_objects()` and `.cleanup_objects()` functions from the `web_test_setup_cleanup` module should be used (passing any additonal arguments as specified in the "Test Profiles" section). The `setup()` and `cleanup()` functions do the driver setup as well, but, in addition, require the calling class, the suffix number of the user to use (ie 1 for `{user}-wig1`), and the name of the browser as arguments. 

Several functions log information in files called `*objects.txt`. These files can be useful for debugging. They should not be committed, and it is harmless to delete them - they will be automatically remade when needed. Note that these files are reused every time one of the functions that use them is called, so if multiple tests or test suites are run, they will likely only contain information about the last test. All log files will be automatically placed in the `misc_files` folder.

The primary known cause of flaky tests is the test not waiting long enough for the object to properly appear. Using the `sleep()` or `WebDriverWait` functions can help fix this, as can retrying the action if it fails. For example, the `setup_objects` function uses `sleep()`, the `web_test_interactions` and `web_test_page_objects` methods use `WebDriverWait`, and the `web_test_assertions_v2` methods will retry the query an additional time (after a five-second `sleep()`) if they fail to find what they're looking for.

The `Page` class contains a `take_screenshot()` function. This function can be called at any time during the tests and requires no additional arguments. It will name the screenshot file `<method>_screenshot.png` and save it to the `unit_tests/web_tests/misc_files` folder.

## Test Profiles

The tests have a set of automatically-created objects, created in the `web_test_setup_cleanup.setup()` function. 

Additional profiles can be added to the suite. In order to do so, the object should be added to the creation list in `web_test_setup_cleanup.setup_objects()`. Any tests that previously used an object with that suffix (likely an `add` test) should given a new suffix. The corresponding `delete_objects_by_type()` call in `web_test_setup_cleanup.cleanup_objects()` should have the count updated to ensure it deletes all objects. Additional profiles should likely not be added in the universal objects (see below) - they should be added in an optional group if at all possible, to cut down on test runtime.

New types of objects can also be added to the suite, in a similar manner. A new group of creation `subprocess.run` calls will need to be added in `setup_objects()`, and an accompanying call to `delete_objects_by_type()` in `cleanup_objects()`. If the objects cannot be deleted with the `delete_objects_by_type()` command syntax, they must either be deleted in a custom method (like aliases) or automatically deleted as part of another method (like cloud metadata). Again, they should be added in an optional group if possible (see below).

There are two categories of objects - some that are created by `setup_objects()` regardless of arguments passed, and some that are only created when the tests request them. The objects created under [Universal Objects](#universal-objects) are created automatically when `setup_objects()` is run, regardless of arguments. To create the other set of objects, pass the names of the object groups (ie "users") to the `setup()` function as a list of strings.

A few of the test objects do not have a command line setup for their creation and deletion (currently only the keypairs). These items should use Selenium to set up the objects on the web site that dictates them. This setup should be done in headless mode and should be configured to give outputs similar to the command line. Using Selenium for setups is slow and fragile, and should not be used if there is a command line alternative. These tests are configured to use the same browser as the tests, so that if the user does not have all the browsers, the tests will still run.

There is one additional group created as part of the universal setup that is not specified below and has no output in the setup scripts. It is not to be edited in any way during the tests, and any user used to run tests (currently `{user}-wiu1` and `{user}-wiu2`) should be in it. The real user account (ie `{user}`) is also added to this group when it is created, to allow this user to make the test objects within this group. The group is called `{user}-wig0`. All clouds, aliases, and any other objects requiring a group are and should be created under this group, with a few rare exceptions (for example, if a group test requires a group to have a cloud in it). It is saved as `gvar['base_group']`. It is the first item created as part of the setup, and the last item deleted, and should remain so. Many functions have an optional `group` argument that is invoked to prevent cloud tests from failing, and, if needed, this is the group that should be passed.

Note that some objects (like the metadata files) do not have their own delete method. These objects are cleaned up when their containing objects are cleaned up.

Note that some keywords do additional setup, besides creating the objects (in fact, some do not create objects at all). When creating test setup functions, these actions should be taken into account.

### Universal Objects

`{user}-wiu1` is a standard user. They are in the `{user}-wig1` group. They are the account used in regular user tests.

`{user}-wiu2` is a super user. They are in the `{user}-wig2` group. They are they account used in super user tests.

`{user}-wiu3` is a standard user. They are not in any groups.

`{user}-wig1` contains the `{user}-wiu1` user. It is a group to be edited in update tests.

`{user}-wig2` contains the `{user}-wiu2` user. It is a group to be edited in update tests.

`{user}-wig3` contains no users.

`{user}-wig0::{user}-wic1` is a standard openstack cloud. It is a cloud to be edited in update tests.

`{user}-wig0::{user}-wic2` is a standard openstack cloud. It is a cloud to be removed in deletion tests.

### Users

`{user}-wiu4` is a standard user. They are in the `{user}-wig1` group. They are a user to be edited in update tests.

### Groups

`{user}-wig4` contains no users. It is a group to be removed in deletion tests.

### Clouds

`{user}-wig0::{user}-wic1::{user}-wim1.yaml` is a standard cloud metadata. It is to be edited in update tests.

`{user}-wig0::{user}-wic1::{user}-wim2.yaml` is a standard cloud metadata. It is to be removed in deletion tests.

### Aliases

`{user}-wig0.{user}-wia1` is a standard alias. It contains the `{user}-wic1` cloud. It is to be edited in update tests.

`{user}-wig0.{user}-wia2` is a standard alias. It contains the `{user}-wic1` and `{user}-wic2` clouds. It is to be edited in update tests.

`{user}-wig0.{user}-wia3` is a standard alias. It contains the `{user}-wic1` cloud. It is to be deleted in delete tests.

### Defaults

`{user}-wig1::{user}-wim1.yaml` is a standard group metadata. It is to be edited in update tests.

`{user}-wig1::{user}-wim2.yaml` is a standard group metadata. It is to be removed in deletion tests.

### Images

`{user}-wig0::{user}-wic1::{user}-wii1.hdd` is a standard RAW image. It is to be edited in edit tests.

`{user}-wig0::{user}-wic1::{user}-wii2.hdd` is a standard RAW image. It is to be deleted in delete tests.

### Keys

`{user}-wik1` is a standard key. It is used in tests requiring the selection of a key (also added by `clouds` and `defaults`)

`{user}-wik2` is a standard key. It is to be deleted in delete tests.

### Servers

`{user}-wis1` is a server with the login credentials of the `{user}-wiu1` user.

`{user}-wis2` is a server with the login credentials of the `{user}-wiu2` user.

## Future Features (TODOs)

This section discusses all the changes that would be beneficial to the web test framework. Some of the features in here may not be feasible, but this is a list of the ideal items that would be changed in the test suite.

### Fixes

These items should ideally be fixed before the test suite is complete.

### Functional

These items should be finished before the test suite is considered completed. They affect the test suite's functionality.

- Openstack command line

- Script to set up test starter files (image files, key files, etc)

- Time-dependent flaky tests for status page (may be fixed)

- Chrome tests

### Tidying Up

These items shouldn't affect the test suite's functionality much, but they would make it tidier and easier to work with. They should be done before the test suite is considered completed if possible, but they won't break anything if they aren't.

- Rewrite/edit README

- Standardize integer vs string for page object methods

- Update comments/docstrings

- Remove code that was commented out for testing

- Add setup option for single key (instead of having it be added as part of other setups)

### Additional Features

These are features for future implementation, or to be added if time permits.

#### Test Coverage

These items are additional test coverage that may or may not be necessary.

- Multiple types of clouds (held up on not having access to multiple types of clouds)

- Typing in select bars

- Drag and drop to modify plot scale 

- Click and drag plot zoom (and double click zoom out)

#### Other Features

These items are not necessary, but would be useful.

- Rewrite time rounding function

- Alternate assertion information passing (phase out logfiles)

- Class/method documentation for test modules

- Speed up setup/teardown

- Safari/Edge/IE tests (likely require VMs and use of `webdriver.Remote`)