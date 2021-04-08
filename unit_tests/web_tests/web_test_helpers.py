import sys

# This module contains a variety of wrapper functions for miscellaneous test 
# actions. This module may be deleted if the functions within all have a better
# location.

server_url = 'https://csv2-dev.heprc.uvic.ca'

def get_homepage(driver):
    driver.get(server_url)

def get_homepage_login(driver, username, password):
    from time import sleep
    from selenium.common.exceptions import UnexpectedAlertPresentException

    url_split = server_url.split('//')
    authenticated_url = url_split[0] + '//' + username + ':' + password + '@' + url_split[1]
    driver.get(authenticated_url)

def wait_for_openstack_poller(cloud_name, item_flag, item_name, wait=sys.maxsize, output=False):

    import subprocess
    from time import sleep

    out = subprocess.DEVNULL
    if output:
        out = None
    count = 0
    while subprocess.run(['cloudscheduler', 'cloud', 'update', '-cn', cloud_name, item_flag, item_name], stdout=out).returncode != 0 and count < wait:
        count += 1
        if output:
            print("Error connecting to the cloud. This may happen several times. Retrying...")
        sleep(15)
    
def misc_file_full_path(filename):
    import os

    path = os.path.abspath('web_tests/misc_files/' + filename)
    return path

def cumulative_days(month, year):
    feb = 28
    if year%4 == 0 and year%100 !=0:
        feb = 29
    days = [31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    sum = 0
    for number in days[:month-1]:
        sum += number
    return sum

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

def round_datetime(dt, round, forward):
    import datetime

    round = int(round)
    subtract = datetime.timedelta(seconds=(dt.hour*3600 + dt.minute*60 + dt.second)%round, microseconds=dt.microsecond)
    dt = dt - subtract
    if subtract.seconds > (round / 15) and forward:# and not (subtract.seconds < 6 and subtract.seconds // 60 == 0):
        dt += datetime.timedelta(seconds=round)
    return dt

def round_date(dt, round, forward):
    import datetime

    if round < 30:
        subtract = datetime.timedelta(days=(dt.year*365 + dt.year//4 - dt.year//100 + cumulative_days(dt.month, dt.year) + dt.day) % round)
        dt = dt - subtract
        print(dt)
        print(forward)
        print(round)
        if forward and not (round > 13 and subtract.days <= 1):
            dt += datetime.timedelta(days=round)
        if round >= 7:
            if dt.weekday() != 6:
                if forward and round > 10:
                    dt += datetime.timedelta(days=7-dt.isoweekday())
                else:
                    dt -= datetime.timedelta(days=dt.isoweekday())
            if not forward and round < 10:
                dt += datetime.timedelta(days=7)
        print(dt)
        try:
            dt.replace(day=dt.day+1)
        except ValueError:
            if forward:# and dt.day < 30:
                dt += datetime.timedelta(days=round)
        #if not forward and dt.day == 1:
        #    if (dt - datetime.timedelta(days=1)).day < 30:
        #        dt -= datetime.timedelta(days=1)
    else:
        if forward:
            dt = dt.replace(month=(dt.month)%12 + 1)
        else:
            dt = dt.replace(month=(dt.month)%12 - 1)
        while (dt.month-1)%(round//31) != 0:
            if dt.month >= 12:
                dt = dt.replace(month=1, year= dt.year+1)
            else:
                try:
                    dt = dt.replace(month=dt.month+1)
                except ValueError:
                    dt = dt.replace(month=dt.month+2, day=1)
    return dt

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
