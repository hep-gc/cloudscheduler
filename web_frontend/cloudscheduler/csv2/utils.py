from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import config


def get_quotas(filter=None):
    return None

def get_vms(filter=None):
    return None

def get_flavors(filter=None):
    return None

def get_images(filter=None):
    return None

def get_networks(filter=None):
    return None

def get_groups(filter=None):
    return None

# may be best to query the view instead of the resources table
def get_group_resources(filter=None):
    return None