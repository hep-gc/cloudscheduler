import multiprocessing
from multiprocessing import Process
import time
import socket
import logging
import config
import datetime
from dateutil import tz, parser

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient
from neutronclient.v2_0 import client as neuclient
from cinderclient import client as cinclient

from attribute_mapper.attribute_mapper import map_attributes


# The purpose of this file is to get some information from the various registered
# openstack clouds and place it in a database for use by cloudscheduler
#
# Target data sets (should all be available from novaclient):
#       Flavor information
#       Quota Information
#       Image Information
#       Network Information
#
# This file also polls the openstack clouds for live VM information and inserts it into the database

## UTILITY FUNCTIONS
#

def get_openstack_session(auth_url, username, password, project, user_domain="Default", project_domain_name="Default"):
    authsplit = auth_url.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad openstack URL: %s, could not determine version, aborting session", auth_url)
        return False
    if version == 2:
        try:
            auth = v2.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                tenant_name=project)
            sess = session.Session(auth=auth, verify=config.cacert)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s:%s" % (auth_url, exc))
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
            return False
        return sess
    elif version == 3:
        #connect using keystone v3
        try:
            auth = v3.Password(
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project,
                user_domain_name=user_domain,
                project_domain_name=project_domain_name)
            sess = session.Session(auth=auth, verify=config.cacert)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess

def get_nova_client(session):
    nova = novaclient.Client("2", session=session)
    return nova

def get_neutron_client(session):
    neutron = neuclient.Client(session=session)
    return neutron

def get_cinder_client(session):
    cinder = cinclient.Client("2", session=session)
    return cinder



def get_flavor_data(nova):
    try:
        return  nova.flavors.list()
    except Exception as exc:
        logging.error("Unable to retireve Flavor data")
        logging.error(exc)
        return False

# Returns a tuple of quotas (novaquotas, cinderquotas)
def get_quota_data(nova, cinder, project):
    # this command gets the default quotas for a project
    nova_quotas = nova.quotas.defaults(project)
    # it should be possible to get quotas at the project-user level but access must be enabled
    # on the openstack side the command for this is nova.quotas.get(tenant_id, user_id)

    # weneed to also get the storage quotas for a project since they are not available from nova
    cinder_quotas = cinder.quotas.defaults(project)
    return nova_quotas, cinder_quotas

# Returns the limits of the openstack project associated with the passed in nova object
def get_limit_data(nova):
    try:
        limits = {}
        limit_generator = nova.limits.get().absolute
        for limit in limit_generator:
            limits[limit.name] = [limit.value]
        return limits
    except Exception as exc:
        logging.error("Unable to retrieve Limit data")
        logging.error(exc)
        return False


def get_image_data(nova):
    try:
        return nova.glance.list()
    except Exception as exc:
        logging.error("Unable to retrieve Image data")
        logging.error(exc)
        return False


def get_network_data(neutron):
    try:
        return neutron.list_networks()['networks']
    except Exception as exc:
        logging.error("Unable to retrieve Network data")
        logging.error(exc)
        return False

def get_vm_list(nova):
    try:
        return nova.servers.list()
    except Exception as exc:
        logging.error("Unable to retrieve VM list")
        logging.error(exc)
        return False

def terminate_vm(session, vm):
    nova = get_nova_client(session)
    try:
        nova.servers.delete(vm.vmid)
        return True
    except Exception as exc:
        logging.error("Unable to terminate vm: %s", vm.hostname)
        logging.error(exc)
        return False


## PROCESS FUNCTIONS
#

# This process thread will be responsible for polling the list of VMs from each registered
# openstack cloud and reporting their state back to the database for use by cloud scheduler
#
def vm_poller():
    multiprocessing.current_process().name = "VM Poller"
    while True:
        try:
            logging.debug("Begining poll cycle")
            Base = automap_base()
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
                "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            db_session = Session(engine)
            Vm = Base.classes.csv2_vms
            Cloud = Base.classes.csv2_group_resources
            Poll_Times = Base.classes.csv2_poll_times
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")

            # Itterate over cloud list
            poll_time =  int(time.time())
            for cloud in cloud_list:
                logging.info("Polling VMs from group:cloud -  %s:%s" % (cloud.group_name, cloud.cloud_name))
                authsplit = cloud.authurl.split('/')
                try:
                    version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
                except ValueError:
                    logging.error("Bad openstack URL, could not determine version, skipping %s", cloud.authurl)
                    continue
                if version == 2:
                    session = get_openstack_session(
                        auth_url=cloud.authurl,
                        username=cloud.username,
                        password=cloud.password,
                        project=cloud.project)
                else:
                    session = get_openstack_session(
                        auth_url=cloud.authurl,
                        username=cloud.username,
                        password=cloud.password,
                        project=cloud.project,
                        user_domain=cloud.user_domain_name,
                        project_domain_name=cloud.project_domain_name)

                if session is False:
                    logging.error("Unable to setup session, skipping %s", cloud.cloud_name)
                    if version == 2:
                        logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
                    else:
                        logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
                    continue
                # setup nova object
                nova = get_nova_client(session)

                # get server list
                vm_list = get_vm_list(nova)
                if vm_list is False:
                    continue
                for vm in vm_list:
                    vm_dict = {
                        'group_name': cloud.group_name,
                        'cloud_name': cloud.cloud_name,
                        'auth_url': cloud.authurl,
                        'project': cloud.project,
                        'hostname': vm.name,
                        'vmid': vm.id,
                        'status': vm.status,
                        'flavor_id': vm.flavor["id"],
                        'task': vm.__dict__.get("OS-EXT-STS:task_state"),
                        'power_state': vm.__dict__.get("OS-EXT-STS:power_state"),
                        'last_updated': int(time.time())
                    }

                    vm_dict, unmapped = map_attributes(src="os_vms", dest="csv2", attr_dict=vm_dict)
                    if unmapped:
                        logging.error("unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)
                    vm_dict['status_changed_time'] = parser.parse(vm.updated).astimezone(tz.tzlocal()).strftime('%s') 
                    new_vm = Vm(**vm_dict)
                    try:
                        db_session.merge(new_vm)
                    except Exception as exc:
                        logging.error(exc)
                        logging.error("unable to merge sessions, database incosistency or other error while proccessing vms for %s:%s:" % (cloud.group_name, cloud.cloud_name))
                try:        
                    db_session.commit()
                except Exception as exc:
                    logging.error(exc)
                    logging.error("Unable to commit database session while proccessing vms for grp:cloud - %s:%s:" % (cloud.group_name, cloud.cloud_name))
                    logging.error("Aborting cycle...")
            logging.debug("Poll cycle complete, sleeping...")
            try:
                new_pt = Poll_Times(process_id="vm_poller_" + str(socket.getfqdn()), last_poll=poll_time)
                db_session.merge(new_pt)
                db_session.commit()
            except Exception as exc:
                logging.error(exc)
                logging.error("Unable to update vm poll time")
            # This cycle should be reasonably fast such that the scheduler will always have the most
            # up to date data during a given execution cycle.
            time.sleep(config.vm_sleep_interval)
        except Exception as exc:
            logging.error(exc)
            logging.error("Error during database automapping or general execution")
            logging.error("Aborting cycle...")
            time.sleep(config.vm_sleep_interval)


    return None


def flavorPoller():
    multiprocessing.current_process().name = "Flavor Poller"

    while True:
        #thingdo
        try:
            Base = automap_base()
            engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
                "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
            Base.prepare(engine, reflect=True)
            db_session = Session(engine)
            Flavor = Base.classes.cloud_flavors
            Cloud = Base.classes.csv2_group_resources
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")

            logging.debug("Polling flavors")
            current_cycle = int(time.time())
            for cloud in cloud_list:
                logging.info("Processing flavours from group:cloud -  %s:%s" % (cloud.group_name, cloud.cloud_name))
                authsplit = cloud.authurl.split('/')
                try:
                    version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
                except ValueError:
                    logging.error("Bad openstack URL, could not determine version, skipping %s" % cloud.authurl)
                    continue
                if version == 2:
                    session = get_openstack_session(
                        auth_url=cloud.authurl,
                        username=cloud.username,
                        password=cloud.password,
                        project=cloud.project)
                else:
                    session = get_openstack_session(
                        auth_url=cloud.authurl,
                        username=cloud.username,
                        password=cloud.password,
                        project=cloud.project,
                        user_domain=cloud.user_domain_name,
                        project_domain_name=cloud.project_domain_name)

                if session is False:
                    logging.error("Unable to setup session, skipping %s", cloud.cloud_name)
                    if version == 2:
                        logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
                    else:
                        logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
                    continue
                # setup openstack api objects
                nova = get_nova_client(session)

                flav_list = get_flavor_data(nova)
                if flav_list is False:
                    continue
                for flavor in flav_list:
                    if flavor.swap == "":
                        swap = 0
                    else:
                        swap = flavor.swap

                    if flavor.disk == "":
                        disk = 0
                    else:
                        disk = flavor.disk
                    flav_dict = {
                        'group_name': cloud.group_name,
                        'cloud_name': cloud.cloud_name,
                        'name': flavor.name,
                        'ram': flavor.ram,
                        'vcpus': flavor.vcpus,
                        'id': flavor.id,
                        'swap': swap,
                        'disk': disk,
                        'ephemeral_disk': flavor.ephemeral,
                        'is_public': flavor.__dict__.get('os-flavor-access:is_public'),
                        'last_updated': current_cycle
                    }
                    flav_dict, unmapped = map_attributes(src="os_flavors", dest="csv2", attr_dict=flav_dict)
                    if unmapped:
                        logging.error("Unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)
                    new_flav = Flavor(**flav_dict)
                    db_session.merge(new_flav)

                #now remove any that were not updated
                flav_to_delete = db_session.query(Flavor).filter(
                    Flavor.last_updated < current_cycle,
                    Flavor.group_name == cloud.group_name,
                    Flavor.cloud_name == cloud.cloud_name)
                for flav in flav_to_delete:
                    logging.info("Cleaning up flavor: %s", flav)
                    db_session.delete(flav)
            try:        
                db_session.commit()
            except Exception as exc:
                logging.error("Unable to commit database session")
                logging.error(exc)
                logging.error("Aborting cycle...")
            logging.debug("End of cycle, sleeping...")
            time.sleep(config.flavor_sleep_interval)

        except Exception as exc:
            logging.error(exc)
            logging.error("Exception during database automapping or general execution")
            logging.error("Aborting cycle...")
            logging.debug("End of cycle, sleeping...")
            time.sleep(config.flavor_sleep_interval)

    return None

def imagePoller():
    multiprocessing.current_process().name = "Image Poller"

    while True:
        #thingdo
        Base = automap_base()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        db_session.autoflush = False
        Image = Base.classes.cloud_images
        Cloud = Base.classes.csv2_group_resources
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")

        logging.debug("Polling Images")
        current_cycle = int(time.time())
        current_cycle = int(time.time())
        for cloud in cloud_list:
            logging.info("Processing Images from group:cloud -  %s:%s" % (cloud.group_name, cloud.cloud_name))
            authsplit = cloud.authurl.split('/')
            try:
                version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
            except ValueError:
                logging.error("Bad openstack URL, could not determine version, skipping %s", cloud.authurl)
                continue
            if version == 2:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project)
            else:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project,
                    user_domain=cloud.user_domain_name,
                    project_domain_name=cloud.project_domain_name)
            if session is False:
                logging.error("Unable to setup session, skipping %s", cloud.cloud_name)
                if version == 2:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
                else:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
                continue

            # setup openstack api object
            nova = get_nova_client(session)

            image_list = get_image_data(nova)
            if image_list is False:
                continue
            for image in image_list:
                if image.size == "":
                    size = 0
                else:
                    size = image.size

                img_dict = {
                    'group_name': cloud.group_name,
                    'cloud_name': cloud.cloud_name,
                    'container_format': image.container_format,
                    'disk_format': image.disk_format,
                    'min_ram': image.min_ram,
                    'id': image.id,
                    'size': size,
                    'visibility': image.visibility,
                    'min_disk': image.min_disk,
                    'name': image.name,
                    'last_updated': current_cycle
                }
                img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=img_dict)
                if unmapped:
                    logging.error("Unmapped attributes found during mapping, discarding:")
                    logging.error(unmapped)
                new_image = Image(**img_dict)
                try:
                    db_session.merge(new_image)
                except Exception as exc:
                    logging.error(exc)
                    logging.error("Database inconsistency, unable to merge image entry:")
                    logging.error(img_dict)
            try:        
                db_session.commit()
            except Exception as exc:
                logging.error(exc)
                logging.error("Unable to commit database session while proccessing for grp:cloud - %s:%s:" % (cloud.group_name, cloud.cloud_name))
                logging.error("Aborting poll cycle...")
                break
            # do Image cleanup
            img_to_delete = db_session.query(Image).filter(
                Image.last_updated < current_cycle,
                Image.group_name == cloud.group_name,
                Image.cloud_name == cloud.cloud_name)
            for img in img_to_delete:
                logging.info("Cleaning up image: %s", img)
                db_session.delete(img)

        try:        
            db_session.commit()
        except Exception as exc:
            logging.error(exc)
            logging.error("Unable to perform final commit of database session")
            logging.error("Aborting cycle...")
        logging.debug("End of cycle, sleeping...")
        time.sleep(config.image_sleep_interval)

def limitPoller():
    multiprocessing.current_process().name = "Limit Poller"

    while True:
        #thingdo
        Base = automap_base()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        Limit = Base.classes.cloud_limits
        Cloud = Base.classes.csv2_group_resources
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")


        current_cycle = int(time.time())
        for cloud in cloud_list:
            logging.info("Processing Limits from group:cloud -  %s:%s" % (cloud.group_name, cloud.cloud_name))
            authsplit = cloud.authurl.split('/')
            try:
                version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
            except ValueError:
                logging.error("Bad openstack URL, could not determine version, skipping %s", cloud.authurl)
                continue
            if version == 2:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project)
            else:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project,
                    user_domain=cloud.user_domain_name,
                    project_domain_name=cloud.project_domain_name)

            if session is False:
                logging.error("Unable to setup session, skipping %s", cloud.cloud_name)
                if version == 2:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
                else:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
                continue
            # setup openstack api objects
            nova = get_nova_client(session)

            logging.debug("Polling limits")
            limits_dict = get_limit_data(nova)
            if limits_dict is False:
                continue
            limits_dict['group_name'] = cloud.group_name
            limits_dict['cloud_name'] = cloud.cloud_name
            limits_dict['last_updated'] = int(time.time())
            limits_dict, unmapped = map_attributes(src="os_limits", dest="csv2", attr_dict=limits_dict)
            if unmapped:
                logging.error("Unmapped attributes found during mapping, discarding:")
                logging.error(unmapped)
            for key in limits_dict:
                if "-1" in str(limits_dict[key]):
                    limits_dict[key] = config.no_limit_default

            new_limits = Limit(**limits_dict)
            db_session.merge(new_limits)

            #now remove any that were not updated
            limit_to_delete = db_session.query(Limit).filter(
                Limit.last_updated < current_cycle,
                Limit.group_name == cloud.group_name,
                Limit.cloud_name == cloud.cloud_name)
            for limit in limit_to_delete:
                logging.info("Cleaning up limit %s", limit)
                db_session.delete(limit)

        try:        
            db_session.commit()
        except Exception as exc:
            logging.error(exc)
            logging.error("Unable to commit database session")
            logging.error("Aborting cycle...")
        logging.debug("End of cycle, sleeping...")
        time.sleep(config.limit_sleep_interval)

    return None

def networkPoller():
    multiprocessing.current_process().name = "Network Poller"
    last_cycle = 0

    while True:
        #thingdo
        Base = automap_base()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        db_session.autoflush = False
        Network = Base.classes.cloud_networks
        Cloud = Base.classes.csv2_group_resources
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")


        current_cycle = int(time.time())
        for cloud in cloud_list:
            logging.info("Processing Limits from group:cloud -  %s:%s" % (cloud.group_name, cloud.cloud_name))
            authsplit = cloud.authurl.split('/')
            try:
                version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
            except ValueError:
                logging.error("Bad openstack URL, could not determine version, skipping %s", cloud.authurl)
                continue
            if version == 2:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project)
            else:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project,
                    user_domain=cloud.user_domain_name,
                    project_domain_name=cloud.project_domain_name)

            if session is False:
                logging.error("Unable to setup session, skipping %s", cloud.cloud_name)
                if version == 2:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
                else:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
                continue
            # setup openstack api objects
            neutron = get_neutron_client(session)
            net_list = get_network_data(neutron)
            if net_list is False:
                continue
            for network in net_list:
                network_dict = {
                    'group_name': cloud.group_name,
                    'cloud_name': cloud.cloud_name,
                    'name': network['name'],
                    'subnets': ''.join(network['subnets']),
                    'tenant_id': network['tenant_id'],
                    'router:external': network['router:external'],
                    'shared': network['shared'],
                    'id': network['id'],
                    'last_updated': int(time.time())
                }
                network_dict, unmapped = map_attributes(
                    src="os_networks",
                    dest="csv2",
                    attr_dict=network_dict)
                if unmapped:
                    logging.error("Unmapped attributes found during mapping, discarding:")
                    logging.error(unmapped)
                new_network = Network(**network_dict)
                db_session.merge(new_network)

            #now remove any that were not updated
            net_to_delete = db_session.query(Network).filter(
                Network.last_updated <= last_cycle,
                Network.group_name == cloud.group_name,
                Network.cloud_name == cloud.cloud_name)
            for net in net_to_delete:
                logging.info("Cleaning up network: %s", net)
                db_session.delete(net)

        try:        
            db_session.commit()
            last_cycle = current_cycle
        except Exception as exc:
            logging.error(exc)
            logging.error("Unable to commit database session")
            logging.error("Aborting cycle...")
        logging.debug("End of cycle, sleeping...")
        time.sleep(config.network_sleep_interval)

    return None

# def vmExecutor():
# May need a process to relay commands to the VMs (peaceful shutdown//kill)


# The VMs will need to be cleaned up more frequently and as such
# the vm cleanup routine will have its own process on its own cycle
def vmCleanUp():
    multiprocessing.current_process().name = "VM Cleanup"
    last_cycle = 0
    vm_poller_id = "vm_poller_" + str(socket.getfqdn())
    while True:
        current_cycle_time = time.time()
        #set up database objects
        logging.debug("Begining cleanup cycle")
        Base = automap_base()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        Vm = Base.classes.csv2_vms
        Poll_Times = Base.classes.csv2_poll_times
        Cloud = Base.classes.csv2_group_resources

        last_vm_poll = db_session.query(Poll_Times).filter(Poll_Times.process_id == vm_poller_id)
        if last_cycle == 0:
            logging.info("First cycle, sleeping for now...")
            #first cycle- just sleep for the first while waiting for db updates.
            last_cycle = current_cycle_time
            time.sleep(config.vm_cleanup_interval)
            continue
        elif last_cycle >= last_vm_poll[0].last_poll:
            logging.error("vm poller hasn't been run since last cleanup, there may be a problem with the vm poller process")
            logging.error("Skipping cycle...")
            time.sleep(config.vm_cleanup_interval)
            continue

        # check for vms that have dissapeared since the last cycle
        logging.debug("Querying database for vms to remove...")
        vm_to_delete = db_session.query(Vm).filter(Vm.last_updated <= last_cycle)
        for vm in vm_to_delete:
            logging.info("Cleaning up VM: %s from group:cloud - %s:%s" % (vm.hostname, vm.group_name, vm.cloud_name))
            db_session.delete(vm)

        # need to commit the session here to remove vms that are gone before we look at which to terminate

        try:        
            db_session.commit()
        except Exception as exc:
            logging.error(exc)
            logging.error("Unable to commit database session")
            logging.error("Aborting cycle...")
            logging.info("Sleeping...")
            time.sleep(config.vm_cleanup_interval)
            continue
        db_session = Session(engine)

        # check for vms that have been marked for termination
        logging.debug("Querying database for VMs marked for termination...")
        vm_to_destroy = db_session.query(Vm).filter(Vm.terminate == 1, Vm.manual_control != 1)
        for vm in vm_to_destroy:
            logging.info("VM marked for termination... terminating: %s from group:cloud - %s:%s" % (vm.hostname, vm.group_name, vm.cloud_name))
            # terminate vm
            # need to get cloud data from csv2_group_resources using group_name + cloud_name from vm
            logging.info("Getting cloud connection info from group resources..")
            cloud = db_session.query(Cloud).filter(
                Cloud.group_name == vm.group_name,
                Cloud.cloud_name == vm.cloud_name).first()
            authsplit = cloud.authurl.split('/')
            try:
                version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
            except ValueError:
                logging.error("Bad openstack URL, could not determine version, skipping %s URL: %s", (vm, cloud.authurl))
                continue
            logging.info("Creating openstack session for group:cloud - %s:%s" % (cloud.group_name, cloud.cloud_name))
            if version == 2:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project)
            else:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project,
                    user_domain=cloud.user_domain_name,
                    project_domain_name=cloud.project_domain_name)
            if session is False:
                logging.error("Unable to setup session, unable to terminate %s", vm)
                if version == 2:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (auth_url, username, project))
                else:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            # returns true if vm terminated, false if an error occured
            # probably wont need to use this result outside debugging as
            # deleted VMs should be removed on the next cycle
            logging.info("Terminating %s", (vm.hostname,))
            result = terminate_vm(session, vm)

        try:        
            db_session.commit()
            last_cycle = current_cycle_time
        except Exception as exc:
            logging.error(exc)
            logging.error("Unable to commit database session")
            logging.error("Aborting cycle...")

        time.sleep(config.vm_cleanup_interval)
    return None

def keypairPoller():
    multiprocessing.current_process().name = "Keypair Poller"
    last_cycle = 0

    while True:
        current_cycle_time = time.time()
        #set up database objects
        logging.debug("Begining keypair polling cycle")
        Base = automap_base()
        engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
            "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
        Base.prepare(engine, reflect=True)
        db_session = Session(engine)
        Keypairs = Base.classes.cloud_keypairs
        Cloud = Base.classes.csv2_group_resources
        cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")

        current_cycle = int(time.time())
        for cloud in cloud_list:
            logging.info("Processing Keypairs from group:cloud -  %s:%s" % (cloud.group_name, cloud.cloud_name))
            authsplit = cloud.authurl.split('/')
            try:
                version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
            except ValueError:
                logging.error("Bad openstack URL, could not determine version, skipping %s", cloud.authurl)
                continue
            if version == 2:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project)
            else:
                session = get_openstack_session(
                    auth_url=cloud.authurl,
                    username=cloud.username,
                    password=cloud.password,
                    project=cloud.project,
                    user_domain=cloud.user_domain_name,
                    project_domain_name=cloud.project_domain_name)

            if session is False:
                logging.error("Unable to setup session, skipping %s", cloud.cloud_name)
                if version == 2:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s", (cloud.auth_url, cloud.username, cloud.project))
                else:
                    logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (cloud.auth_url, cloud.sername, cloud.project, cloud.user_domain, cloud.project_domain_name))
                continue

            # setup openstack api objects
            nova = get_nova_client(session)

            #setup fingerprint list
            fingerprint_list = []

            try:
                # get keypairs and add them to database
                cloud_keys = nova.keypairs.list()
            except Exception as exc:
                logging.error(exc)
                logging.error("Unable to poll keypairs from nova, skipping %s-%s" % (cloud.group_name, cloud.cloud_name))
            for key in cloud_keys:
                key_dict = {
                    "cloud_name":  cloud.cloud_name,
                    "group_name":  cloud.group_name,
                    "key_name":    key.name,
                    "fingerprint": key.fingerprint
                }
                fingerprint_list.append(key.fingerprint)
                new_key = Keypairs(**key_dict)
                db_session.merge(new_key)
            try:
                db_session.commit()
            except Exception as exc:
                logging.error(exc)
                logging.error("Unable to commit database session during keypair proccessing")
                logging.error("Skipping %s - %s" % (cloud.group_name, cloud.cloud_name))
                break

            # now we need to check database for any keys that have been deleted
            db_keys = db_session.query(Keypairs).filter(
                Keypairs.cloud_name == cloud.cloud_name,
                Keypairs.group_name == cloud.group_name)

            for key in db_keys:
                #check against fingerprint list created earlier
                if key.fingerprint not in fingerprint_list:
                    # delete it
                    db_session.delete(key)
            try:
                db_session.commit()
            except Exception as exc:
                logging.error(exc)
                logging.error("Unable to commit database session during keypair proccessing")
                logging.error("Skipping %s - %s" % (cloud.group_name, cloud.cloud_name))
                break
        logging.info("End of cycle, sleeping")
        time.sleep(config.keypair_sleep_interval)



## MAIN
#
if __name__ == '__main__':

    logging.basicConfig(
        filename=config.poller_log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-12s - %(levelname)s - %(message)s')
    processes = []

    p_vm_poller = Process(target=vm_poller)
    processes.append(p_vm_poller)
    p_vm_cleanup = Process(target=vmCleanUp)
    processes.append(p_vm_cleanup)
    p_flavor_poller = Process(target=flavorPoller)
    processes.append(p_flavor_poller)
    p_image_poller = Process(target=imagePoller)
    processes.append(p_image_poller)
    p_limit_poller = Process(target=limitPoller)
    processes.append(p_limit_poller)
    p_network_poller = Process(target=networkPoller)
    processes.append(p_network_poller)
    p_keypair_poller = Process(target=keypairPoller)
    processes.append(p_keypair_poller)

    # Wait for keyboard input to exit
    try:
        for process in processes:
            process.start()
        while True:
            for process in processes:
                if not process.is_alive():
                    logging.error("%s process died!", process.name)
                    logging.error("Restarting %s process...", process.name)
                    process.start()
                time.sleep(1)
            time.sleep(10)
    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process.name)
