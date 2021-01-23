# Running the Web Tests

This document contains details of how to set up, write, and run the web tests. 

## Setup

Each user you plan to use in the tests must have a Firefox profile. Currently, the only way to do this is by manually creating a new Firefox profile at `about:profiles`, switching to that profile, logging into cloudscheduler manually with that user's credentials, and then saving them, although ideally, there will soon be a script to do this as part of the setup. These profiles should be added to the `settings.yaml` file like so:

```yaml
firefox_profiles:
- root/.mozilla/firefox/<profile_name>
```

The credentials added should be `{user}-wiu1`, `{user}-wiu2`, and `{user}-wiu3`, and all of them should have the password `user_secret`.

## Adding Tests

New tests should be named starting with `test_web_` (although this is not a breaking requirement). All test files must be put in the `web_tests` directory, and each test class must have the following added to `create_test_suite.py`:

```python
    from .<filename> import <ClassName>

    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(<ClassName>))
```

New tests should additionally follow all rules for Unittest test classes, as they are run using the Unittest framework.

New test classes should include the `web_tests_setup_cleanup` module and call the `setup()` function as part of the setup. `setup()` currently automatically deletes all old test setups when run. The `cleanup()` function also exists - currently, its only purpose is to be run from the Python interpreter to manually clean the test objects from the database, although it is likely going to become a part of the `tearDown()` function.

Common functions are stored in files starting with `web_tests_`. These files can be included as needed in any `test_web` files (and probably should be for a majority of them). New files containing common functions should continue this convention (although this is, again, not a breaking requirement).

## Writing Tests

The `cls.gvar` variable, which should be assigned the return value of `web_tests_setup_cleanup.setup()`, contains server and user information read from various `.yaml` configuration files. This includes the locations of the firefox profiles and the user credentials for the sample users.

## Running Tests

The web tests do run with the `run_tests` script in the `unit_tests` folder. However, because failure and error numbers are not surfaced by `unittest`, the script does not add the numbers for the web tests to its error tallies.

Web tests can be run using `./run_tests web` in the `unit_tests` folder, or using `python3 -m unittest` in the `web_tests` folder. For compatibility with the other unit tests, the first approach is recommended, as other unit tests can then be run simultaneously. One can also run a particular class directly using `python3 <filename>.py` or `python3 -m unittest <filename>.ClassName`. Individual tests can be run with `python3 -m unittest <filename>.ClassName.test_name`.