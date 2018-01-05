from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from csv2 import config


'''
dev code
= db_session.query(Cloud).filter(Cloud.cloud_type=="openstack")
db_session.merge(new_flav)
db_session.commit()
'''


def get_quotas(group_name=None):
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    Quota = Base.classes.cloud_quotas
    if group_name is None:
        quota_list = db_session.query(Quota)
    else:
        quota_list = db_session.query(Quota).filter(Quota.group_name==group_name)
    return quota_list

#
# This function accepts a group name and returns all virtual machines related to that group
# if no group name is given it returns the entire list of vms
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
    Base = automap_base()
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
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    GroupResources = Base.classes.csv2_group_resources
    group_resources_list = db_session.query(GroupResources).filter(GroupResources.group_name==group_name)
    return group_resources_list

#
# This function accepts a user name and retrieves & returns all groups associated with the user
#
def get_user_groups(user):
    group_list = []
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    db_session = Session(engine)
    User_groups = Base.classes.csv2_user_groups
    user_group_rows = db_session.query(User_groups).filter(User_groups.username==user)
    if user_group_rows is not None:
        for row in user_group_rows:
            group_list.append(row.group_name)
    return group_list

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
