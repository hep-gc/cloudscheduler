from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import exists
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select
from csv2 import config
from lib.schema import *

import time

'''
dev code
= db_session.query(Cloud).filter(Cloud.cloud_type=="openstack")
db_session.merge(new_flav)
db_session.commit()
'''


def db_open():
    """
    Provide a database connection and optionally mapping.
    """

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.automap import automap_base

    db_engine = create_engine(
        "mysql://%s:%s@%s:%s/%s" % (
            config.db_user,
            config.db_password,
            config.db_host,
            str(config.db_port),
            config.db_name
            )
        )

    db_session = Session(db_engine)
    db_connection = db_engine.connect()
    db_map = automap_base()
    db_map.prepare(db_engine, reflect=True)

    return db_engine,db_session,db_connection,db_map


def get_limits(group_name=None):
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Limit = Base.classes.cloud_limits
    if group_name is None:
        limit_list = db_session.query(Limit)
    else:
        limit_list = db_session.query(Limit).filter(Limit.group_name==group_name)
    return limit_list

#
# This function accepts a group name and cloud name and returns all virtual machines related to that group and cloud
# if no group and cloud name is given it returns the entire list of vms
#
def get_vms(group_name=None, cloud_name=None):
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    VM = Base.classes.csv2_vms
    if group_name is None:
        vm_list = db_session.query(VM)
    else:
        if cloud_name is None:
            vm_list = db_session.query(VM).filter(VM.group_name==group_name)
        else:
            vm_list = db_session.query(VM).filter(VM.group_name==group_name, VM.cloud_name==cloud_name)
    return vm_list

def get_flavors(filter=None):
    Base = declarative_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Flavors = Base.classes.cloud_flavors
    flavor_list = db_session.query(Flavors)
    return flavor_list

def get_images(filter=None):
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Images = Base.classes.cloud_images
    image_list = db_session.query(Images)
    return image_list

def get_networks(filter=None):
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Networks = Base.classes.cloud_networks
    network_list = db_session.query(Networks)
    return network_list


def get_groups(filter=None):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    conn = engine.connect()
    s = select([view_group_with_yaml])
    return conn.execute(s)


def get_group_resources(group_name):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    conn = engine.connect()
    s = select([view_group_resources]).where(view_group_resources.c.group_name == group_name)
    return conn.execute(s)


def get_counts(group_name=None):
    metadata = MetaData()    
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    conn = engine.connect()
    s = select([view_group_list]).where(view_group_list.c.group_name == group_name)
    return conn.execute(s)


#def get_cloud_status(group_name):
#    metadata = MetaData()    
#    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
#    conn = engine.connect()
#    s = select([view_cloud_status]).where(view_cloud_status.c.group_name == group_name)
#    return conn.execute(s)

def get_cloud_status(group_name):
    db_engine,db_session,db_connection,db_map = db_open()
    s = select([view_cloud_status]).where(view_cloud_status.c.group_name == group_name)
    return db_connection.execute(s)

#
# This function accepts a user name and retrieves & returns all groups associated with the user
#
def get_user_groups(user):
    user_group_list = []
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    user_groups = Base.classes.csv2_user_groups
    user_group_rows = db_session.query(user_groups).filter(user_groups.username==user)
    if user_group_rows is not None:
        for row in user_group_rows:
            user_group_list.append(row.group_name)
    return user_group_list

#
# This function accepts a group name and returns all jobs related to that group
# if no group name is given it returns the entire list of jobs
#
def get_condor_jobs(group_name=None):
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Jobs = Base.classes.condor_jobs
    if group_name is None:
        job_list = db_session.query(Jobs)
    else:
        job_list = db_session.query(Jobs).filter(Jobs.group_name==group_name)
    return job_list


def get_condor_machines(filter=None):
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Machines = Base.classes.condor_machines
    if group_name is None:
        machine_list = db_session.query(Machines)
    else:
        # machines do not currently have group_name in their classad (and therefore not in database)
        # there are several possible solutions
        #   1. find a way to inject it on boot
        #   2. have the cscollector update the classad by cross referencing the job_id
        #   3. do not add group_name to machine classads and instead cross reference job_ids every time to get machine list
        #machine_list = db_session.query(Machines).filter(Machines.group_name=group_name)
        machine_list = []
        
    return machine_list


# add new group resources
def put_group_resources(query_dict):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)

    metadata = MetaData(bind=engine)

    table = Table('csv2_group_resources', metadata, autoload=True)
    db_session = Session(engine)

    columns = table.c

    action = query_dict['action']

    # Only accept data if column exisits in the table.
    query_filtered = {}
    for key in query_dict:
       if key == 'action' or key == 'csrfmiddlewaretoken':
            continue

       if key in columns:
            query_filtered.update({key:query_dict[key]})
       else:
            return [1, 'cloud modify: request to update bad key "%s".' % key]

    if action =="add":
        if(db_session.query(exists().where(table.c.cloud_name==query_dict['cloud_name'] and table.c.group_name==query_dict['group_name'])).scalar()):
            return [1, 'cloud modify: request to add existing cloud']
        else:
            ins = table.insert().values(query_filtered)
            print(">>>>>>>>>>>>>>>>>>", ins)

    elif action =="modify":
        #ins = table.update().where(table.c.cloud_name==query_dict['cloud_name_orig'] and table.c.group_name==query_dict['group_name']).values(query_filtered)
        ins = table.update().where(table.c.cloud_name==query_dict['cloud_name'] and table.c.group_name==query_dict['group_name']).values(query_filtered)

    elif action =="delete":
        ins = table.delete(table.c.cloud_name==query_dict['cloud_name'] and table.c.group_name==query_dict['group_name'])

    else:
        return 0

    conn = engine.connect()
    conn.execute(ins)

    return 1


# add new groups
def put_groups(query_dict):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)

    metadata = MetaData(bind=engine)

    table = Table('csv2_groups', metadata, autoload=True)
    db_session = Session(engine)

    columns = table.c

    action = query_dict['action']

    # Only accept data if column exisits in the table.
    query_filtered = {}
    for key in query_dict:
       if key in columns:
            query_filtered.update({key:query_dict[key]})

    if action =="add":
        if(db_session.query(exists().where(table.c.group_name==query_dict['group_name'])).scalar()):
            return 0
        else:
            #if group_name in user_groups:

            ins = table.insert().values(query_filtered)

    elif action =="modify":
        #ins = table.update().where(table.c.cloud_name==query_dict['cloud_name_orig'] and table.c.group_name==query_dict['group_name']).values(query_filtered)
        ins = table.update().where(table.c.group_name==query_dict['group_name']).values(query_filtered)

    elif action =="delete":
        ins = table.delete(table.c.group_name==query_dict['group_name'])

    else:
        return 0

    conn = engine.connect()
    conn.execute(ins)

    return 1
