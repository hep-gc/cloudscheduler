from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import config


'''
dev code
= db_session.query(Cloud).filter(Cloud.cloud_type=="openstack")
db_session.merge(new_flav)
db_session.commit()
'''


def get_quotas(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Quota = Base.classes.cloud_quotas
    quota_list = db_session.query(Quota)
    return quota_list

def get_vms(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    VM = Base.classes.cloud_vm
    vm_list = db_session.query(VM)
    return vm_list

def get_flavors(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Flavors = Base.classes.cloud_flavors
    flavor_list = db_session.query(Flavors)
    return flavor_list

def get_images(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Images = Base.classes.cloud_images
    image_list = db_session.query(Images)
    return image_list

def get_networks(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Networks = Base.classes.cloud_networks
    network_list = db_session.query(Networks)
    return network_list

def get_groups(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Groups = Base.classes.csv2_groups
    group_list = db_session.query(Groups)
    return group_list

# may be best to query the view instead of the resources table
def get_group_resources(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    GroupResources = Base.classes.csv2_group_resources
    group_resources_list = db_session.query(GroupResources)
    return group_resources_list