import sys
import subprocess
from time import sleep
import os

# This module contains a variety of wrapper functions for miscellaneous test 
# actions. This module may be deleted if the functions within all have a better
# location.

def wait_for_openstack_poller(cloud_name, item_flag, item_name, wait=sys.maxsize, output=False):
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
    path = os.path.abspath('web_tests/misc_files/' + filename)
    return path
