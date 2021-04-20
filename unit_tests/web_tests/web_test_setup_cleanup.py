from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from cloudscheduler.unit_tests.unit_test_common import load_settings
from time import sleep
import subprocess
import signal
import web_tests.web_test_helpers as helpers
import os

# This module contains setup and cleanup functions for the unittest web tests.
# Setups and cleanups are done here to prevent issues of passing variables
# between test runners and to allow tests to be run individually with the
# unittest framework

def setup(cls, profile, objects, browser='firefox'):
    # Try/except block here ensures that cleanups will occur even on setup
    # error. If we update to python 3.8 or later, the unittest
    # addClassCleanup() is a better way of handling this.
    try:
        cls.gvar = setup_objects(objects, browser)
        if browser == 'firefox':
            cls.driver = webdriver.Firefox()
        elif browser == 'chromium':
            options = webdriver.ChromeOptions()
            # This line prevents Chromedriver hanging (see here: https://
            # stackoverflow.com/questions/51959986/how-to-solve-selenium-
            # chromedriver-timed-out-receiving-message-from-renderer-exc)
            options.add_argument('--disable-gpu')
            options.add_argument('--start-maximized')
            options.binary_location = '/usr/bin/chromium-browser'
            cls.driver = webdriver.Chrome(options=options)
        elif browser == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.binary_location = '/usr/bin/google-chrome'
            cls.driver = webdriver.Chrome(options=options)
        elif browser == 'opera':
            cls.driver = webdriver.Opera()
        helpers.get_homepage_login(cls.driver, cls.gvar['user'] + '-wiu' + str(profile), cls.gvar['user_secret'])
    except:
        print("Error in test setup")
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
        raise

def setup_objects(objects=[], browser='firefox'):
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
    cores = []
    for i in range(1, clouds_num + 1):
        clouds.append(gvar['user'] + '-wic' + str(i))
        if i == 1:
            cores.append('4')
        else:
            cores.append('0')
    for i in range(0, clouds_num):
        subprocess.run(['cloudscheduler', 'cloud', 'add', '-ca', credentials['authurl'], '-cn', clouds[i], '-cpw', credentials['password'], '-cP', credentials['project'], '-cr', credentials['region'], '-cU', credentials['username'], '-ct', 'openstack', '-vc', cores[i], '-g', gvar['base_group'], '-s', 'unit-test'])
    for i in range(0, clouds_num):
        helpers.wait_for_openstack_poller(clouds[i], ['-vsg', 'default', '-vf', 't1'], output=True)
    if 'clouds' in objects:
        for i in range(1, 3):
            name = gvar['user'] + '-wim' + str(i) + '.yaml'
            try:
                metadata = open('web_tests/misc_files/' + name, 'x')
                metadata.write("sample_value_" + str(i) + ": sample_key_" + str(i))
                metadata.close()
            except FileExistsError:
                pass
            filename = helpers.misc_file_full_path(name)
            subprocess.run(['cloudscheduler', 'cloud', 'metadata-load', '-cn', gvar['user'] + '-wic1', '-f', filename, '-mn', name])
        # This updates the security group setting, which requires a connection
        # to the cloud. The setup timing is unpredictable, so this loops it 
        # until the connection is established.
        #beaver_setup_keys(gvar, 1, browser)

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
            metadata = open('web_tests/misc_files/' + name, 'x')
            metadata.write("sample_value_" + str(i) + ": sample_key_" + str(i))
            metadata.close()
        except FileExistsError:
            pass
        filename = helpers.misc_file_full_path(name)
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
        filename = helpers.misc_file_full_path(images[i])
        subprocess.run(['cloudscheduler', 'image', 'upload', '-ip', 'file://' + filename, '-df', 'raw', '-cl', gvar['user'] + '-wic1', '-g', gvar['base_group'], '-s', 'unit-test'])
    if 'images' in objects:
        helpers.wait_for_openstack_poller(gvar['user'] + '-wic1', ['-vi', gvar['user'] + '-wii1.hdd'], output=True)

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

    #add keys
    if 'keys' in objects:
        keys_num = 2
        keys = []
        for i in range(1, keys_num+1):
            keys.append(gvar['user'] + '-wik' + str(i))
        for i in range(0, keys_num):
            subprocess.run(['openstack', 'keypair', 'create', '--private-key', '/home/centos/cloudscheduler/unit_tests/web_tests/misc_files/' + keys[i], keys[i]], stdout=subprocess.DEVNULL)
            print('keypair "' + keys[i] + '" successfully added.')
        keystring = gvar['user'] + '-wik1'
        helpers.wait_for_openstack_poller(gvar['user'] + '-wic1', ['-vk', keystring], output=True)

    if 'status' in objects:
        for i in range(1, 3):
            subprocess.run(['cloudscheduler', 'my', 'settings', '-sri', '60','-sfv', 'true', '-s', gvar['user'] + '-wis' + str(i)], stdout=subprocess.DEVNULL)
            helpers.wait_for_openstack_poller(gvar['user'] + '-wic' + str(i), ['-vi', 'centos7-image', '-vn', 'private'], output=True)

    if 'jobs' in objects:
        server_vm = helpers.server_url.split('//')[1]
        server_account = gvar['server_username'] + '@' + server_vm
        subprocess.run(['cloudscheduler', 'group', 'update', '-htcu', gvar['server_username'], '-gn', gvar['base_group']])
        subprocess.run(['ssh', server_account, '-p', str(gvar['server_port']), '-i', gvar['server_keypath'], 'condor_submit job.condor'])

    return gvar

def cleanup(cls, browser='firefox'):
    print("\nUnittest Teardown:")
    if hasattr(cls, 'driver') and cls.driver is not None:
        browser = cls.driver.name
        cls.driver.quit()
    cleanup_objects(browser)

def cleanup_objects(browser='firefox'):
    #subprocess.call(helpers.misc_file_full_path('testing-openrc.sh'))

    gvar = load_settings(web=True)
    gvar['base_group'] = gvar['user'] + '-wig0'

    logfile = 'web_tests/misc_files/objects.txt'
    #beaver_cleanup_keys(gvar, 4, 2, browser)

    os.environ['OS_AUTH_URL'] = gvar['cloud_credentials']['authurl']
    os.environ['OS_PROJECT_NAME'] = gvar['cloud_credentials']['project']
    os.environ['OS_USER_DOMAIN_NAME'] = 'Default'
    os.environ['OS_PROJECT_DOMAIN_ID'] = 'default'
    os.environ['OS_USERNAME'] = gvar['cloud_credentials']['username']
    os.environ['OS_PASSWORD'] = gvar['cloud_credentials']['password']
    os.environ['OS_REGION_NAME'] = gvar['cloud_credentials']['region']

    try:
        object_log = open(logfile, mode='x')
    except FileExistsError:
        object_log = open(logfile, mode='w')

    server_vm = helpers.server_url.split('//')[1]
    server_account = gvar['server_username'] + '@' + server_vm

    subprocess.run(['ssh', server_account, '-p', str(gvar['server_port']), '-i', gvar['server_keypath'], 'condor_q -nobatch -format "%d." ClusterId -format "%d " ProcId -format "%s\n" cmd'], stdout=object_log)

    object_log.close()
    object_log = open(logfile, mode='r')

    for line in object_log:
        job = line.split(' ')
        job[-1] = job[-1].strip()
        task = job[-1]
        task = task.split('/')
        if task[-1] == 'job.sh' and job[0] != 'Name':
            subprocess.run(['ssh', server_account, '-p', str(gvar['server_port']), '-i', gvar['server_keypath'], 'condor_rm ' + job[0]])

    object_log.close()

    try:
        object_log = open(logfile, mode='x')
    except FileExistsError:
        object_log = open(logfile, mode='w')

    subprocess.run(['nova', 'list', '--name', gvar['base_group'] + '--' + gvar['user'] + '-wic.*'], stdout=object_log)

    object_log.close()
    object_log = open(logfile, mode='r')

    for line in object_log:
        names = line.split('|')
        try:
            name = names[2].strip()
        except IndexError:
            continue
        if not name == '' and not name[0] == '-' and not name == 'Name':
            subprocess.run(['nova', 'delete', name])

    object_log.close()
   
    try:
        object_log = open(logfile, mode = 'x')
    except FileExistsError:
        object_log = open(logfile, mode = 'w')
 
    subprocess.run(['openstack', 'keypair', 'list', '--format', 'csv'], stdout=object_log)

    object_log.close()
    object_log = open(logfile, mode='r')

    names = []
    for line in object_log:
        row = line.split(',')
        names.append(row[0].strip('"'))

    for i in range(1, 5):
        remove = gvar['user'] + '-wik' + str(i)
        if remove in names:
            subprocess.run(['openstack', 'keypair', 'delete', remove])
            print('keypair "' + remove + '" successfully deleted.')

    object_log.close()

    delete_by_type(gvar, ['defaults', '-wis', '-s', 'server', []], 2)
    for i in range(2, 1, -1):
        delete_by_type(gvar, ['image', '-wii', '-in', 'name', ['-g', gvar['user'] + '-wig0', '-cn', gvar['user'] + '-wic' + str(i)]], 3, others=['test-os-image-raw'])

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

def delete_by_type(gvar, type_info, number, others=[]):
    # type_info is a list of strings (and one list of strings)
    # The first string is the name of the object to be deleted (ex 'user')
    # The second string is the suffix used to generate the names of the test objects (ex '-wiu')
    # The third string is the flag used to indicate this identifier (ex '-un')
    # The fourth string is the column name for the list command (ex 'username')
    # The fifth item is a list of strings that provide extra necessary arguments (this will often be an empty list)

    objects = []
    object_log = None
    object_list = []
    logfile = 'web_tests/misc_files/objects.txt'

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

    add = ''
    if type_info[0] == 'metadata':
        add = '.yaml'
    if type_info[0] == 'image':
        add = '.hdd'

    for name in others:
        objects.append(name + add)

    for i in range(1, number+1):
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
