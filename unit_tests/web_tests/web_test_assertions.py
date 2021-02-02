import unittest
import subprocess

# This module contains a set of assertions on the cloudscheduler database, for
# use in the web tests. Note that these methods use the cloudscheduler list
# command, and therefore are much slower than Selenium assertions. These should # be used only once per test.

logfile = 'assert_objects.txt'

def assertAdded(type, name, group=None):
    list_by_type(type, group)
    object_file = open(logfile, 'r')
    for line in object_file:
        if line.strip()==name:
             object_file.close()
             return
    object_file.close()
    raise AssertionError

def assertDeleted(type, name, group=None):
    list_by_type(type, group)
    object_file = open(logfile, 'r')
    for line in object_file:
        if line.strip()==name:
             object_file.close()
             raise AssertionError
    object_file.close()

assertNotAdded = assertDeleted

def assertHasAttribute(type, name, attribute, attribute_name, group=None):
    # This method should only be used on objects that are known to be created -
    # ie the test should not be creating them. If the test is creating the
    # object, use assertAddedWithAttribute
    list_attribute_by_name(type, name, attribute, group)
    object_file = open(logfile, 'r')
    record = ""
    for line in object_file:
        record += line
    record = record.split(',')
    record[-1] = record[-1].strip()
    if attribute_name not in record:
        object_file.close()
        raise AssertionError
    object_file.close()

def assertAddedWithAttribute(type, name, attribute, attribute_name, group=None):
    list_attribute_by_name(type, name, attribute, group)
    object_file = open(logfile, 'r')
    record = ""
    for line in object_file:
        record += line
    if record.strip() == "":
        object_file.close()
        raise AssertionError
    record = record.split(',')
    record[-1] = record[-1].strip()
    if attribute_name not in record:
        object_file.close()
        raise AssertionError()
    object_file.close()

def assertHasNotAttribute(type, name, attribute, attribute_name, group=None):
    # This method should only be used on objects that are known to be created -
    # ie the test should not be creating them. If the test is creating the
    # object, use assertAddedWithoutAttribute
    list_attribute_by_name(type, name, attribute, group)
    object_file = open(logfile, 'r')
    record = ""
    for line in object_file:
        record += line
    record = record.split(',')
    record[-1] = record[-1].strip()
    if attribute_name in record:
        object_file.close()
        raise AssertionError
    object_file.close()

def assertAddedWithoutAttribute(type, name, attribute, attribute_name, group=None):
    list_attribute_by_name(type, name, attribute, group)
    object_file = open(logfile, 'r')
    record = ""
    for line in object_file:
        record += line
    if record.strip() == "":
        object_file.close()
        raise AssertionError
    record = record.split(',')
    record[-1] = record[-1].strip()
    if attribute_name in record:
        object_file.close()
        raise AssertionError()
    object_file.close()

def list_by_name(type, name, group=None):
    # This function is unused. It currently is not working because the empty 
    # '-CSV' flag doesn't work properly with subprocess.run
    object_file = None
    try:
        object_file = open(logfile, 'x')
    except FileExistsError:
        object_file = open(logfile, 'w')
    object_names = names()
    object = object_names[type]
    flags = []
    if group:
        flags = ['-g', group]
    subprocess.run(['cloudscheduler', object['name'], 'list', object['flag'], name, '-CSV', '""', *flags], stdout=object_file)
    object_file.close()

def list_attribute_by_name(type, name, attribute, group=None):
    object_file = None
    try:
        object_file = open(logfile, 'x')
    except FileExistsError:
        object_file = open(logfile, 'w')
    object_names = names()
    object = object_names[type]
    flags = []
    if group:
        flags = ['-g', group]
    subprocess.run(['cloudscheduler', object['name'], 'list', object['flag'], name, '-CSV', object['column_name'] + ',' + attribute, *flags], stdout=object_file)
    object_file.close()

def list_by_type(type, group=None):
    object_file = None
    try:
        object_file = open(logfile, 'x')
    except FileExistsError:
        object_file = open(logfile, 'w')
    object_names = names()
    object = object_names[type]
    flags = []
    if group:
        flags = ['-g', group]
    subprocess.run(['cloudscheduler', object['name'], 'list', '-CSV', object['column_name'], *flags], stdout=object_file)
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

    user = {
        'name': 'user',
        'flag': '-un',
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
        'user': user,
        'vm': vm
    }

    return names
