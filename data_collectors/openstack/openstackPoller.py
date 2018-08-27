import multiprocessing
from multiprocessing import Process
import datetime
import hashlib
import datetime
import logging
import socket
import time
from dateutil import tz, parser

import config

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

## Poller sub-functions.

def _delete_obsolete_items(type, inventory, db_session, base_class, item_key, poll_time=None):
    for group_name in inventory:
        for cloud_name in inventory[group_name]:
            obsolete_items = db_session.query(base_class).filter(
                base_class.group_name == group_name,
                base_class.cloud_name == cloud_name
                )

            uncommitted_updates = 0
            for item in obsolete_items:
                if item_key == '-' and poll_time:
                    if inventory[group_name][cloud_name]['-']['poll_time'] >= poll_time:
                        continue
                    else:
                        del inventory[group_name][cloud_name]
                else:
                    if poll_time:
                        if item.__dict__[item_key] in inventory[group_name][cloud_name] and inventory[group_name][cloud_name][item.__dict__[item_key]]['poll_time'] >= poll_time:
                            continue
                        else:
                            del inventory[group_name][cloud_name][item.__dict__[item_key]]
                    else:
                        if item.__dict__[item_key] in inventory[group_name][cloud_name]:
                            continue

                logging.info("Cleaning up %s: %s from group:cloud - %s::%s" % (type, item.__dict__[item_key], item.group_name, item.cloud_name))
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

def _foreign(vm):
    native_id = '%s--%s--' % (vm.group_name, vm.cloud_name)
    if vm.hostname[:len(native_id)] == native_id:
        return False
    else:
        return True

def _get_neutron_client(session):
    neutron = neuclient.Client(session=session)
    return neutron

def _get_nova_client(session):
    nova = novaclient.Client("2", session=session)
    return nova

def _get_openstack_session(cloud):
    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.error("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
        return False
    if version == 2:
        session = _get_openstack_session_v1_v2(
            auth_url=cloud.authurl,
            username=cloud.username,
            password=cloud.password,
            project=cloud.project)
    else:
        session = _get_openstack_session_v1_v2(
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

def _get_openstack_session_v1_v2(auth_url, username, password, project, user_domain="Default", project_domain_name="Default"):
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

def _inventory_group_and_cloud(inventory, group_name, cloud_name):
    if group_name not in inventory:
        inventory[group_name] = {}

    if cloud_name not in inventory[group_name]:
        inventory[group_name][cloud_name] = {}

    return

def _inventory_item(inventory, group_name, cloud_name, item, update_time):
    inventory[group_name][cloud_name][item] = True
    return int(parser.parse(update_time).astimezone(tz.tzlocal()).strftime('%s'))

def _inventory_item_hash(inventory, group_name, cloud_name, item, item_dict, poll_time):
    _inventory_group_and_cloud(inventory, group_name, cloud_name)

    if item not in inventory[group_name][cloud_name]:
        inventory[group_name][cloud_name][item] = {'hash': None}

    inventory[group_name][cloud_name][item]['poll_time'] = poll_time

    hash_object = hashlib.new('md5')
    for hash_item in item_dict:
       if hash_item == 'group_name' or hash_item == 'cloud_name' or hash_item == 'last_updated':
           continue
       
       logging.info("<<<<<<<<<<<<<<<<<<<<<<<< %s" % hash_item)
       hash_object.update(str(item_dict[hash_item]).encode('utf-8'))

    new_hash = hash_object.hexdigest()
    if new_hash == inventory[group_name][cloud_name][item]['hash']:
        return True

    inventory[group_name][cloud_name][item]['hash'] = new_hash
    return False

## Poller functions.

# Process VM commands.
def command_poller():
    multiprocessing.current_process().name = "VM Commands"
    last_poll_time = 0
    vm_poller_id = "vm_poller_" + str(socket.getfqdn())
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    VM = Base.classes.csv2_vms
    CLOUD = Base.classes.csv2_group_resources

    try:
        while True:
            logging.info("Beginning command poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            # Retrieve list of VMs to be terminated.
            vm_to_destroy = db_session.query(VM).filter(VM.terminate == 1, VM.manual_control != 1)
            for vm in vm_to_destroy:
                if _foreign(vm):
                    logging.info("skipping foreign VM %s marked for termination... - %s::%s" % (vm.hostname, vm.group_name, vm.cloud_name))
                    continue

                # Get session with hosting cloud.
                cloud = db_session.query(CLOUD).filter(
                    CLOUD.group_name == vm.group_name,
                    CLOUD.cloud_name == vm.cloud_name).first()
                session = _get_openstack_session(cloud)
                if session is False:
                    continue

                # Terminate the VM.
                nova = _get_nova_client(session)
                try:
                    nova.servers.delete(vm.vmid)
                    logging.info("VM Terminated: %s", (vm.hostname,))
                except Exception as exc:
                    logging.exception("Failed to terminate VM: %s", vm.hostname)
                    logging.error(exc)

            logging.info("Completed command poller cycle")
            last_poll_time = new_poll_time
            db_session.close()
            time.sleep(config.vm_cleanup_interval)

    except Exception as exc:
        logging.exception("Command poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def flavor_poller():
    multiprocessing.current_process().name = "Flavor Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password +
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    FLAVOR = Base.classes.cloud_flavors
    CLOUD = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        inventory = {}
        while True:
            logging.info("Beginning flavor poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing flavours from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup OpenStack api objects
                nova = _get_nova_client(session)

                # Retrieve all flavours for this cloud.
                try:
                    flav_list =  nova.flavors.list()
                except Exception as exc:
                    logging.error("Failed to retrieve flavor data for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    continue

                if flav_list is False:
                    logging.info("No flavors defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # Process flavours for this cloud.
                uncommitted_updates = 0
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

                    if _inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, flavor.name, flav_dict, new_poll_time):
                        continue

                    new_flav = FLAVOR(**flav_dict)
                    try:
                        db_session.merge(new_flav)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge flavor entry for %s::%s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name, flavor.name))
                        logging.error(exc)
                        abort_cycle = True
                        break

                del nova
                if abort_cycle:
                    break

                if uncommitted_updates > 0:
                    try:        
                        db_session.commit()
                        logging.info("Flavor updates committed: %d" % uncommitted_updates)
                    except Exception as exc:
                        logging.exception("Failed to commit flavor updates for %s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name))
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
            _delete_obsolete_items('Flavor', inventory, db_session, FLAVOR, 'name', poll_time=new_poll_time)

            logging.info("Completed flavor poller cycle")
            last_poll_time = new_poll_time
            db_session.close()
            time.sleep(config.flavor_sleep_interval)

    except Exception as exc:
        logging.exception("Flavor poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def image_poller():
    multiprocessing.current_process().name = "Image Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    IMAGE = Base.classes.cloud_images
    CLOUD = Base.classes.csv2_group_resources
    last_poll_time = 0

    try:
        while True:
            logging.info("Beginning image poller cycle")
            db_session = Session(engine)
            # db_session.autoflush = False
            new_poll_time = int(time.time())

            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing Images from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup OpenStack api object
                _inventory_group_and_cloud(inventory, cloud.group_name, cloud.cloud_name,)
                nova = _get_nova_client(session)

                # Retrieve all images for this cloud.
                try:
                    image_list =  nova.glance.list()
                except Exception as exc:
                    logging.error("Failed to retrieve image data for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    continue

                if image_list is False:
                    logging.info("No images defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                uncommitted_updates = 0
                for image in image_list:
                    image_update_time = _inventory_item(inventory, cloud.group_name, cloud.cloud_name, image.name, image.updated_at)
                    if image_update_time < last_poll_time:
                        continue

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

                    new_image = IMAGE(**img_dict)
                    try:
                        db_session.merge(new_image)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge image entry for %s::%s::%s:" % (cloud.group_name, cloud.cloud_name, image.name))
                        logging.error(exc)
                        abort_cycle = True
                        break

                del nova
                if abort_cycle:
                    break

                if uncommitted_updates > 0:
                    try:        
                        db_session.commit()
                        logging.info("Image updates committed: %d" % uncommitted_updates)
                    except Exception as exc:
                        logging.exception("Failed to commit image updates for %s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name))
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            # Scan the OpenStack images in the database, removing each one that is not in the inventory.
            _delete_obsolete_items('Image', inventory, db_session, IMAGE, 'name')

            logging.info("Completed image poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.image_sleep_interval)

    except Exception as exc:
        logging.exception("Image poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

# Retrieve keypairs.
def keypair_poller():
    multiprocessing.current_process().name = "Keypair Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    KEYPAIR = Base.classes.cloud_keypairs
    CLOUD = Base.classes.csv2_group_resources

    try:
        inventory = {}
        while True:
            logging.info("Beginning keypair poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing Key pairs from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s" % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup openstack api objects
                nova = _get_nova_client(session)

                #setup fingerprint list
                fingerprint_list = []

                try:
                    # get keypairs and add them to database
                    cloud_keys = nova.keypairs.list()
                except Exception as exc:
                    logging.error("Failed to poll key pairs from nova, skipping %s::%s" % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    continue

                uncommitted_updates = 0
                for key in cloud_keys:
                    key_dict = {
                        "cloud_name":  cloud.cloud_name,
                        "group_name":  cloud.group_name,
                        "key_name":    key.name,
                        "fingerprint": key.fingerprint
                    }
                    fingerprint_list.append(key.fingerprint)

                    if _inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, key.name, key_dict, new_poll_time):
                        continue

                    new_key = KEYPAIR(**key_dict)
                    try:
                        db_session.merge(new_key)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge keypair entry for %s::%s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name, key.name))
                        logging.error(exc)
                        abort_cycle = True
                        break

                del nova
                if abort_cycle:
                    break

                if uncommitted_updates > 0:
                    try:
                        db_session.commit()
                        logging.info("Keypair updates committed: %d" % uncommitted_updates)
                    except Exception as exc:
                        logging.error("Failed to commit new keypairs for %s::%s, aborting cycle..."  % (cloud.group_name, cloud.cloud_name))
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            # Scan the OpenStack keypairs in the database, removing each one that was not updated in the inventory.
            _delete_obsolete_items('Keypair', inventory, db_session, KEYPAIR, 'key_name', poll_time=new_poll_time)

            logging.info("Completed keypair poller cycle")
            db_session.close()
            time.sleep(config.keypair_sleep_interval)

    except Exception as exc:
        logging.exception("Keypair poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def limit_poller():
    multiprocessing.current_process().name = "Limit Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    LIMIT = Base.classes.cloud_limits
    CLOUD = Base.classes.csv2_group_resources

    try:
        inventory = {}
        while True:
            logging.info("Beginning limit poller cycle")
            db_session = Session(engine)
            new_poll_time = int(time.time())

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            uncommitted_updates = 0
            for cloud in cloud_list:
                logging.info("Processing Limits from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # Retrieve limit list for the current cloud.
                nova = _get_nova_client(session)

                limits_dict = {}
                try:
                    limit_list = nova.limits.get().absolute
                    for limit in limit_list:
                        limits_dict[limit.name] = [limit.value]
                except Exception as exc:
                    logging.error("Failed to retrieve limits from nova, skipping %s::%s" % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    continue

                if limits_dict is False:
                    logging.info("No limits defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # Process limit list for the current cloud.
                limits_dict['group_name'] = cloud.group_name
                limits_dict['cloud_name'] = cloud.cloud_name
                limits_dict['last_updated'] = int(time.time())
                limits_dict, unmapped = map_attributes(src="os_limits", dest="csv2", attr_dict=limits_dict)
                if unmapped:
                    logging.error("Unmapped attributes found during mapping, discarding:")
                    logging.error(unmapped)

                if _inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, '-', limits_dict, new_poll_time):
                    continue

                for limit in limits_dict:
                    if "-1" in str(limits_dict[limit]):
                        limits_dict[limit] = config.no_limit_default

                new_limits = LIMIT(**limits_dict)
                try:
                    db_session.merge(new_limits)
                    uncommitted_updates += 1
                except Exception as exc:
                    logging.exception("Failed to merge limits for %s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    abort_cycle = True
                    break

            del nova
            if abort_cycle:
                db_session.close()
                time.sleep(config.limit_sleep_interval)
                continue

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Limit updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.error("Failed to commit new limits for %s::%s, aborting cycle..."  % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    abort_cycle = True
                    break

            # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
            _delete_obsolete_items('Limit', inventory, db_session, LIMIT, '-', poll_time=new_poll_time)

            logging.info("Completed limit poller cycle")
            db_session.close()
            time.sleep(config.limit_sleep_interval)

    except Exception as exc:
        logging.exception("Limit poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

def network_poller():
    multiprocessing.current_process().name = "Network Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    NETWORK = Base.classes.cloud_networks
    CLOUD = Base.classes.csv2_group_resources

    try:
        while True:
            logging.info("Beginning network poller cycle")
            db_session = Session(engine)
            # db_session.autoflush = False
            new_poll_time = int(time.time())

            inventory = {}
            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Processing networks from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # Retrieve network list.
                neutron = _get_neutron_client(session)
                try:
                    net_list = neutron.list_networks()['networks']
                except Exception as exc:
                    logging.error("Failed to retrieve networks from neutron, skipping %s::%s" % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    continue

                if net_list is False:
                    logging.info("No networks defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                uncommitted_updates = 0
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

                    ### debugging
                    for hash_item in network_dict:
                        logging.info('>>>>>>>>>>>>>>>> %s, %s, %s, %s' % (cloud.group_name, cloud.cloud_name, hash_item, network_dict[hash_item]))

                    if _inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, network['name'], network_dict, new_poll_time):
                        continue

                    network_dict, unmapped = map_attributes(src="os_networks", dest="csv2", attr_dict=network_dict)
                    if unmapped:
                        logging.error("Unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)

                    new_network = NETWORK(**network_dict)
                    try:
                        db_session.merge(new_network)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge network entry for %s::%s::%s, aborting cycle..." % (cloud.group_name, cloud.cloud_name, network['name']))
                        logging.error(exc)
                        abort_cycle = True
                        break

                del neutron
                if abort_cycle:
                    break

                if uncommitted_updates > 0:
                    try:
                        db_session.commit()
                        logging.info("Network updates committed: %d" % uncommitted_updates)
                    except Exception as exc:
                        logging.error("Failed to commit new networks for %s::%s, aborting cycle..."  % (cloud.group_name, cloud.cloud_name))
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                db_session.close()
                time.sleep(config.network_sleep_interval)
                continue

            # Scan the OpenStack networks in the database, removing each one that was not updated in the inventory.
            _delete_obsolete_items('Network', inventory, db_session, NETWORK, 'name', poll_time=new_poll_time)

            logging.info("Completed network poller cycle")
            db_session.close()
            time.sleep(config.network_sleep_interval)

    except Exception as exc:
        logging.exception("Network poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

# Retrieve VMs.
def vm_poller():
    multiprocessing.current_process().name = "VM Poller"
    Base = automap_base()
    engine = create_engine("mysql://" + config.db_user + ":" + config.db_password + \
        "@" + config.db_host + ":" + str(config.db_port) + "/" + config.db_name)
    Base.prepare(engine, reflect=True)
    VM = Base.classes.csv2_vms
    CLOUD = Base.classes.csv2_group_resources
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
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            for cloud in cloud_list:
                logging.info("Polling VMs from group:cloud -  %s::%s" % (cloud.group_name, cloud.cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    continue

                # setup nova object
                _inventory_group_and_cloud(inventory, cloud.group_name, cloud.cloud_name,)
                nova = _get_nova_client(session)

                # Retrieve VM list for this cloud.
                try:
                    vm_list = nova.servers.list()
                except Exception as exc:
                    logging.error("Failed to retrieve VM data for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    logging.error(exc)
                    continue

                if vm_list is False:
                    logging.info("No VMs defined for %s::%s, skipping this cloud..." % (cloud.group_name, cloud.cloud_name))
                    del nova
                    continue

                # Process VM list for this cloud.
                uncommitted_updates = 0
                for vm in vm_list:
                    vm_update_time = _inventory_item(inventory, cloud.group_name, cloud.cloud_name, vm.name, vm.updated)
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
                    new_vm = VM(**vm_dict)
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
            _delete_obsolete_items('VM', inventory, db_session, VM, 'hostname')

            logging.info("Completed VM poller cycle")
            last_poll_time = new_poll_time
            del inventory
            db_session.close()
            time.sleep(config.vm_sleep_interval)

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        db_session.close()

## Main.

if __name__ == '__main__':

    logging.basicConfig(
        filename=config.poller_log_file,
        level=config.log_level,
        format='%(asctime)s - %(processName)-16s - %(levelname)s - %(message)s')

    logging.info("**************************** starting openstack VM poller *********************************")

    processes = {}
    process_ids = {
        'command':     command_poller,
        'flavor':      flavor_poller,
        'image':       image_poller,
        'keypair':     keypair_poller,
        'limit':       limit_poller,
        'network':     network_poller,
        'vm':          vm_poller,
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
