# Cloudscheduler API Test Framework

## To Use

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
./run_tests [999] -ss -sc
```

## Running the Database Interaction Tests

These tests are set to only run when specified:

```
./run_tests db
```

For a successful test run, the following must be done first:

1. Stop all csv2 services. `systemctl stop 'csv2*'`
1. Restart the mariadb service. `systemctl restart mariadb`
1. Load the test vm data into the database. `mysql -ucsv2 -p csv2 < /opt/cloudscheduler/unit-tests/csv2_vm_dump.sql`
1. Restart the web server. `systemctl restart httpd`
1. Run the tests. `./run_tests db`

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
