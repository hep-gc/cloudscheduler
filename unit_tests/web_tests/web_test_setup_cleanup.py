from selenium import webdriver
from cloudscheduler.unit_tests.unit_test_common import load_settings
from time import sleep
import subprocess
import signal
import os

# This module contains setup and cleanup functions for the unittest web tests.
# Setups and cleanups are done here to prevent issues of passing variables
# between test runners and to allow tests to be run individually with the
# unittest framework

def setup(cls, profile, objects):
    # Try/except block here ensures that cleanups will occur even on setup
    # error. If we update to python 3.8 or later, the unittest
    # addClassCleanup() is a better way of handling this.
    try:
        cls.gvar = setup_objects(objects)
        cls.driver = webdriver.Firefox(webdriver.FirefoxProfile(cls.gvar['firefox_profiles'][profile-1]))
        cls.driver.get("https://csv2-dev.heprc.uvic.ca")
        cls.alert = cls.driver.switch_to.alert
        cls.alert.accept()
    except:
        print("Error in test setup")
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
        raise

def setup_objects(objects=[]):
    print('\nUnittest setup:')

    cleanup_objects()

    gvar = load_settings(web=True)

    # detailed descriptions of the test data is in the web_tests README

    gvar['base_group'] = gvar['user'] + '-wig0'
    subprocess.run(['cloudscheduler', 'group', 'add', '-gn', gvar['base_group'], '-un', gvar['user'], '-htcf', gvar['fqdn']], stdout=subprocess.DEVNULL)

    #add groups
    groups_num = 0
    if 'groups' in objects:
        groups_num = 4
    else:
        groups_num = 3
    groups = []
    for i in range(1, groups_num + 1):
        groups.append(gvar['user'] + '-wig' + str(i))
    for i in range(0, groups_num):
        subprocess.run(['cloudscheduler', 'group', 'add', '-htcf', gvar['fqdn'], '-gn', groups[i]])

    #add users
    users_num = 0
    if 'users' in objects:
        users_num = 4
    else:
        users_num = 3
    users = []
    for i in range(1, users_num + 1):
        users.append(gvar['user'] + '-wiu' + str(i))
    flags = []
    flags.append(['-gn', gvar['base_group'] + ',' + gvar['user'] + '-wig1'])
    flags.append(['-SU', 'true','-gn', gvar['base_group'] + ',' + gvar['user'] + '-wig2'])
    flags.append([])
    if 'users' in objects:
        flags.append(['-gn', gvar['user'] + '-wig1'])
    for i in range(0, users_num):
        subprocess.run(['cloudscheduler', 'user', 'add', '-un', users[i], '-upw', gvar['user_secret'], *flags[i]])

    #add clouds
    clouds_num = 0
    if 'clouds' in objects:
        clouds_num = 2
    else:
        clouds_num = 0
    credentials = gvar['cloud_credentials']
    clouds = []
    for i in range(1, clouds_num + 1):
        clouds.append(gvar['user'] + '-wic' + str(i))
    for i in range(0, clouds_num):
        subprocess.run(['cloudscheduler', 'cloud', 'add', '-ca', credentials['authurl'], '-cn', clouds[i], '-cpw', credentials['password'], '-cP', credentials['project'], '-cr', credentials['region'], '-cU', credentials['username'], '-ct', 'openstack', '-g', gvar['base_group']])
    if 'clouds' in objects:
        for i in range(1, 3):
            name = gvar['user'] + '-wim' + str(i) + '.yaml'
            try:
                metadata = open('web_tests/' + name, 'x')
                metadata.write("sample_value_" + str(i) + ": sample_key_" + str(i))
                metadata.close()
            except FileExistsError:
                pass
            filename = os.path.abspath('web_tests/' + name)
            subprocess.run(['cloudscheduler', 'cloud', 'metadata-load', '-cn', gvar['user'] + '-wic1', '-f', filename, '-mn', name])
        # This updates the security group setting, which requires a connection
        # to the cloud. The setup timing is unpredictable, so this loops it 
        # until the connection is established.
        while subprocess.run(['cloudscheduler', 'cloud', 'update', '-cn', clouds[0], '-vsg', 'default']).returncode != 0:
            print("Error connecting to the cloud. This may happen several times. Retrying...")
            sleep(15)

    return gvar

def get_homepage(driver):
    driver.get("https://csv2-dev.heprc.uvic.ca")

def cleanup(cls):
    print("\nUnittest Teardown:")
    if hasattr(cls, 'driver') and cls.driver is not None:
        cls.driver.quit()
    cleanup_objects()

def cleanup_objects():
    gvar = load_settings(web=True)
    gvar['base_group'] = gvar['user'] + '-wig0'

   
    delete_by_type(gvar, ['cloud', '-wic', '-cn', 'cloud_name', ['-g', gvar['base_group']]], 5)
    delete_by_type(gvar, ['user', '-wiu', '-un', 'username', []], 8)
    delete_by_type(gvar, ['group', '-wig', '-gn', 'group_name', []], 7)
    
    # This group must be deleted last - it is the containing group for clouds
    # and cleanup will fail if it is deleted earlier.
    subprocess.run(['cloudscheduler', 'group', 'delete', '-gn', gvar['base_group'], '-Y'], stdout=subprocess.DEVNULL)

def delete_by_type(gvar, type_info, number):
    # type_info is a list of strings (and one list of strings)
    # The first string is the name of the object to be deleted (ex 'user')
    # The second string is the suffix used to generate the names of the test objects (ex '-wiu')
    # The third string is the flag used to indicate this identifier (ex '-un')
    # The fourth string is the column name for the list command (ex 'username')
    # The fifth item is a list of strings that provide extra necessary arguments (this will often be an empty list)

    objects = []
    object_log = None
    object_list = []
    logfile = 'objects.txt'

    try:
        object_log = open(logfile, mode = 'x')
    except FileExistsError:
        object_log = open(logfile, mode = 'w') 
    
    subprocess.run(['cloudscheduler', type_info[0], 'list', '-CSV', type_info[3], *type_info[4]], stdout=object_log)
    
    object_log.close()
    object_log = open(logfile, mode = 'r')

    for line in object_log:
        object_list.append(line.strip())

    for i in range(1, number+1):
        objects.append(gvar['user'] + type_info[1] + str(i))
    
    for object in objects:
        if object in object_list:
            subprocess.run(['cloudscheduler', type_info[0], 'delete', type_info[2], object, *type_info[4], '-Y'])

    object_log.close()

def keyboard_interrupt_handler(signal, frame):
    # This ensures that interrupted tests will still clean up. If cloudscheduler
    # updates to Python 3.8, unittest's addClassCleanups is a better way to 
    # handle this.
    print("\nCleaning up and exiting...")
    cleanup_objects()
    # BaseException is raised here to avoid running into the unittest error
    # handler.
    raise BaseException

signal.signal(signal.SIGINT, keyboard_interrupt_handler)
