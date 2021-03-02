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

    #setup gvar additions
    oversize = {}
    oversize['varchar_20'] = 'invalid-web-test-20-char'
    oversize['varchar_32'] = 'invalid-web-test-too-long-32-char'
    oversize['varchar_64'] = 'invalid-web-test-string-that-is-too-long-for-64-character-sql-data-field'
    oversize['varchar_128'] = 'invalid-web-test-data-example-for-testing-string-that-is-too-long-for-a-one-hundred-and-twenty-eight-character-sql-database-field-and-is-lowerdash'
    oversize['varchar_256'] = 'invalid-web-test-data-example-for-testing-string-that-is-too-long-for-a-two-hundred-and-fifty-six-character-sql-database-field-and-is-also-lowerdash-compliant-so-that-verification-looking-for-lowerdash-compliant-strings-will-not-get-tripped-up-and-throw-an-error'
    oversize['varchar_512'] = 'invalid-web-test-data-example-for-testing-string-that-is-too-long-for-a-five-hundred-and-twelve-character-sql-database-field-and-is-also-lowerdash-compliant-so-that-verification-looking-for-lowerdash-compliant-strings-will-not-get-tripped-up-and-throw-an-error-and-is-also-this-extremely-long-because-some-database-fields-have-their-length-cut-off-at-five-hundred-and-twelve-characters-so-tests-for-those-fields-require-a-string-that-is-over-five-hundred-and-twelve-characters-long-which-is-why-this-is-created-in-the-setup-because-this-would-be-a-hassle-to-type-every-time'
    oversize['int_11'] = 2147483690
    oversize['bigint_20'] = 9223372036854775810
    gvar['oversize'] = oversize

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
        subprocess.run(['cloudscheduler', 'group', 'add', '-htcf', gvar['fqdn'], '-gn', groups[i], '-un', gvar['user'], '-s', 'unit-test'])

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
        subprocess.run(['cloudscheduler', 'user', 'add', '-un', users[i], '-upw', gvar['user_secret'], *flags[i], '-s', 'unit-test'])

    #add clouds
    clouds_num = 0
    if 'clouds' in objects:
        clouds_num = 2
    else:
        clouds_num = 2
    credentials = gvar['cloud_credentials']
    clouds = []
    for i in range(1, clouds_num + 1):
        clouds.append(gvar['user'] + '-wic' + str(i))
    for i in range(0, clouds_num):
        subprocess.run(['cloudscheduler', 'cloud', 'add', '-ca', credentials['authurl'], '-cn', clouds[i], '-cpw', credentials['password'], '-cP', credentials['project'], '-cr', credentials['region'], '-cU', credentials['username'], '-ct', 'openstack', '-g', gvar['base_group'], '-s', 'unit-test'])
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
        while subprocess.run(['cloudscheduler', 'cloud', 'update', '-cn', clouds[0], '-vsg', 'default', '-s', 'unit-test']).returncode != 0:
            print("Error connecting to the cloud. This may happen several times. Retrying...")
            sleep(15)

    aliases_num = 0
    if 'aliases' in objects:
        aliases_num = 3
    else:
        aliases_num = 0
    aliases = []
    for i in range(1, aliases_num+1):
        aliases.append(gvar['user'] + '-wia' + str(i))
    if 'aliases' in objects:
        clouds = [gvar['user'] + '-wic1'] * 3
        clouds[1] += ',' + gvar['user'] + '-wic2'
    for i in range(0, aliases_num):
        subprocess.run(['cloudscheduler', 'alias', 'add', '-an', aliases[i], '-cn', clouds[i], '-g', gvar['base_group'], '-s', 'unit-test'])

    # add defaults
    defaults_num = 0
    if 'defaults' in objects:
        subprocess.run(['cloudscheduler', 'group', 'update', '-gn', gvar['user'] + '-wig1', '-un',  gvar['user'] + ',' + gvar['user'] + '-wiu2', '-s', 'unit-test'])
        subprocess.run(['cloudscheduler', 'group', 'update', '-gn', gvar['user'] + '-wig2', '-un', gvar['user'] + '-wiu1', '-s', 'unit-test'])
    if 'defaults' in objects:
        defaults_num = 2
    else:
        defaults_num = 0
    for i in range(1, defaults_num+1):
        name = gvar['user'] + '-wim' + str(i) + '.yaml'
        try:
            metadata = open('web_tests/' + name, 'x')
            metadata.write("sample_value_" + str(i) + ": sample_key_" + str(i))
            metadata.close()
        except FileExistsError:
            pass
        filename = os.path.abspath('web_tests/' + name)
        subprocess.run(['cloudscheduler', 'metadata', 'load', '-g', gvar['user'] + '-wig1', '-f', filename, '-mn', name, '-s', 'unit-test'])
    if 'defaults' in objects:
        subprocess.run(['cloudscheduler', 'cloud', 'add', '-ca', credentials['authurl'], '-cn', gvar['user'] + '-wic1', '-cpw', credentials['password'], '-cP', credentials['project'], '-cr', credentials['region'], '-cU', credentials['username'], '-ct', 'openstack', '-g', gvar['user'] + '-wig1', '-s', 'unit-test'])

    #add images
    if 'images' in objects:
        images_num = 2
    else:
        images_num = 0
    images = []
    for i in range(1, images_num+1):
        images.append(gvar['user'] + '-wii' + str(i) + '.hdd')
    for i in range(0, images_num):
        filename = os.path.abspath('web_tests/' + images[i])
        subprocess.run(['cloudscheduler', 'image', 'upload', '-ip', 'file://' + filename, '-df', 'raw', '-cl', gvar['user'] + '-wic1', '-g', gvar['base_group'], '-s', 'unit-test'])

    #add servers
    if 'servers' in objects:
        servers_num = 2
    else:
        servers_num = 0
    servers = []
    users = []
    for i in range(1, servers_num+1):
        servers.append(gvar['user'] + '-wis' + str(i))
        users.append(gvar['user'] + '-wiu' + str(i))
    for i in range(0, servers_num):
        subprocess.run(['cloudscheduler', 'defaults', 'set', '-s', servers[i], '-sa', gvar['address'], '-su', users[i], '-spw', gvar['user_secret']])

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

    delete_by_type(gvar, ['defaults', '-wis', '-s', 'server', []], 2, csv=False)
    delete_by_type(gvar, ['image', '-wii', '-in', 'name', ['-g', gvar['user'] + '-wig0', '-cn', gvar['user'] + '-wic1']], 3, csv=False)

    logfile = 'objects.txt'
    try:
        object_log = open(logfile, mode = 'x')
    except FileExistsError:
        object_log = open(logfile, mode = 'w') 
    
    subprocess.run(['cloudscheduler', 'alias', 'list', '-CSV', 'alias_name,clouds', '-g', gvar['base_group'], '-s', 'unit-test'], stdout=object_log)
    
    object_log.close()
    object_log = open(logfile, mode = 'r')

    aliases = []
    for line in object_log:
        object_list = line.strip()
        object_list = object_list.split(',')
        alias = object_list[0]
        object_list = object_list[1:]
        objects_to_remove = ''
        for item in object_list:
            objects_to_remove = objects_to_remove + ',' + item
        objects_to_remove = objects_to_remove.strip(',')
        aliases.append((alias, objects_to_remove))

    test_objects = []
    for i in range(0, 5):
        test_objects.append(gvar['user'] + '-wia' + str(i))
    for alias in aliases:
        if alias[0] in test_objects:
            subprocess.run(['cloudscheduler', 'alias', 'update', '-an', alias[0], '-cn', alias[1], '-co', 'delete', '-g', gvar['base_group'], '-s', 'unit-test'])
    object_log.close()

    delete_by_type(gvar, ['cloud', '-wic', '-cn', 'cloud_name', ['-g', gvar['user'] + '-wig1']], 1)
    delete_by_type(gvar, ['metadata', '-wim', '-mn', 'metadata_name', ['-g', gvar['user'] + '-wig1']], 9)
    delete_by_type(gvar, ['cloud', '-wic', '-cn', 'cloud_name', ['-g', gvar['base_group']]], 6)
    delete_by_type(gvar, ['user', '-wiu', '-un', 'username', []], 9)
    delete_by_type(gvar, ['group', '-wig', '-gn', 'group_name', []], 8)
    
    # This group must be deleted last - it is the containing group for clouds
    # and cleanup will fail if it is deleted earlier.
    subprocess.run(['cloudscheduler', 'group', 'delete', '-gn', gvar['base_group'], '-Y', '-s', 'unit-test'], stdout=subprocess.DEVNULL)

def delete_by_type(gvar, type_info, number, csv=True):
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

    flags = []
    flags.append('-CSV')
    flags.append(type_info[3])
    if type_info[0] != 'defaults':
        flags.append('-s')
        flags.append('unit-test')
    for flag in type_info[4]:
        flags.append(flag)
    
    subprocess.run(['cloudscheduler', type_info[0], 'list', *flags], stdout=object_log)
    
    object_log.close()
    object_log = open(logfile, mode = 'r')

    for line in object_log:
        object_list.append(line.strip())

    for i in range(1, number+1):
        add = ''
        if type_info[0] == 'metadata':
            add = '.yaml'
        if type_info[0] == 'image':
            add = '.hdd'
        objects.append(gvar['user'] + type_info[1] + str(i) + add)
    
    for object in objects:
        flags = type_info[4]
        if type_info[0] != 'defaults':
            flags.append('-s')
            flags.append('unit-test')
        if type_info[0] != 'image':
            flags.append('-Y')
        if object in object_list:
            subprocess.run(['cloudscheduler', type_info[0], 'delete', type_info[2], object,  *flags])

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
