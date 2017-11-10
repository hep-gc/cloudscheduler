from multiprocessing import Process
import time
import json
import logging
import config

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client
from neutronclient.v2_0 import client as neuclient

#NEED TO ADD CACERT TO CONFIG FOR MAKING AUTH CONNECTIONS


# The purpose of this file is to get some information from the various registered
# openstack clouds and place it in a database for use by cloudscheduler
#
# Target data sets (should all be available from novaclient):
#       Flavor information
#       Quota Information
#       Image Information
#       Network Information

## UTILITY FUNCTIONS
#

def get_openstack_session(auth_url, username, password, project, user_domain="Default", project_domain="Default"):
    authsplit = auth_url.split('/')
    version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    if version == 2:
        try:
            auth = v2.Password(auth_url=auth_url, username=username, password=password, tenant_name=project)
            sess = session.Session(auth=auth, verify=config.cacert)
        except Exception as e:
            print("Problem importing keystone modules, and getting session: %s" % e)
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(auth_url=auth_url, username=username, password=password, project_name=project, user_domain_name=user_domain, project_domain=project_domain_name)
            sess = session.Session(auth=auth, verify=config.cacert)
        except Exception as e:
            print("Problem importing keystone modules, and getting session: %s" % e)
        return sess

def get_nova_client(session):
    nova = client.Client("2", session=session)
    return nova

def get_neutron_client(session):
    neutron = neuclient.Client(session=session)
    return neutron

def get_flavor_data(nova):
    return  nova.flavors.list()

def get_quota_data(nova, project):
    #this command gets the default quotas for a project, unsure if this is user specific
    quotas = nova.quotas.defaults(project)
    return quotas

def get_image_data(nova):
    return nova.glance.list()

def get_network_data(neutron):
    return neutron.list_networks()

## SubProccess Functions
#
def metadata_poller():
    # The logic here will depend on how the cloud configuration data is stored in the database
    # if we can query by cloud type it will be easy to get the openstack ones and itterate over them

    # get cloud configuration data (uname/pw/auth_url/domains)
    # prepare database session
    # init neutron and nova clients
    # get metadata
    # insert into rows using **kwargs
    # merge data
    # commit session
    # sleep cycle
    return None



## MAIN 
#
if __name__ == '__main__':

    logging.basicConfig(filename=config.collector_log_file,level=logging.DEBUG)
    processes = []

    p_metadata_poller = Process(target=metadata_poller)
    processes.append(p_metadata_poller)

   

    # Wait for keyboard input to exit
    try:
        for process in processes:
            process.start()
        while(True):
            for process in processes:
                if not process.is_alive():
                    logging.error("%s process died!" % process.name)
                    logging.error("Restarting %s process...")
                    process.start()
                time.sleep(1)
            time.sleep(10)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s" % process.name)


