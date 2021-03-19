import sys

# This module contains a variety of wrapper functions for miscellaneous test 
# actions. This module may be deleted if the functions within all have a better
# location.

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
    for number in days[:month]:
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
    if (round >= 60 or subtract.seconds > 6) and forward and not (subtract.seconds < 6 and subtract.seconds // 60 == 0):
        print(forward)
        dt += datetime.timedelta(seconds=round)
    return dt

def round_date_old(dt, round, forward):
    import datetime

    subtract = datetime.timedelta(days=(dt.year*365 + dt.year//4 - dt.year//100 + cumulative_days(dt.month, dt.year) + dt.day) % round)
    dt = dt - subtract
    print(dt)
    print(round)
    if forward:
        dt += datetime.timedelta(days=round)
    if round >= 7:
        #if dt.weekday() < 2:
        if dt.weekday() != 6:
            dt -= datetime.timedelta(days=dt.isoweekday())
        #else:
        #    dt += datetime.timedelta(days=(7 - dt.isoweekday()))
    print(dt)
    #if round > 30:
    #    divide = round//30
    #    print(divide)
    #    if (dt.month-1)%divide != 0:
    #        dt += datetime.timedelta(days=30*(divide-(dt.month-1)%divide))
    return dt

def round_date(dt, round, forward):
    import datetime

    if round < 30:
        dt = round_date_old(dt, round, forward)
    else:
        print(round//31)
        if forward:
            dt = dt.replace(month=dt.month+1)
        while (dt.month-1)%(round//31) != 0:
            if dt.month >= 12:
                dt = dt.replace(month=1, year= dt.year+1)
            else:
                dt = dt.replace(month=dt.month+1)
    print(dt)
    return dt
