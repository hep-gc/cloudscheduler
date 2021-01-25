from selenium import webdriver
from cloudscheduler.unit_tests.unit_test_common import load_settings
import subprocess

# setups and cleanups are done here to prevent issues of passing variables
# between test runners and to allow tests to be run individually with the
# unittest framework

def setup():
    print('Unittest setup:')

    cleanup()

    gvar = load_settings(web=True)

    #detailed descriptions of the test data is in the web_tests README

    #add groups
    groups = []
    for i in range(1, 5):
        groups.append(gvar['user'] + '-wig' + str(i))
    for i in range(0, 4):
        subprocess.run(['cloudscheduler', 'group', 'add', '-htcf', gvar['fqdn'], '-gn', groups[i]])

    #add users
    users = []
    for i in range(1, 4):
        users.append(gvar['user'] + '-wiu' + str(i))
    flags = []
    flags.append(['-gn', gvar['user'] + '-wig1'])
    flags.append(['-SU', 'true','-gn', gvar['user'] + '-wig2'])
    flags.append([])
    for i in range(0, 3):
        subprocess.run(['cloudscheduler', 'user', 'add', '-un', users[i], '-upw', gvar['user_secret'], *flags[i]])

    return gvar

def cleanup():
    gvar = load_settings(web=True)
    
    delete_by_type(gvar, ['user', '-wiu', '-un', 'username'], 3)
    delete_by_type(gvar, ['group', '-wig', '-gn', 'group_name'], 6)

def delete_by_type(gvar, type_info, number):
    # type_info is a list of strings
    # The first string is the name of the object to be deleted (ex 'user')
    # The second string is the suffix used to generate the names of the test objects (ex '-wiu')
    # The third string is the flag used to indicate this identifier (ex '-un')
    # The fourth string is the column name for the list command (ex 'username')

    objects = []
    object_log = None
    object_list = []

    try:
        object_log = open('objects.txt', mode = 'x')
    except FileExistsError:
        object_log = open('objects.txt', mode = 'w') 
    
    subprocess.run(['cloudscheduler', type_info[0], 'list', '-CSV', type_info[3]], stdout=object_log)
    
    object_log.close()
    object_log = open('objects.txt', mode = 'r')

    for line in object_log:
        object_list.append(line.strip())

    for i in range(1, number+1):
        objects.append(gvar['user'] + type_info[1] + str(i))
    
    for object in objects:
        if object in object_list:
            subprocess.run(['cloudscheduler', type_info[0], 'delete', type_info[2], object, '-Y'])

    object_log.close()
