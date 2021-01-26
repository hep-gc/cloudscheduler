import unittest
import subprocess

def assertAdded(type, name):
    list_by_type(type)
    object_file = open('assert_objects.txt, 'r')
    for line in object_file:
        if line==name:
             object_file.close()
             return
    object_file.close()
    raise AssertionError

def assertDeleted(type, name):
    list_by_type(type)
    object_file = open('assert_objects.txt', 'r')
    for line in object_file:
        if line==name:
             object_file.close()
             raise AssertionError
    object_file.close()

def assertHasAttribute(type, name, attribute_name):
    list_by_name(type, name)
    object_file = open('assert_objects.txt', 'r')
    record = ""
    for line in object_file:
        record += line
    record = record.split(',')
    if attribute_name not in record:
        object_file.close()
        raise AssertionError
    object_file.close()

def list_by_name(type, name):
    object_file = None
    try:
        object_file = open('assert_objects.txt', 'x')
    except FileExistsException:
        object_file = open('assert_objects.txt', 'w')
    object_names = names()
    object = object_names[type]
    subprocess.run(['cloudscheduler', object['name'], 'list', object['flag'], name, '-CSV', '""'], stdout=object_file)
    object_file.close()

def list_by_type(object):
    object_file = None
    try:
        object_file = open('assert_objects.txt', 'x')
    except FileExistsException:
        object_file = open('assert_objects.txt', 'w')
    object_names = names()
    object = object_names[type]
    subprocess.run(['cloudscheduler', object['name'], 'list', '-CSV', object['column_name'], stdout=object_file)
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
