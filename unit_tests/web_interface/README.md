# Web Interface Tests
This is for anyone who wants to run or continue the creation of these tests.
## Initial setup
* You run `py setup.py -s` (assuming that this is a first-ever run or the tests were previously cleaned up). This sets up all of the test objects (groups, clouds, etc.) that the tests will assert the presence of and manipulate.
* You create 3 separate Firefox profiles (`about:profiles`), each one having the credentials of one of the test users. The format of the names of these users is `<your username>-wiu<1-3>`. Their passwords are all the same, and need to match the password in the test credentials file (`~/cloudscheduler/unit_tests/credentials.yaml`). The tests currently only actually use the first user. The first user is supposed to perform most actions *not* requiring privileges, the second is supposed to perform most actions requiring privileges (adding and deleting groups and users), and the third is not in any groups (meaning it cannot perform any actions). (For the reason these profiles are necessary, see my co-op report.)
## How a test runs
After completing the inital setup:
* You run `py test_status.py` or `py -m unittest test_status.py`.
    * `unittest` calls `test_status.TestStatus.setUpClass()`, which calls `web_common.load_web_settings()`, which calls `unit_test_common.load_settings()` to load both your CLI defaults (`~/.csv2/unit-test/settings.yaml`) and your test credentials (`~/cloudscheduler/unit_tests/credentials.yaml`) into a global variable called `gvar`. If you don't have a CLI defaults file, you will need to create one using the CLI. If you don't have a test credentials file, `unit_test_common.load_settings()` will prompt you for the information that would be in it and create it for you. `web_common.load_web_settings()` also calls `web_common.switch_user()` which starts a new Firefox session controlled by WebDriver for the tests to take place in.
    * `unittest` calls `TestStatus.test_*()`. These methods access elements (which represent HTML tags) in Firefox using WebDriver and make assertions about them. They use a few common functions:
        * `web_common.assert_one()` asserts that the current page or a particular element has exactly one child element that meets certain criteria. (See its docstring for more.)
        * `web_common.submit_form()` submits a `<form>` with specified data and asserts what the response is.
        * `web_common.submit_valid_combinations()` and `web_common.submit_invalid_combinations()` both take datasets (dictionaries) and submit each of them in the same form, asserting what the response is each time.
* If you want to run tests again, run `py setup.py` to cleanup all of the used test objects and setup fresh ones. If you are done testing, run `py setup.py -c` to just cleanup.
## Progress
I have created what I believe are thorough tests for the Status and Clouds pages. When I left (2020-04-30) these pages had 4 and 11 tests, respectively, and they were all passing. I have started creating tests for the Aliases page, but this is not finished. I have not tested switching the active group yet, as I thought it would be appropriate to do that along with the other group tests.
The plan was to have tests for multiple browsers, but so far only Firefox tests have been implemented. 
## Known bugs
### Initial page stops loading prematurely
Sometimes when a test suite starts, Firefox will open and start loading the first page, then just stop loading before there is anything on the page. As a temporary fix you can manually navigate to the correct page when this happens, and Firefox does not seem to stop twice in one run. I have searched online, but this does not seem to be a widespread issue.
