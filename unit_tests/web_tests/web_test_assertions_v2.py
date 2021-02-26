import unittest
import subprocess
from time import sleep

logfile = 'assert_v2_objects.txt'
sleep_time = 2

def assertExists(type, name, group=None, metadata_cloud=None, defaults=False, settings=False, server='unit-test', is_retry=False):
    object_names = names()
    columns = object_names[type]['column_name']

    if metadata_cloud:
        list_objects('cloud', 'metadata_names', metadata_cloud, group, None, defaults, settings, server)
    elif settings:
        list_objects('my', columns, None, group, None, defaults, settings, server)
    else:
        list_objects(type, columns, None, group, None, defaults, settings, server)

    object_file = open(logfile, 'r')
    record = []
    for line in object_file:
        list = line.strip()
        list = list.split(',')
        record.append(*list) 

    for object_name in record:
        if object_name == name:
            object_file.close()
            return

    object_file.close()
    if is_retry:
        raise AssertionError()
    else:
        sleep(sleep_time)
        assertExists(type, name, group, metadata_cloud, defaults, settings, server, True)

def assertNotExists(type, name, group=None, metadata_cloud=None, defaults=False, settings=False, server='unit-test', is_retry=False):
    object_names = names()
    columns = object_names[type]['column_name']

    if metadata_cloud:
        list_objects('cloud', 'metadata_names', metadata_cloud, group, None, defaults, settings, server)
    elif settings:
        list_objects('my', columns, None, group, None, defaults, settings, server)
    else:
        list_objects(type, columns, None, group, None, defaults, settings, server)

    object_file = open(logfile, 'r')
    record = []
    for line in object_file:
        list = line.strip()
        list = list.split(',')
        record.append(*list) 

    for object_name in record:
        if object_name == name:
            object_file.close()
            if is_retry:
                raise AssertionError()
            else:
                sleep(sleep_time)
                assertNotExists(type, name, group, metadata_cloud, defaults, settings, server, True)

    object_file.close()

def assertHasAttribute(type, name, attribute, attribute_name, group=None, err=None, metadata_cloud=None, defaults=False, name_field=True, settings=False, server='unit-test', is_retry=False):
    object_names = names()
    columns = object_names[type]['column_name']
    if attribute:
        columns += ','
        columns += attribute

    if metadata_cloud:
        list_objects('cloud', columns, metadata_cloud, group, name, defaults, settings, server)
    elif settings:
        list_objects('my', columns, None, group, None, defaults, settings, server)
    elif defaults or not name_field:
        list_objects(type, columns, None, group, None, defaults, settings, server)
    else:
        list_objects(type, columns, name, group, None, defaults, settings, server)

    object_file = open(logfile, 'r')
    record = ''

    if name_field:
        for line in object_file:
            record += line
        if record.strip() == '':
            object_file.close()
            if is_retry:
                raise AssertionError()
            else:
                sleep(sleep_time)
                assertHasAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, defaults, name_field, settings, server, True)

        record = record.split(',')
        record[-1] = record[-1].strip()
        attribute_test = attribute_name.split(',')
        attribute_test[-1] = attribute_test[-1].strip()

        if err:
            try:
                int(attribute_name)
            except TypeError:
                raise AssertionError()
            for i in range(int(attribute_name)-err, int(attribute_name)+err):
                if str(i) in record:
                    object_file.close()
                    return

            object_file.close()
            if is_retry:
                raise AssertionError()
            else:
                sleep(sleep_time)
                assertHasAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, defaults, name_field, settings, server, True)

        else:
            for line in attribute_test:
                if line not in record:
                    object_file.close()
                    if is_retry:
                        raise AssertionError()
                    else:
                        sleep(sleep_time)
                        assertHasAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, defaults, name_field, settings, server, True)
            object_file.close()

    else:
        for line in object_file:
            list = line.split(',')
            list[-1] = list[-1].strip()
            if list[0] == name:
                for item in list[1:]:
                    if item == attribute_name:
                        object_file.close()
                        return
            object_file.close()
            if is_retry:
                raise AssertionError()
            else:
                sleep(sleep_time)
                assertHasAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, defaults, name_field, settings, server, True)

def assertHasNotAttribute(type, name, attribute, attribute_name, group=None, err=None, metadata_cloud=None, defaults=False, name_field=True, settings=False, server= 'unit-test', is_retry=False):
    object_names = names()
    columns = object_names[type]['column_name']
    if attribute:
        columns += ','
        columns += attribute

    if metadata_cloud:
        list_objects('cloud', columns, metadata_cloud, group, name, defaults, settings, server)
    elif settings:
        list_objects('my', columns, None, group, None, defaults, settings, server)
    elif defaults or not name_field:
        list_objects(type, columns, None, group, None, defaults, settings, server)
    else:
        list_objects(type, columns, name, group, None, defaults, settings, server)

    object_file = open(logfile, 'r')
    record = ''

    if name_field:
        for line in object_file:
            record += line
        if record.strip() == '':
            object_file.close()
            if is_retry:
                raise AssertionError()
            else:
                sleep(sleep_time)
                assertHasNotAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, defaults, name_field, settings, server, True)

        record = record.split(',')
        record[-1] = record[-1].strip()
        attribute_test = attribute_name.split(',')
        attribute_test[-1] = attribute_test[-1].strip()

        if err:
            try:
                int(attribute_name)
            except TypeError:
                raise AssertionError()
            for i in range(int(attribute_name)-err, int(attribute_name)+err):
                if str(i) in record:
                    object_file.close()
                    if is_retry:
                        raise AssertionError()
                    else:
                        sleep(sleep_time)
                        assertHasNotAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, defaults, name_field, settings, server, True)

            object_file.close()
            return

        else:
            for line in attribute_test:
                if line in record:
                    object_file.close()
                    if is_retry:
                        raise AssertionError()
                    else:
                        sleep(sleep_time)
                        assertHasNotAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, defaults, name_field, settings, server, True)
            object_file.close()

    else:
        for line in object_file:
            list = line.split(',')
            list[-1] = list[-1].strip()
            if list[0] == name:
                for item in list[1:]:
                    if item == attribute_name:
                        object_file.close()
                        if is_retry:
                            raise AssertionError()
                        else:
                            sleep(sleep_time)
                            assertHasNotAttribute(type, name, attribute, attribute_name, group, err, metadata_cloud, name_field, settings, server, True)
        object_file.close()

def list_objects(type, columns, name, group, metadata, defaults, settings, server):
    object_file = None
    try:
        object_file = open(logfile, 'x')
    except FileExistsError:
        object_file = open(logfile, 'w')

    command = 'list'
    if metadata:
        command = 'metadata-list'
    if defaults:
        command = 'defaults'
    if settings:
        command = 'settings'
        
    object_names = names()

    flags = []
    if group:
        flags.append('-g')
        flags.append(group)
    if name:
        flags.append(object_names[type]['flag'])
        flags.append(name)
    if metadata:
        flags.append('-mn')
        flags.append(metadata)
    flags.append('-s')
    flags.append(server)

    subprocess.run(['cloudscheduler', type, command, '-CSV', columns, *flags], stdout=object_file)

    object_file.close()

def names():
    alias = {
        'name': 'alias',
        'flag': None,
        'column_name': 'alias_name'
    }

    cloud = {
        'name': 'cloud',
        'flag': '-cn',
        'column_name': 'cloud_name'
    }

    defaults = {
        'name': 'defaults',
        'flag': '-s',
        'column_name': 'server'
    }

    group = {
        'name': 'group',
        'flag': '-gn',
        'column_name': 'group_name'
    }

    job = {
        'name': 'job',
        'flag': '-jI',
        'column_name': 'global_job_id'
    }

    metadata = {
        'name': 'metadata',
        'flag': '-mn',
        'column_name': 'metadata_name'
    }

    my = {
        'name': 'my',
        'flag': '-un',
        'column_name': 'username'
    }

    settings = {
        'name': 'settings',
        'flag': '-un',
        'column_name': 'username'
    }

    user = {
        'name': 'user',
        'flag': None,
        'column_name': 'username'
    }

    vm = {
        'name': 'vm',
        'flag': None,
        'column_name': 'vmid'
    }

    names = {
        'alias': alias,
        'cloud': cloud,
        'defaults': defaults,
        'group': group,
        'job': job,
        'metadata': metadata,
        'my': my,
        'settings': settings,
        'user': user,
        'vm': vm
    }

    return names
