import sys

# This module contains a variety of wrapper functions for miscellaneous test 
# actions. This module may be deleted if the functions within all have a better
# location.

def wait_for_openstack_poller(cloud_name, args, wait=sys.maxsize, output=False):

    import subprocess
    from time import sleep

    out = subprocess.DEVNULL
    if output:
        out = None
    count = 0
    while subprocess.run(['cloudscheduler', 'cloud', 'update', '-cn', cloud_name, *args], stdout=out).returncode != 0 and count < wait:
        count += 1
        if output:
            print("Error connecting to the cloud. This may happen several times. Retrying...")
        sleep(15)
    
def misc_file_full_path(filename):
    import os

    path = os.path.abspath('cloudscheduler/unit_tests/web_tests/misc_files/' + filename)
    return path

def skip_if_browsers(browser, skip):
    import unittest

    browser_list = ''
    if len(skip) == 1:
        browser_list = ' ' +  skip[0]
    else:
        for s in skip:
            if s == skip[-1]:
                browser_list += ' and ' + s
            else:
                browser_list += ' ' + s + ','
    message = "Incompatible with" + browser_list
    if browser in skip:
        raise unittest.SkipTest(message)

def skip_if_flag(name, flag, value):
    import unittest

    message = name + ' flag is set to ' + str(value)

    if flag == value:
        raise unittest.SkipTest(message)

def time_before(difference, units):
    import datetime

    now = datetime.datetime.now()
    time_difference = None
    if units == 'minutes':
        time_difference = datetime.timedelta(minutes=difference)
    if units == 'hours':
        time_difference = datetime.timedelta(hours=difference)
    if units == 'days':
        time_difference = datetime.timedelta(days=difference)
    if units == 'months':
        time_difference = datetime.timedelta(days=int(difference*(365/12)))
    if units == 'years':
        time_difference = datetime.timedelta(days=difference*365 + difference//4 - difference//100)

    before = now - time_difference
    return before

def parse_datetime(datetime_string):
    import datetime

    start_time = None
    try:
        start_time = datetime.datetime.strptime(datetime_string, '%H:%M:%S%b %d, %Y')
    except ValueError:
        try:
            start_time = datetime.datetime.strptime(datetime_string, '%H:%M%b %d, %Y')
        except ValueError:
            try:
                start_time = datetime.datetime.strptime(datetime_string, '%b %d, %Y')
            except ValueError:
                try:
                    start_time = datetime.datetime.strptime(datetime_string, '%b %d%Y')
                except ValueError:
                    try:
                        start_time = datetime.datetime.strptime(datetime_string, '%b %Y')
                    except ValueError:
                        try:
                            start_time = datetime.datetime.strptime(datetime_string, '%H:%M')
                        except ValueError:
                            start_time = datetime.datetime.strptime(datetime_string, '%b %d')

    return start_time

def margin_units_from_units(units):
    if units == 'seconds' or units == 'minutes' or units == 'hours':
        return 'minutes'
    elif units == 'days':
        return 'hours'
    elif units == 'weeks' or units == 'months' or units == 'years':
        return 'days'

def time_within_margin(shown_time, true_time, margin, units):
    import datetime

    first = None
    last = None
    # last is multiplied by 2 to account for the graph sometimes rounding the
    # value forward
    # first has 1 added for the same reason (with months)
    if units == 'minutes':
        first = true_time - datetime.timedelta(seconds=int(margin*60))
        last = true_time + datetime.timedelta(seconds=int(margin*120))
    elif units == 'hours':
        first = true_time - datetime.timedelta(hours=margin)
        last = true_time + datetime.timedelta(hours=margin*2)
    elif units == 'days':
        first = true_time - datetime.timedelta(days=margin*2)
        last = true_time + datetime.timedelta(days=margin+1)
    return shown_time > first and shown_time < last

def parse_command_line_arguments(args, classes, has_regular_user):
    import unittest

    suite = unittest.TestSuite()
    tests = []

    firefox = False
    chromium = False
    opera = False
    chrome = False
    super_user = False
    regular_user = False

    for arg in args:
        if arg == '--firefox' or arg == '-f':
            firefox = True
        elif arg == '--chromium' or arg == '-cb':
            chromium = True
        elif arg == '--opera' or arg == '-o':
            opera = True
        elif arg == '--chrome' or arg == '-gc':
            chrome = True
        elif arg == '--super-user' or arg == '-su':
            super_user = True
        elif arg == '--regular-user' or arg == '-ru':
            regular_user = True

    if not firefox and not chromium and not opera and not chrome:
        firefox = True
        chromium = True
        opera = True
        chrome = True
    if not super_user and not regular_user:
        super_user = True
        regular_user = True

    if firefox and super_user:
        tests.append(classes[0])
    if firefox and regular_user:
        if has_regular_user:
            tests.append(classes[1])
    if chromium and super_user:
        if has_regular_user:
             tests.append(classes[2])
        else:
             tests.append(classes[1])
    if chromium and regular_user:
        if has_regular_user:
            tests.append(classes[3])
    if opera and super_user:
        if has_regular_user:
            tests.append(classes[4])
        else:
            tests.append(classes[2])
    if opera and regular_user:
        if has_regular_user:
            tests.append(classes[5])
    if chrome and super_user:
        if has_regular_user:
            tests.append(classes[6])
        else:
            tests.append(classes[3])
    if chrome and regular_user:
        if has_regular_user:
            tests.append(classes[7])

    for test in tests:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))
    return suite
