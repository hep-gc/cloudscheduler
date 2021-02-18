# Running the Web Tests

This document contains details of how to set up, write, and run the web tests. 

## Setup

The web tests require Python3, Selenium Webdriver, and Geckodriver to run. Selenium Webdriver can be installed via `pip install selenium`. Geckodriver can be downloaded from [GitHub](https://github.com/mozilla/geckodriver/releases/tag/v0.28.0).

Each user used as an active user in the tests must have a Firefox profile, in order to deal with a Selenium issue around username/password popups. In order to make these, go into the python interpreter and run the `setup_objects()` function from `web_test_setup_cleanup` (no parameters need be passed). Then, create a new Firefox profile at `about:profiles`, switch to that profile, log into cloudscheduler manually with that user's credentials, and save them. These profiles should be added to the `settings.yaml` file like so:

```yaml
firefox_profiles:
- root/.mozilla/firefox/<profile_name>
```

Currently, the credentials added should be `{user}-wiu1`, `{user}-wiu2`, and `{user}-wiu3` (although `{user}-wiu3` may be phased out), and all of them should have the password `user_secret`.

Ideally, there will be a script to do this eventually, but as Firefox currently does not seem to recognize passwords input into the `about:logins` page, this isn't currently feasible.

As with the other unit tests, a server configuration and cloud credentials are required to run the tests.

## Adding Tests

New test modules should be named starting with `test_web_` (the modules starting with `web_test_` are helper modules). The test files should be named `test_web_<page>.py`, with the class being named `TestWeb<Page>`. Individual tests should be named `test_web_<page>_<action>_<details>`, where `<action>` is the name of the action using the `cloudscheduler` command. If suitably complex, `<action>` should ideally be formatted as `<object>_<action_on_object>_details`. Note that individual tests having names that start with `test` is currently the only breaking naming requirement.

All test files must be put in the `web_tests` directory, and each test class must have the following added to `create_test_suite.py`:

```python
    from .<filename> import <ClassName>

    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(<ClassName>))
```

New tests should additionally follow all rules for Unittest test classes, as they are run using the Unittest framework.

New test classes should include the `web_test_setup_cleanup` module and call the `setup()` function as part of the `setUpClass()` function, passing it the test class it is being called as a part of. `setup()` currently automatically deletes all old test setups when run (via calling the `cleanup()` function). The `cleanup()` function should be called during the `tearDownClass()` function, again passing it the test class it is being called in. `cleanup()` is also called on error in the setup, and `cleanup_objects()` is called on a `KeyboardInterrupt` at any time during the tests (using a handler contained in this module). Neither function will attempt to delete any object it cannot find. 

New tests should include the `web_test_setup_cleanup`, `web_test_assertions`, and `web_test_page_objects` modules. The other `web_test_*` modules are used in these three modules, and should only be accessed via these three modules. 

New tests that create objects should make sure to update the maximum item numbers in the calls to `delete_objects_by_type()` in `web_test_setup_cleanup.cleanup_objects()`

Each test class uses either the regular user (`{user}-wiu1`) or the super user (`{user}-wiu2`) profile. There is currently no setup to use both. Established practice is to put both the `TestWeb<Page>RegularUser` and `TestWeb<Page>SuperUser` classes in the same file, `test_web_<page>.py`.

## Writing Tests

The `cls.gvar` variable, which is assigned in `web_test_setup_cleanup.setup()`, contains server and user information read from various `.yaml` configuration files. This includes the locations of the firefox profiles and the user credentials for the sample users.

The `web_test_assertions` module contains a set of functions that should be callable within a `TestCase` class and raise the proper errors on failure. These functions access the cloudscheduler database via the `list` command and can test if objects were properly created in the database. However, they are extremely slow compared to assertions using Selenium selectors, and therefore should be used only once per test. In cases where the object being asserted is only available in a group context, all the assertions take a `group` argument (which should typically be `gvar['base_group']`, see "Test Profiles"), which only needs to be specified in these cases. In cases where the object being asserted is a metadata object, and one of its attributes is being asserted on, an optional argument `metadata_name` should be passed (with the `attribute` and `attribute name` referring to the attribute in the metadata table), with this providing the name (including the extension) of the metadata file.

The `web_test_assertions` module contains a pair of functions asserting that two numbers are near each other. These should only be used in situations where the test cannot reliably produce exact numbers and should not be able to (such as with sliding a slider, which can only produce numbers within a certain pixel sensitivity). These functions cannot be used to assert any value that cannot be converted to an integer by Python's `int()` function.

This module also contains a pair of functions to look for attributes with a certain name when there is no cloudscheduler flag for specifying an object's name (check the `web_test_assertions.names()` function to see which objects these are - they will have their `flag` attribute set to `None`). These methods should only be used for objects that do not have a name flag, and they do not take the argument specifying metadata.

Test files should perform actions on the page via page objects (see below). 

## Page Objects

The test files should access the page via the use of page objects. Each page on the csv2 website has one page class, stored in the `web_test_page_objects` module. 

A page object is essentially a class containing functions to perform all actions performable on the page it represents. It is an interface through which the test objects know how to locate, click, type, and perform actions on the page. One page object method should perform one specific click, type, location, or similar action - ie, while the same page object function may be used to click checkboxes adding a user to different groups, a different function should be used to click the superuser checkbox. Actions that are repeated a lot (such as the interaction functions in `web_test_interactions`) should be refactored into a common file, rather than being made a multipurpose file in the page object. Functions should also be named appropriately, so that someone scrolling through the test code without looking at the page objects file would know, in UI terms, what the test is attempting to do.

A new page object should inherit from the `Page` class, which will give it access to the driver and any website-wide components (such as the top navigation bar and error messages). Any interaction with that page should be done via methods implemented in that page class. 

Some page value modification methods take strings, while others take integers. Ensure the correct type is passed to each method. These should eventually be standardized.

The `web_test_interactions`, `web_test_javascript_interactions`, and `web_test_xpath_selectors` modules define the actions that the page objects should use. `web_test_interactions` and `web_test_javascript_interactions` have very similar functions (see below). Each method wraps Selenium's wait action, the find method, and the action taken (sometimes a series of actions) into a single function. `web_test_xpath_selectors` is a set of wrapper functions for various XPath locators. Some of these are described by an object they represent (ie `delete_button`, which is the button on the delete object modal) and some are described by how they find the object (ie `form_input_by_value`, which finds an input within a particular form based on its value attribute).

The `web_test_javascript_interactions` module contains a set of functions that operate similarly to the `web_test_interactions` functions, except for the fact that they use the JavaScript `execute_script` to do the click action. These should not be used without a justifiable reason (ie a Selenium glitch) that the other ones cannot be used, and this glitch should be documented in the comments above the use of the function. Currently, the only Selenium bug requiring the use of these is an inability to click on the side buttons on some pages due to overlapping padding.

Note that the use of Selenium's built-in `.submit()` method has been phased out. This is because the `submit` method only submits the form, and does not perform the `click` action on the button, meaning that some functionality is lost, which can cause improper behavior. The `web_test_xpath_selectors.form_submit_by_name` and `web_test_interactions.click_by_xpath` functions should be used instead.

## Running Tests

The web tests do run with the `run_tests` script in the `unit_tests` folder. However, because failure and error numbers are not surfaced by `unittest`, the script does not add the numbers for the web tests to its error tallies.

Web tests can be run using `./run_tests web`, or using `python3 -m unittest -s web_tests`, both from the `unit_tests` folder. For compatibility with the other unit tests, the first approach is recommended, as other unit tests can then be run simultaneously. One can also run a particular file or class directly using `python3 <filename>.py` or `python3 -m unittest <filename>.<ClassName>`, respectively. Individual tests can be run with `python3 -m unittest <filename>.<ClassName>.<test_name>`. All tests should be run from the `unit_tests` folder to allow module imports to work properly. Note that individual test files, classes, and methods cannot currently be run with the `run_tests` script.

If tests are being set up with clouds, the setup script may display an error similar to: 

```
Error: CV-01749 cloud update, "{user}-wic1" failed - specified value in list of values does not exist: vm_security_groups=default, group_name={user}-wig0, cloud_name={user}-wic1.
Error connecting to the cloud. This may happen several times. Retrying...
```

This is expected behaviour - the cloud setup requires resources from the cloud connection, and when it can access those resources is unpredictable, so the script will try, print that message on a failure, and continue trying until the setup is successful. Depending on where the cloud poller is in its process, it may take up to a dozen retries. The tests will continue to set up properly and run - this is not a setup error.

## Debugging Tests

To create the test fixtures to manually inspect the tests, the `.setup_objects()` and `.cleanup_objects()` functions from the `web_test_setup_cleanup` module should be used (passing any additonal arguments as specified in the "Test Profiles" section). The `setup()` and `cleanup()` functions do the driver setup as well, but, in addition, require the calling class and the suffix number of the Firefox profile to use (ie 1 for `{user}-wig1`) as arguments. 

Several functions log information in files called `*objects.txt`. These files can be useful for debugging. They should not be committed, and it is harmless to delete them - they will be automatically remade when needed. Note that these files are reused every time one of the functions that use them is called, so if multiple tests or test suites are run, they will likely only contain information about the last test. If possible, the use of these files will eventually be phased out.

The primary known cause of flaky tests is the test not waiting long enough for the object to properly appear. Using the `sleep()` or `WebDriverWait` functions can help fix this, as can retrying the action if it fails. For example, the `setup_objects` function uses `sleep()`, the `web_test_interactions` and `web_test_page_objects` methods use `WebDriverWait`, and the `web_test_assertions` methods will retry the query an additional time (after a five-second `sleep()`) if they fail to find what they're looking for.

## Test Profiles

The tests have a set of automatically-created objects, created in the `web_test_setup_cleanup.setup()` function. 

Additional profiles can be added to the suite. In order to do so, the object should be added to the creation list in `web_test_setup_cleanup.setup_objects()`. Any tests that previously used an object with that suffix (likely an `add` test) should given a new suffix. The corresponding `delete_objects_by_type()` call in `web_test_setup_cleanup.cleanup_objects()` should have the count updated to ensure it deletes all objects. Additional profiles should likely not be added in the defaults (see below) - they should be added in an optional group if at all possible, to cut down on test runtime.

New types of objects can also be added to the suite, in a similar manner. A new group of creation `subprocess.run` calls will need to be added in `setup_objects()`, and an accompanying call to `delete_objects_by_type()` in `cleanup_objects()`. If the objects cannot be deleted with the `delete_objects_by_type()` command syntax, they must either be deleted in a custom method (like aliases) or automatically deleted as part of another method (like cloud metadata). Again, they should be added in an optional group if possible.

There are two categories of objects - some that are created by `setup_objects()` regardless of arguments passed, and some that are only created when the tests request them. The objects created under "Defaults", below, are created automatically when `setup_objects()` is run, regardless of arguments. To create the other set of objects, pass the names of the object groups (ie "users") to the `setup()` function as a list of strings.

There is one additional group created as part of the default setup that is not specified below and has no output in the setup scripts. It is not to be edited in any way during the tests, and any user with a profile (with the exception of `{user}-wiu3`, who is not in groups) should be in it. The real user account (ie `{user}`) is also added to this group when it is created, to allow this user to make the test objects within this group. The group is called `{user}-wig0`. All clouds, aliases, and any other objects requiring a group are and should be created under this group, and it is saved as `gvar['base_group']`. It is the first item created as part of the setup, and the last item deleted, and should remain so. Many functions have an optional `group` argument that is invoked to prevent cloud tests from failing, and, if needed, this is the group that should be passed.

Note that some objects (like the metadata files) do not have their own delete method. These objects are cleaned up when their containing objects are cleaned up.

### Defaults

`{user}-wiu1` is a standard user. They are in the `{user}-wig1` group.

`{user}-wiu2` is a super user. They are in the `{user}-wig2` group.

`{user}-wiu3` is a standard user. They are not in any groups.

`{user}-wig1` contains the `{user}-wiu1` user. It is a group to be edited in update tests.

`{user}-wig2` contains the `{user}-wiu2` user. It is a group to be edited in update tests.

`{user}-wig3` contains no users.

`{user}-wig0::{user}-wic1` is a standard cloud. It is a cloud to be edited in update tests.

`{user}-wig0::{user}-wic2` is a standard cloud. It is a cloud to be removed in deletion tests.

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