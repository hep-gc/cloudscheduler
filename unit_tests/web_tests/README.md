# Running the Web Tests

This document contains details of how to set up, write, and run the web tests. 

## Setup

Each user you plan to use in the tests must have a Firefox profile, in order to deal with a Selenium issue around username/password popups. In order to make these, go into the python interpreter and run the `setup_objects()` function from `web_test_setup_cleanup`. Then, create a new Firefox profile at `about:profiles`, switch to that profile, log into cloudscheduler manually with that user's credentials, and save them. These profiles should be added to the `settings.yaml` file like so:

```yaml
firefox_profiles:
- root/.mozilla/firefox/<profile_name>
```

Currently, the credentials added should be `{user}-wiu1`, `{user}-wiu2`, and `{user}-wiu3`, and all of them should have the password `user_secret`.

Ideally, there will be a script to do this eventually, but as Firefox currently does not seem to recognize passwords input into the `about:logins` page, this isn't currently feasible.

## Adding Tests

New test functions should be named starting with `test_web_`. The test files should be named `test_web_<page>.py`, with the class being named `TestWeb<Page>`. Individual tests should be named `test_web_<page>_<action>_<details>`. Note that individual tests having names that start with `test` is currently the only breaking requirement.

All test files must be put in the `web_tests` directory, and each test class must have the following added to `create_test_suite.py`:

```python
    from .<filename> import <ClassName>

    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(<ClassName>))
```

New tests should additionally follow all rules for Unittest test classes, as they are run using the Unittest framework.

New test classes should include the `web_test_setup_cleanup` module and call the `setup()` function as part of the `setUpClass()` function, passing it the test class it is being called as a part of. `setup()` currently automatically deletes all old test setups when run (via calling the `cleanup()` function). The `cleanup()` function should be called during the `tearDownClass()` function, again passing it the test class it is being called in. `cleanup()` is also called on error in the setup or on a `KeyboardInterrupt` at any time during the tests (using a handler contained in this module). Neither function will attempt to delete any object it cannot find. 

Common functions are stored in files starting with `web_test_`. These files can be included as needed in any `test_web` files (and probably should be for a majority of them). New files containing common functions should continue this convention (although this is, again, not a breaking requirement).

## Writing Tests

The `cls.gvar` variable, which is assigned in `web_test_setup_cleanup.setup()`, contains server and user information read from various `.yaml` configuration files. This includes the locations of the firefox profiles and the user credentials for the sample users.

The `web_test_javascript_interactions` module contains a set of functions that operate similarly to the `web_test_interactions` functions, except for the fact that they use the JavaScript `execute_script` to do the click action. These should not be used without a justifiable reason (ie a Selenium glitch) that the other ones cannot be used. Including this module in any more classes than strictly necessary is discouraged. 

The `web_test_assertions` module contains a set of functions that should be callable within a `TestCase` class and raise the proper errors on failure. These functions access the cloudscheduler database via the `list` command and can test if objects were properly created in the database. However, they are extremely slow compared to assertions using Selenium selectors - if the test can be asserted with another assertion method, that is probably better, and they should ideally only be used one-per-test.

The `web_test_xpath_selectors` module contains the XPath formatters for several common buttons and should be used along with the `web_test_interactions.click_by_xpath()` function. This module may eventually be replaced by a group of page objects - this possibility needs to be investigated.

## Running Tests

The web tests do run with the `run_tests` script in the `unit_tests` folder. However, because failure and error numbers are not surfaced by `unittest`, the script does not add the numbers for the web tests to its error tallies.

Web tests can be run using `./run_tests web`, or using `python3 -m unittest -s web_tests`, both from the `unit_tests` folder. For compatibility with the other unit tests, the first approach is recommended, as other unit tests can then be run simultaneously. One can also run a particular class directly using `python3 <filename>.py` or `python3 -m unittest <filename>.ClassName`. Individual tests can be run with `python3 -m unittest <filename>.ClassName.test_name`. All tests should be run from the `unit_tests` folder to allow module imports to work properly.

## Debugging Tests

To create the test fixtures to manually inspect the tests, the `.setup_objects()` and `.cleanup_objects()` functions from the `web_test_setup_cleanup` module should be used. The `setup()` and `cleanup()` functions do the driver setup as well, but require the calling class as an argument. 

Several functions log information in files called `*objects.txt`. These files can be useful for debugging. They should not be committed, and it is harmless to delete them - they will be automatically remade when needed. If possible, the use of these files will eventually be phased out.

## Test Profiles

The tests have a set of automatically-created objects, created in the `web_test_setup_cleanup.setup()` function. 

Additional profiles can be added to the suite. In order to do so, the object should be added to the creation list in `web_test_setup_cleanup.setup_objects()`. Any tests that previously used an object with that suffix (likely an `add` test) should given a new suffix. The corresponding `delete_objects_by_type()` call in `web_test_setup_cleanup.cleanup_objects()` should have the count updated to ensure it deletes all objects.

### Users

`{user}-wiu1` is a standard user. They are in the `{user}-wig1` group.

`{user}-wiu2` is a super user. They are in the `{user}-wig2` group.

`{user}-wiu3` is a standard user. They are not in any groups.

### Groups

`{user}-wig1` contains the `{user}-wiu1` user.

`{user}-wig2` contains the `{user}-wiu2` user.

`{user}-wig3` contains no users.

`{user}-wig4` contains no users. It is a group to be removed in deletion tests.