from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import exists
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select
from csv2 import config
from lib.schema import *


'''
dev code
= db_session.query(Cloud).filter(Cloud.cloud_type=="openstack")
db_session.merge(new_flav)
db_session.commit()
'''


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
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Groups = Base.classes.csv2_groups
    group_list = db_session.query(Groups)
    return group_list

# may be best to query the view instead of the resources table
def get_group_resources(group_name):
    metadata = MetaData()    
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    conn = engine.connect()
    s = select([view_group_resources]).where(view_group_resources.c.group_name == group_name)
    group_resources_list = conn.execute(s)
    return group_resources_list


# may be best to query the view instead of the resources table
def get_counts(group_name=None):
    metadata = MetaData()    
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    conn = engine.connect()
    s = select([view_group_list]).where(view_group_list.c.group_name == group_name)
    count_list = conn.execute(s)
    return count_list

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
def put_group_resources(action, group, cloud, url, uname, pword):
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)

    metadata = MetaData(bind=engine)

    table = Table('csv2_group_resources', metadata, autoload=True)
    db_session = Session(engine)

    if action=="add":

        if(db_session.query(exists().where(table.c.cloud_name==cloud)).scalar()):
            return 0

        else:
            ins = table.insert().values(
            group_name="Testing",
            cloud_name=cloud,
            authurl=url,
            project="default",
            username=uname,
            password=pword,
            keyname="",
            cacertificate="",
            region="",
            userdomainname="",
            projectdomainname="",
            extrayaml="",  
            cloud_type="",
            )

    elif action=="modify":
        ins = table.update().where(table.c.cloud_name==cloud).values(
            group_name="Testing",
            cloud_name=cloud,
            authurl=url,
            project="default",
            username=uname,
            password=pword,
            keyname="",
            cacertificate="",
            region="",
            userdomainname="",
            projectdomainname="",
            extrayaml="",  
            cloud_type="",
            )
    elif action=="delete":
        ins = table.delete(table.c.cloud_name==cloud)
    else:
        return 0

    conn = engine.connect()
    conn.execute(ins)

    return 1
