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
        time_difference = datetime.timedelta(days=int(difference*30.4))
    if units == 'years':
        time_difference = datetime.timedelta(days=difference*365)

    before = now - time_difference
    return before

def parse_datetime(datetime_string):
    import datetime

    start_time = None
    try:
        start_time = datetime.datetime.strptime(datetime_string, '%H:%M:%S%b %d, %Y')
        print("Try 1")
    except ValueError:
        try:
            start_time = datetime.datetime.strptime(datetime_string, '%H:%M%b %d, %Y')
            print("Try 2")
        except ValueError:
            try:
                start_time = datetime.datetime.strptime(datetime_string, '%b %d, %Y')
                print("Try 3")
            except ValueError:
                start_time = datetime.datetime.strptime(datetime_string, '%b %Y')
                print("Try 4")

    return start_time

def round_datetime(dt, round, forward):
    import datetime

    round = int(round)
    subtract = datetime.timedelta(seconds=(dt.hour*3600 + dt.minute*60 + dt.second)%round, microseconds=dt.microsecond)
    dt = dt - subtract
    if forward and (round >= 60 or subtract.seconds > 6):
        dt += datetime.timedelta(seconds=round)
    return dt
