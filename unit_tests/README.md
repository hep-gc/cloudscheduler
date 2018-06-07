# Cloudscheduler API Test Framework

## To Use

```bash
# run all the tests
./run_tests
# run a subset of the tests
./run_tests [1-5,10]
# run all the user add tests
./run_tests user_add
# run specific tests in user add
./run_tests user_add[1-5,10]
# run tests from multiple groups
./run_tests user_list user_add[1-5,10] user_delete
# skip setup, cleanup, and all tests
./run_tests [999] -ss -sc
```

## To Develop

Add test files with a name of the form: `test_<object><priority>_<endpoint>[_<detail>].py`.

Ex. `test_user3_update_groups.py`