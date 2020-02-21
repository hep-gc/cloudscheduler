# Cloudscheduler API Test Framework

## To Use

Create a `unit-test` server alias in defaults (using the `cloudscheduler defaults set` cli command).
The `unit-test` server should have the `server-address`, `server-user`, and `server-password` of a privleged user.
Server credentials used to create test clouds (username, password, region, and project) and a randomly generated password used to create test users are saved in `~/cloudscheduler/unit-tests/credentials.yaml`. If you attempt to run the tests without this file, you will be prompted for the server credentials (which will then be saved in the file).

To run tests:

```bash
# run all the tests
./run_tests
# run a subset of the tests
./run_tests [1-5,10]
# run all user tests
./run_tests user
# run all the user add tests
./run_tests user_add
# run specific tests in user add
./run_tests user_add[1-5,10]
# run tests from multiple groups
./run_tests user_list user_add[1-5,10] user_delete
# skip setup, cleanup, and all tests
./run_tests [9999] -ss -sc
```
## To Develop

Add test files with a name of the form: `test_<object>[<priority>]_<endpoint>[_<detail>].py`.

Ex. `test_user3_update_groups.py`

When writing tests for a new object:

1. Create a setup file named `<object>_requests_setup.py`
1. Create a cleanup file named `<object>_requests_cleanup.py`
1. Add the object name to the `TEST_OBJECTS` list in `run_tests`
1. Create test files

For the error code resequence to work correctly a line like this must be present in the test file:

```python
# lno: GV - error code identifier.
```
