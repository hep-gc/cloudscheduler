# The Cloudscheduler V2 Web Testing Framework

This document is the primary source of information on the cloudscheduler v2 web testing framework. 

For people using the tests: follow the [setup instructions](#setup), then use the [instructions on running tests](#running-tests).

For people writing tests: read the entirety of the document. For additional documentation, consult the [old README](./docs/OLD_README.md), [web test docs](./docs/web_test_docs.md), and [template file](./docs/web_test_templates.md).

## Setup

There are three ways to set up the web tests, which have varying degrees of automation. Additionally, there are [final setup instructions](#other-setup) that all three methods need.

### Full Setup Script

The full setup scripts have been written for CentOS 7 and Ubuntu. They are [web_test_setup_full_centos.sh](./setup_scripts/web_test_setup_full_centos.sh) and [web_test_setup_full_ubuntu.sh](./setup_scripts/web_test_setup_full_ubuntu.sh).

Requirements to run the full setup:
- one of the above operating systems
- sudo access on your machine
- cloudscheduler web account credentials
- an account on the cloudscheduler server machine
- an ssh key to the cloudscheduler server machine that does not require a passphrase
- the cloudscheduler repository in the user's home directory

### Object Setup Script

The object setup script should work for any linux-based distribution. However, it has only been tested on CentOS 7. It is [web_test_setup_objects.sh](./setup_scripts/web_test_setup_objects.sh).

Requirements to run the object setup:
- a linux-based machine (linux or MacOS)
- the cloudscheduler repository in the user's home directory
- cloudscheduler web account credentials
- an account on the cloudscheduler server machine
- an ssh key to the cloudscheduler server machine that does not require a passphrase

This script replaces steps 5-8 of the manual setup. All other steps will need to be done as described.

### Manual Setup

The manual setup can be done on any OS.

Steps:
1. Install `python3` using your default package manager 
2. Install Selenium Webdriver for Python via `pip3 install selenium`
3. Install the Openstack cli via `pip3 install python-openstackclient` 
4. Set your host computer's environment variable `XDG_SESSION_TYPE` to `wayland`
5. Download a [CernVM image](http://cernvm.cern.ch/releases/production/cernvm4-micro-2020.07-1.hdd), move it to [the `misc_files` directory](./misc_files), and name it `{user}-wii1.hdd`
6. Create three copies of the CernVM image, called `{user}-wii2.hdd`, `{user}-wii3.hdd`, and `{user}-wii4.hdd`
7. Create two public keys using `ssh-keygen`, naming them `{user}-wik3` and `invalid_web_test`. Do not use a passphrase. Put them in [the `misc_files` directory](./misc_files)
8. On the server machine, in your home directory, add the [job.condor](./misc_files/job.condor) file, updating the `{user}-wig0` with your username, and the [job.sh](./misc_files/job.sh) file
9. Run `cloudscheduler defaults set`, saving the result as the `unit-test` server
10. Set up the browsers

### Browser Setup

There are four browsers that the tests work with. To run the full script, all the browsers must be installed, but tests can be run with as few as one browser.

#### Firefox and Geckodriver

1. If Firefox is not installed, download it from [Mozilla](https://www.mozilla.org/en-CA/firefox/new/)
2. Download Geckodriver from [GitHub](https://github.com/mozilla/geckodriver/releases/tag/v0.28.0)
3. Unzip Geckodriver

#### Chromium and Chromedriver

1. If on CentOS (and perhaps others), install the EPEL repository
2. Install Chromium from the default package manager
3. Install Chromedriver from the default package manager 

#### Opera and OperaChromiumDriver

1. Download Opera from their [web site](https://www.opera.com/download)
2. Download OperaChromiumDriver from [Github](https://github.com/operasoftware/operachromiumdriver/releases)
3. Unzip OperaChromiumDriver
4. Move the operadriver executable to `/usr/bin` and ensure everyone has execute permissions on it

#### Chrome and Chromedriver

1. Download Chrome from their [web site](https://www.google.com/intl/en_ca/chrome/)
2. If on CentOS (and perhaps others), install the EPEL repository
3. Install Chromedriver from the default package manager

### Other Setup

This setup must be done for all tests.

- set the system time to the correct time zone
- ensure the system can access a GUI

## Running Tests

There are three different ways of running the web tests: the `run_tests` script, running as a module, and running via unittest.

`./run_tests web` integrates with the rest of the unit tests. This script can run all the web tests or a single browser, using `./run_tests web_<browser>`. It can be run alongside other unit tests, although it cannot run individually numbered tests like the typical unit tests. It must be run in a directory with a symbolic link to the main cloudscheduler folder.

Running as a module is done via `python3 -m <module_name> <options>`. It must be run in a directory with a symbolic link to the main cloudscheduler folder. The module name can be any test module, and the options are as follows, where, if no flag of a type is specified, all tests of that type will be run:

| Short-Form Tag | Long-Form Tag    | Meaning                                   |
|----------------|------------------|-------------------------------------------|
| `-f`           | `--firefox`      | Run the Firefox tests                     |
| `-cb`          | `--chromium`     | Run the Chromium (chromium-browser) tests |
| `-o`           | `--opera`        | Run the Opera tests                       |
| `-gc`          | `--chrome`       | Run the Chrome (google-chrome) tests      |
| `-su`          | `--super-user`   | Run the tests with a super user           |
| `-ru`          | `--regular-user` | Run the tests with a regular user         |

Running via unittest is done via `python3 -m <file_name>.<ClassName>.<function_name> -v`. It must be run in a directory with a symbolic link to the main cloudscheduler folder.

## Test Debugging

### Error Connecting to Cloud

The tests may display an error like the following:

```
Error: CV-01749 cloud update, "{user}-wic1" failed - specified value in list of values does not exist: vm_security_groups=default, group_name={user}-wig0, cloud_name={user}-wic1.
Error connecting to the cloud. This may happen several times. Retrying...
```

This is an expected error. The tests will continue to retry until the openstack poller gets the resources.

### Resource Warning: Unclosed Socket

Some tests have displayed the following error:

```
/usr/local/lib64/python3.6/site-packages/yaml/scanner.py:286: ResourceWarning: unclosed <socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('127.0.0.1', 40206), raddr=('127.0.0.1', 41942)>
```

This error does not cause any known problems for the tests and may be ignored.

### Process Unexpectedly Closed

Attempting to run tests can cause the following error:

```
selenium.common.exceptions.WebDriverException: Message: Process unexpectedly closed with status 1
```

This is usually a result of x11 forwarding failing.

## Creating New Test Files

New test files should be built off the template in [web_test_template.md](./web_test_template.md#test_web_page.py). These files should be placed in [the `web_tests` directory](./).

The new tests should be imported into and added to [create_test_suite.py](./create_test_suite.py).

## Writing Tests

[web_test_assertions_v2.py](./web_test_assertions_v2.py) contains the current set of web test assertions. These can be used on any cloudscheduler objects, and are documented further in [the web test docs](./web_test_docs.md).

All supporting files (uploads, downloads, etc) should be stored in the [misc_files](./misc_files) folder.

The settings load a variable called `cls.gvar`, which contains a variety of important variables:

| Containing Key    | Key             | Meaning                                                                                  |
|-------------------|-----------------|------------------------------------------------------------------------------------------|
| N/A               | fqdn            | fully-qualified domain name of the server                                                |
| N/A               | user_secret     | the password for the created user accounts                                               |
| N/A               | address         | the URL of the csv2 server                                                               |
| N/A               | user            | the current user's username                                                              |
| N/A               | server_username | the username of the account on the server vm                                             |
| N/A               | server_port     | the port to access the server vm on                                                      |
| N/A               | server_keypath  | the path to a key with no passphrase for accessing the server vm                         |
| N/A               | keys_accessible | whether the user's keys are the ones the openstack poller uses                           |
| N/A               | max_wait        | the amount of time the pages are permitted to try to load (may be unused)                |
| N/A               | setup_required  | if the tests need setup (may be unused)                                                  |
| N/A               | base_group      | the group all objects are created in unless otherwise specified (gvar['user'] + '-wig0') |
| N/A               | browser         | the browser the tests are being run in                                                   |
| cloud_credentials | authurl         | the url of the cloud provider to create clouds on                                        |
| cloud_credentials | password        | the user's account password on the cloud provider                                        |
| cloud_credentials | project         | the project to create clouds within                                                      |
| cloud_credentials | region          | the region the cloud provieder is in                                                     |
| cloud_credentials | username        | the user's account username on the cloud provider                                        |
| oversize          | varchar_20      | a string that's too long for the SQL varchar 20 type                                     |
| oversize          | varchar_32      | a string that's too long for the SQL varchar 32 type                                     |
| oversize          | varchar_64      | a string that's too long for the SQL varchar 64 type                                     |
| oversize          | varchar_128     | a string that's too long for the SQL varchar 128 type                                    |
| oversize          | varchar_256     | a string that's too long for the SQL varchar 256 type                                    |
| oversize          | varchar_512     | a string that's too long for the SQL varchar 512 type                                    |
| oversize          | int_11          | an integer that's too long for the SQL int 11 type                                       |
| oversize          | bigint_20       | an integer that's too long for the SQL bigint 20 type                                    |

### Page Objects

Page objects are classes stored in the [web_test_page_objects.py](./web_test_page_objects.py) file. They are used by the tests to interact with the webpage.

New page objects should inherit from `Page`, the base page class, and the page object's `__init__` function should call the the base `__init__` function.

A page object should contain methods for interacting with each element on the page. Similar elements (such as a list of group checkboxes) may have one interaction function, but objects with different purposes (such as the group checkboxes and the superuser checkbox) should have different methods, even if the way of interacting with them is very similar.

The [web_test_interactions.py](./web_test_interactions.py), [web_test_javascript_interactions.py](./web_test_javascript_interactions.py), and [web_test_xpath_selectors.py](./web_test_xpath_selectors.py) files are used to wrap common interactions within the page objects.

## Test Objects

The test setup and cleanup creates a variety of objects:

| Keyword  | Object                                     | Details                                         | Purpose                |
|----------|--------------------------------------------|-------------------------------------------------|------------------------|
| N/A      | {user}-wiu1                                | Regular user in the {user}-wig1 group           | active testing account |
| N/A      | {user}-wiu2                                | Super user in the {user}-wig2 group             | active testing account |
| N/A      | {user}-wiu3                                | Regular user                                    | unknown                |
| N/A      | {user}-wig1                                | Contains {user}-wiu1                            | editing                |
| N/A      | {user}-wig2                                | Contains {user}-wiu2                            | editing                |
| N/A      | {user}-wig0::{user}-wic1                   | none                                            | editing                |
| N/A      | {user}-wig0::{user}-wic2                   | none                                            | deletion               |
| users    | {user}-wiu4                                | Regular user in the {user}-wig1 group           | editing                |
| groups   | {user}-wig4                                | none                                            | deletion               |
| clouds   | {user}-wig0::{user}-wic1::{user}-wim1.yaml | none                                            | editing                |
| clouds   | {user}-wig0::{user}-wic1::{user}-wim2.yaml | none                                            | deletion               |
| aliases  | {user}-wig0.{user}-wia1                    | contains the {user}-wic1 cloud                  | editing                |
| aliases  | {user}-wig0.{user}-wia2                    | contains the {user}-wic1 and {user}-wic2 clouds | editing                |
| aliases  | {user}-wig0.{user}-wia3                    | contains the {user}-wic1 cloud                  | deletion               |
| defaults | {user}-wig1::{user}-wim1.yaml              | none                                            | editing                |
| defaults | {user}-wig1::{user}-wim2.yaml              | none                                            | deletion               |
| images   | {user}-wig0::{user}=wic1::{user}-wii1.hdd  | RAW format                                      | editing                |
| images   | {user}-wig0::{user}=wic1::{user}-wii2.hdd  | RAW format                                      | deletion               |
| keys     | {user}-wik1                                | none                                            | selection              |
| keys     | {user}-wik2                                | none                                            | deletion               |
| servers  | {user}-wis1                                | credentials of the {user}-wiu1 user             | reading settings       |
| servers  | {user}-wis2                                | credentials of the {user}-wiu2 user             | reading settings       |

### New Test Objects

New test objects should be added to the `setup_objects` function in [web_test_setup_cleanup.py](./web_test_setup_cleanup.py). A corresponding deletion method should be added in `cleanup_objects`.

## Future Development

This is a list of possible future features that have not been implemented.

### Future Tests

- TMultiple types of clouds (held up on not having access to multiple types of clouds)
- Typing in select elements (works as a search feature)
- Drag and drop actions on the status page plot (zoom in, double-click zoom out, move axes)
- Additional config file tests (only `condor_poller.py` is currently tested)

### Future Features

- Standardize integer vs string for cloud page object inputs
- Update comments/docstrings
- Remove code that was commented out for testing
- Edit openstack delete method to properly delete keys that are too long for the cloudscheduler interface
- Alternate assertion information passing (investigate if the logfiles are the most effective way to pass information)
- Speed up setup/teardown
- Safari/Edge/IE tests (likely require VMs and use of `webdriver.Remote`)
- Headless test option (for Firefox and Chrome only)
- Better keyboard interrupt handling (exit testing framework instead of erroring remaining tests)
- Investigate vms not registering in condor (does not appear to affect tests, but vms remain unregistered)