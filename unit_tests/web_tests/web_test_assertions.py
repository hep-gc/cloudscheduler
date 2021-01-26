import unittest
import subprocess

def assertAdded():
    pass

def assertDeleted():
    pass

def list(name, options):
    pass

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
