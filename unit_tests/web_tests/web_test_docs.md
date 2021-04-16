# Web Test Docs

This document is an overview of the various common web test modules and functions. It is intended for people extending the web tests.

## Web Test Assertions (v2)

The `web_test_assertions` v1 file is no longer in use.

The `web_test_assertions_v2` module is a set of assertions on csv2 objects. The four functions that should be called from outside the module are `assertExists` (which checks for the presence of an object), `assertNotExists` (which checks for the lack of presence of an object), `assertHasAttribute` (which checks that a certain object has a certain attribute), and `assertHasNotAttribute` (which checks that a certain object does not have a certain attribute).

Each assertion takes a list of arguments, as follows:

| Argument Name  | Argument Meaning                                       | Example          | Specified For                         | Default   |
|----------------|--------------------------------------------------------|------------------|---------------------------------------|-----------|
| type           | the type of object                                     | cloud            | all methods                           | N/A       |
| name           | the name of the object being asserted on               | {user}-wic1      | all methods                           | N/A       |
| attribute      | the name of the type of attribute                      | metadata_names   | attribute assertions                  | N/A       |
| attribute_name | the name of the attribute being asserted about         | {user}-wim1.yaml | attribute assertions                  | N/A       |
| group          | the name of the group the object is in                 | {user}-wig0      | assertions on objects in groups       | `None`    |
| err            | the margin of error of the assertion                   | 3                | integer assertions with a range       | `None`    |
| metadata_cloud | the cloud a cloud metadata is in                       | {user}-wic1      | cloud metadata assertions             | `None`    |
| defaults       | whether the object is a default                        | `True`           | default object assertions             | `False`   |
| name_field     | whether the object has a name flag in the list command | `False`          | objects with no name flag             | `True`    |
| settings       | whether the object is a user setting                   | `True`           | user setting object assertions        | `False`   |
| server         | the name of the server to assert on                    | {user}-wis1      | objects requiring an alternate server | unit-test |
| image_cloud    | the cloud a cloud image is in                          | {user}-wic1      | cloud image assertions                | `None`    |
| is_retry       | whether this is the second try of an assertion         | `False`          | never (internal use only)             | `False`   |

## Web Test Helpers

The `web_test_helpers` module is an assortment of functions that go nowhere else. This includes a variety of functions for the handling of datetimes, login functions, and cli functions.

### Datetime Functions

The `web_test_helpers` module currently contains all of the web tests' datetime handling, for the status pages.

The `cumulative_days` function calculates how many days were in the year up to and including a month. It takes a month and a year. It is part of the original datetime handling and is unused.

The `time_before` function calculates a specified amount of time before now. It takes a unit and a number of units.

The `parse_datetime` function parses a datetime from the format used on the status page chart. It takes a string read from the status page chart.

The `round_datetime` function rounds a datetime by a specified number of seconds. It takes a datetime, the seconds to round it by, and whether it should be rounded forward or backward. It is part of the original datetime handling and is unused.

The `round_date` function rounds a date by a specified number of days. It takes a datetime, the days to round it by, and whether it should be rounded forward or backward. It is part of the original datetime handling and is unused.

The `margin_units_from_units` function determines the units of the margin of error based on the units of the number. The conversion is as follows:

| Units   | Margin Units |
|---------|--------------|
| seconds | minutes      |
| minutes | minutes      |
| hours   | minutes      |
| days    | hours        |
| weeks   | days         |
| months  | days         |
| years   | days         |

The `time_within_margin` function calculates whether a time is within the proper margin. It takes a time listed on the chart (`shown_time`), the time that actually is correct (`true_time`), a margin, and the units of the margin.

### Other Functions

The `web_test_helpers` module also contains a set of functions with no specific module.

The `get_homepage` function is used in test setups to initially get the homepage. It requires the driver as an argument.

The `get_homepage_login` function gets the homepage using username/password authentication. It requires the driver and the user's csv2 username and password as arguments.

The `wait_for_openstack_poller` function tries a specified number of times to update a cloud with an object, in order to wait for the openstack poller. Its arguments are as follows:
- `cloud_name`, the name of the cloud the object should be in
- `args`, a list of item flags and names of the objects being updated with
- `wait`, the amount of times to look before failing (defaults to `sys.MAXSIZE`)
- `output`, whether to print the error messages or not (defaults to `False`)

The `misc_file_full_path` function takes a file name in the `misc_files` folder and returns its full absolute path.

The `parse_command_line_arguments` function parses command line arguments for the direct module running of the test files. It takes a list of arguments, a list of available test classes, and a flag stating if the tests have regular user classes.

## Web Test Interactions

The `web_test_interactions` module wraps Selenium locators, waits, and actions. It should not be used directly in the test modules - instead, it should be used in the page objects file.

Each method takes arguments for the driver, the locator object (ie the name, id, or similar), and the timeout (which defaults to a value set at the top of the file). Actions that require more information take additional arguments - for example, the string to type in a text box, or the distance to slide a slider.

## Web Test Javascript Interactions

The `web_test_javascript_interactions` module is an alternate version of the `web_test_interactions` module. It should be used in the same circumstances, but the `web_test_interactions` module is preferred, as it emulates user interactions more closely.

## Web Test Page Objects

The `web_test_page_objects` module contains the page object classes by which the tests should interact with the page objects. 

This module has a base class, `Page`, which all other classes inherit from. This class defines the default behavior for each page, and contains some common components.

Each page object contains unique methods for interacting with that specific page. The majority of these methods simply locate the object and perform an action on it. However, some methods are required to perform more complicated actions, such as determining when a slider has gotten to the correct point. The page objects also contain assertions on the given page.

Most page object classes contain an internal variable that stores the active object or objects in the sidebar. This variable is handled by the page object class and never needs to be dictated from the outside.

## Web Test XPath Selectors

The `web_test_xpath_selectors` module contains a set of wrapper functions for the XPath selectors of various objects.

This module should not be imported into the test scripts themselves. Instead, it should be used through the `web_test_page_objects` module.