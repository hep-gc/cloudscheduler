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

def delete_obsolete_items(type, inventory, db_session, base_class, item_key):
    for group_name in inventory:
        for cloud_name in inventory[group_name]:
            obsolete_items = db_session.query(base_class).filter(
                base_class.group_name == group_name,
                base_class.cloud_name == cloud_name
                )

            uncommitted_updates = 0
            for item in obsolete_items:
                if item[item_key] not in inventory[group_name][cloud_name]:
                    logging.info("Cleaning up %s: %s from group:cloud - %s::%s" % (type, item.item_key, item.group_name, item.cloud_name))
                    try:
                        db_session.delete(item)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to delete %s." % type)
                        logging.error(exc)

            if uncommitted_updates > 0:
                try:        
                    db_session.commit()
                    logging.info("%s deletions committed: %d" % (type, uncommitted_updates))
                except Exception as exc:
                    logging.exception("Failed to commit %s deletions (%d) for %s::%s." % (type, uncommitted_updates, cloud.group_name, cloud.cloud_name))
                    logging.error(exc)

def foreign(vm):
    native_id = '%s--%s--' % (vm.group_name, vm.cloud_name)
    if vm.hostname[:len(native_id)] == native_id:
        return False
    else:
        return True

def get_cinder_client(session):
    cinder = cinclient.Client("2", session=session)
    return cinder

def get_flavor_data(nova):
    try:
        return  nova.flavors.list()
    except Exception as exc:
        logging.error("Failed to retrieve Flavor data")
        logging.error(exc)
        return False

def get_neutron_client(session):
    neutron = neuclient.Client(session=session)
    return neutron

def get_nova_client(session):
    nova = novaclient.Client("2", session=session)
    return nova

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
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s::%s" % (auth_url, exc))
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

def save_inventory_group_and_cloud(inventory, group_name, cloud_name):
    if group_name not in inventory:
        inventory[group_name] = {}

    if cloud_name not in inventory[group_name]:
        inventory[group_name][cloud_name] = {}

    return

def save_inventory_item(inventory, group_name, cloud_name, item, update_time):
    inventory[group_name][cloud_name][item] = True
    return int(parser.parse(update_time).astimezone(tz.tzlocal()).strftime('%s'))

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
        logging.error("Failed to retrieve Limit data")
        logging.error(exc)
        return False


def get_image_data(nova):
    try:
        return nova.glance.list()
    except Exception as exc:
        logging.error("Failed to retrieve Image data")
        logging.error(exc)
        return False


def get_network_data(neutron):
    try:
        return neutron.list_networks()['networks']
    except Exception as exc:
        logging.error("Failed to retrieve Network data")
        logging.error(exc)
        return False

def get_vm_list(nova):
    try:
        return nova.servers.list()
    except Exception as exc:
        logging.error("Failed to retrieve VM list")
        logging.error(exc)
        return False

def terminate_vm(session, vm):
    nova = get_nova_client(session)
    try:
        nova.servers.delete(vm.vmid)
        return True
    except Exception as exc:
        logging.error("Failed to terminate vm: %s", vm.hostname)
        logging.error(exc)
        return False


def get_session(cloud):
    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
        return False
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
        logging.error("Failed to setup session, skipping %s", cloud.cloud_name)
        if version == 2:
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s",
                          (cloud.authurl, cloud.username, cloud.project))
        else:
            logging.error(
                "Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s",
                (cloud.authurl, cloud.username, cloud.project, cloud.user_domain, cloud.project_domain_name))
    return session

## PROCESS FUNCTIONS

# This process thread will be responsible for polling the list of VMs from each registered
# OpenStack cloud and reporting their state back to the database for use by cloud scheduler
#
def vm_poller():
    multiprocessing.current_process().name = "VM Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Vm = Base.classes.csv2_vms
    Cloud = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        while True:
            # This cycle should be reasonably fast such that the scheduler will always have the most
            # up to date data during a given execution cycle.
            logging.info("Beginning VM poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            # For each OpenStack cloud, retrieve and process VMs.
            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Polling VMs from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = get_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup nova object
                save_inventory_group_and_cloud(inventory, cloud.group_name, cloud.cloud_name,)
                nova = get_nova_client(session)

                # get server list
                vm_list = get_vm_list(nova)
                if vm_list is False:
                    logging.info("No VMs defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    del nova
                    continue

                uncommitted_updates = 0
                for vm in vm_list:
                    vm_update_time = save_inventory_item(inventory, cloud.group_name, cloud.cloud_name, vm.name, vm.updated)
                    if vm_update_time < last_poll_time:
                        continue

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

                    vm_dict['status_changed_time'] = vm_update_time
                    new_vm = Vm(**vm_dict)
                    try:
                        db_session.merge(new_vm)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge VM entry for %s::%s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name, vm.name))
                        logging.error(exc)
                        abort_cycle = True
                        break

                del nova
                if abort_cycle:
                    break

                if uncommitted_updates > 0:
                    try:        
                        db_session.commit()
                        logging.info("VM updates committed: %d" % uncommitted_updates)
                    except Exception as exc:
                        logging.exception("Failed to commit VM updates for %s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name))
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                del inventory
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            # Scan the OpenStack VMs in the database, removing each one that is not in the inventory.
            delete_obsolete_items('VM', inventory, db_session, Vm, 'hostname')
#           for group_name in inventory:
#               for cloud_name in inventory[group_name]:
#                   obsolete_vms = db_session.query(Vm).filter(
#                       Vm.group_name == group_name,
#                       Vm.cloud_name == cloud_name
#                       )

#                   uncommitted_updates = 0
#                   for vm in obsolete_vms:
#                       if vm.hostname not in inventory[group_name][cloud_name]:
#                           logging.info("Cleaning up VM: %s from group:cloud - %s::%s" % (vm.hostname, vm.group_name, vm.cloud_name))
#                           try:
#                               db_session.delete(vm)
#                               uncommitted_updates += 1
#                           except Exception as exc:
#                               logging.exception("Failed to delete VM.")
#                               logging.error(exc)

#                   if uncommitted_updates > 0:
#                       try:        
#                           db_session.commit()
#                           logging.info("VM deletions committed: %d" % uncommitted_updates)
#                       except Exception as exc:
#                           logging.exception("Failed to commit VM deletions (%d) for %s::%s." % (uncommitted_updates, cloud.group_name, cloud.cloud_name))
#                           logging.error(exc)

            logging.info("Completed VM poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.vm_sleep_interval)

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def flavorPoller():
    multiprocessing.current_process().name = "Flavor Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password +
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Flavor = Base.classes.cloud_flavors
    Cloud = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        while True:
            logging.info("Beginning flavor poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing flavours from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = get_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup OpenStack api objects
                nova = get_nova_client(session)

                flav_list = get_flavor_data(nova)
                if flav_list is False:
                    logging.info("No flavors defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
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
                        'last_updated': new_poll_time
                    }
                    flav_dict, unmapped = map_attributes(src="os_flavors", dest="csv2", attr_dict=flav_dict)
                    if unmapped:
                        logging.error("Unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)
                    new_flav = Flavor(**flav_dict)
                    try:
                        db_session.merge(new_flav)
                    except Exception as exc:
                        logging.exception("Failed to merge flavor entry for %s::%s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name, flavor.name))
                        logging.error(exc)
                        abort_cycle = True
                        break

                #now remove any that were not updated
                flav_to_delete = db_session.query(Flavor).filter(
                    Flavor.last_updated < new_poll_time,
                    Flavor.group_name == cloud.group_name,
                    Flavor.cloud_name == cloud.cloud_name)
                for flav in flav_to_delete:
                    logging.info("Cleaning up flavor: %s::%s::%s" % (cloud.group_name, cloud.cloud_name, flavor.name))
                    db_session.delete(flav)

                try:        
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit flavor updates for %s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    abort_cycle = True
                    break

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            logging.info("Completed flavor poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.flavor_sleep_interval)

    except Exception as exc:
        logging.exception("Flavor poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def imagePoller():
    multiprocessing.current_process().name = "Image Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Image = Base.classes.cloud_images
    Cloud = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        while True:
            logging.info("Beginning image poller cycle")
            db_session = Session(engine)
            # db_session.autoflush = False
            new_poll_time = int(time.time())

            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing Images from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = get_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup OpenStack api object
                nova = get_nova_client(session)

                image_list = get_image_data(nova)
                if image_list is False:
                    logging.info("No images defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
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
                        'last_updated': new_poll_time
                    }
                    img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=img_dict)
                    if unmapped:
                        logging.error("Unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)
                    new_image = Image(**img_dict)
                    try:
                        db_session.merge(new_image)
                    except Exception as exc:
                        logging.exception("Failed to merge image entry for %s::%s::%s:" % (cloud.group_name, cloud.cloud_name, image.name))
                        logging.error(exc)
                        abort_cycle = True
                        break

                if abort_cycle:
                    break

                # do Image cleanup
                img_to_delete = db_session.query(Image).filter(
                    Image.last_updated < new_poll_time,
                    Image.group_name == cloud.group_name,
                    Image.cloud_name == cloud.cloud_name)
                for img in img_to_delete:
                    logging.info("Cleaning up image: %s::%s::%s" % (cloud.group_name, cloud.cloud_name, img.name))
                    db_session.delete(img)

                # Commit changes for the cloud.
                try:        
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit image updates for %s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    abort_cycle = True
                    break

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            logging.info("Completed image poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.image_sleep_interval)

    except Exception as exc:
        logging.exception("Image poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def limitPoller():
    multiprocessing.current_process().name = "Limit Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Limit = Base.classes.cloud_limits
    Cloud = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        while True:
            logging.info("Beginning limit poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing Limits from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = get_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup OpenStack api objects
                nova = get_nova_client(session)

                limits_dict = get_limit_data(nova)
                if limits_dict is False:
                    logging.info("No limits defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
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
                    Limit.last_updated < new_poll_time,
                    Limit.group_name == cloud.group_name,
                    Limit.cloud_name == cloud.cloud_name)
                for limit in limit_to_delete:
                    logging.info("Cleaning up limit: %s::%s::%s" % (cloud.group_name, cloud.cloud_name, limit))
                    db_session.delete(limit)

            try:        
                db_session.commit()
            except Exception as exc:
                logging.exception("Failed to commit limit updates, aborting cycle...")
                logging.error(exc)
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            logging.info("Completed limit poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.limit_sleep_interval)

    except Exception as exc:
        logging.exception("Limit poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def networkPoller():
    multiprocessing.current_process().name = "Network Poller"
    last_poll_time = 0
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Network = Base.classes.cloud_networks
    Cloud = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        while True:
            logging.info("Beginning network poller cycle")
            db_session = Session(engine)
            # db_session.autoflush = False
            new_poll_time = int(time.time())

            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing networks from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = get_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup OpenStack api objects
                neutron = get_neutron_client(session)
                net_list = get_network_data(neutron)
                if net_list is False:
                    logging.info("No networks defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
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
                    Network.last_updated <= last_poll_time,
                    Network.group_name == cloud.group_name,
                    Network.cloud_name == cloud.cloud_name)
                for net in net_to_delete:
                    logging.info("Cleaning up network: %s::%s::%s" % (cloud.group_name, cloud.cloud_name, net))
                    db_session.delete(net)

            try:        
                db_session.commit()
                last_poll_time = new_poll_time
            except Exception as exc:
                logging.exception("Failed to commit network updates, aborting cycle...")
                logging.error(exc)
                db_session.close()
                time.sleep(config.network_sleep_interval)
                continue

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            logging.info("Completed network poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.network_sleep_interval)

    except Exception as exc:
        logging.exception("Network poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

# The VMs will need to be cleaned up more frequently and as such
# the vm cleanup routine will have its own process on its own cycle
def vmCleanUp():
    multiprocessing.current_process().name = "VM Cleanup"
    last_poll_time = 0
    vm_poller_id = "vm_poller_" + str(socket.getfqdn())
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Vm = Base.classes.csv2_vms
    Cloud = Base.classes.csv2_group_resources

    try:
        while True:
            logging.info("Beginning cleanup poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            # check for vms that have been marked for termination
            logging.info("Querying database for VMs marked for termination...")
            vm_to_destroy = db_session.query(Vm).filter(Vm.terminate == 1, Vm.manual_control != 1)
            for vm in vm_to_destroy:
                if foreign(vm):
                    logging.info("skipping foreign VM %s marked for termination... - %s::%s" % (vm.hostname, vm.group_name, vm.cloud_name))
                    continue

                logging.info("VM marked for termination... terminating: %s from group:cloud - %s::%s" % (vm.hostname, vm.group_name, vm.cloud_name))
                # terminate vm
                # need to get cloud data from csv2_group_resources using group_name + cloud_name from vm
                logging.info("Getting cloud connection info from group resources..")
                cloud = db_session.query(Cloud).filter(
                    Cloud.group_name == vm.group_name,
                    Cloud.cloud_name == vm.cloud_name).first()
                session = get_session(cloud)
                if session is False:
                    continue
                # returns true if vm terminated, false if an error occurred
                # probably wont need to use this result outside debugging as
                # deleted VMs should be removed on the next cycle
                logging.info("Terminating %s", (vm.hostname,))
                result = terminate_vm(session, vm)

            try:        
                db_session.commit()
                last_poll_time = new_poll_time
            except Exception as exc:
                logging.exception("Failed to commit VM terminations, aborting cycle...")
                logging.error(exc)
                db_session.close()
                time.sleep(config.vm_cleanup_interval)
                continue

            logging.info("Completed cleanup poller cycle")
            last_poll_time = new_poll_time
            db_session.close()
            time.sleep(config.vm_cleanup_interval)

    except Exception as exc:
        logging.exception("Cleanup poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def keypairPoller():
    multiprocessing.current_process().name = "Keypair Poller"
    last_poll_time = 0
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    Keypairs = Base.classes.cloud_keypairs
    Cloud = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        while True:
            logging.info("Beginning keypair poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(Cloud).filter(Cloud.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing Key pairs from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = get_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s" % (cloud.group_name, cloud.cloud_name))
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
                    logging.error("Failed to poll key pairs from nova, skipping %s::%s" % (cloud.group_name, cloud.cloud_name))
                    continue

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
                    logging.error("Failed to commit new keypairs for %s::%s, aborting cycle..."  % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
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
                    logging.error("Failed to commit keypair deletions for %s::%s, aborting cycle..."  % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    break

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            logging.info("Completed keypair poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.keypair_sleep_interval)

    except Exception as exc:
        logging.exception("Keypair poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

## MAIN
#
if __name__ == '__main__':

    logging.basicConfig(
        filename=config.poller_log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-16s - %(levelname)s - %(message)s')

    logging.info("**************************** starting openstack VM poller *********************************")

    processes = {}
    process_ids = {
        'vm':          vm_poller,
        'cleanup':     vmCleanUp,
        'flavor':      flavorPoller,
        'image':       imagePoller,
        'limit':       limitPoller,
        'network':     networkPoller,
        'keypair':     keypairPoller,
        }

    # Wait for keyboard input to exit
    try:
        while True:
            for process in process_ids:
                if process not in processes or not processes[process].is_alive():
                    if process in processes:
                        logging.error("%s process died, restarting...", process)
                        del(processes[process])
                    else:
                        logging.info("Restarting %s process", process)
                    processes[process] = Process(target=process_ids[process])
                    processes[process].start()
                    time.sleep(config.main_short_interval)
            time.sleep(config.main_long_interval)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process.name)
