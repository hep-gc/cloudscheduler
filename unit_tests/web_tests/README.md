# Running the Web Tests

This document contains details of how to set up, write, and run the web tests. 

## Setup

Each user you plan to use in the tests must have a Firefox profile. Currently, the only way to do this is by manually creating a new Firefox profile at `about:profiles`, switching to that profile, logging into cloudscheduler manually with that user's credentials, and then saving them. Ideally, there will soon be a script to do this as part of the setup.

## Adding Tests

New tests should be named starting with `test_web_` (although this is not a breaking requirement). All test files must be put in the `web_tests` directory, and each test class must have the following added to `create_test_suite.py`:

```python
    from .<filename> import <ClassName>

    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(<ClassName>))
```

New tests should additionally follow all rules for Unittest test classes, as they are run using the Unittest framework.

## Other Notes

The web tests do run with the `run_tests` script in the `unit_tests` folder. However, because failure and error numbers are not surfaced by `unittest`, the script does not add the numbers for the web tests to its error tallies.

Web tests can be run using `./run_tests web` in the `unit_tests` folder, or using `python3 -m unittest` in the `web_tests` folder. For compatibility with the other unit tests, the first approach is recommended, as other unit tests can then be run simultaneously.