# Cloudscheduler API Test Framework

## To Use

```bash
./run_tests
```

```bash
#./run_tests <test name>[<sequence #s>]
./run_tests user_list user_add[1-5,10]
```

## To Develop

Add test files with a name of the form: `test_<object><priority>_<endpoint>[_<detail>].py`.

Ex. `test_user3_update_groups.py`