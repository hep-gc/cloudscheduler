import multiprocessing
from multiprocessing import Process
import logging
import socket
import time
import sys
import os
import datetime

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    foreign, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    set_orange_count, \
    start_cycle, \
    wait_cycle
#   get_last_poll_time_from_database, \
#   set_inventory_group_and_cloud, \
#   set_inventory_item, \

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql import func

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient
from neutronclient.v2_0 import client as neuclient
from cinderclient import client as cinclient

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

def _get_neutron_client(session):
    neutron = neuclient.Client(session=session)
    return neutron

def _get_nova_client(session):
    nova = novaclient.Client("2", session=session, timeout=10)
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
            sess = session.Session(auth=auth, verify=config.cacerts)
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
            sess = session.Session(auth=auth, verify=config.cacerts)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess

## Poller functions.

# Process VM commands.
def command_poller():
    multiprocessing.current_process().name = "VM Commands"
    last_poll_time = 0
    vm_poller_id = "vm_poller_" + str(socket.getfqdn())

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    VM = config.db_map.classes.csv2_vms
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        while True:
            logging.info("Beginning command poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session
            
            # Retrieve list of VMs to be terminated.
            vm_to_destroy = db_session.query(VM).filter(VM.terminate == 1, VM.manual_control != 1)
            for vm in vm_to_destroy:
                if foreign(vm):
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
                    logging.info("VM Terminated: %s, updating db entry", (vm.hostname,))
                    vm.terminate = 2
                    db_session.merge(vm)
                except Exception as exc:
                    logging.exception("Failed to terminate VM: %s", vm.hostname)
                    logging.error(exc)

            last_poll_time = new_poll_time
            config.db_close(commit=True) # may need to batch these commits if we are attempting to terminate a lot of vms at once or the database sesion will time out
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_command)

    except Exception as exc:
        logging.exception("Command poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def flavor_poller():
    multiprocessing.current_process().name = "Flavor Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    FLAVOR = config.db_map.classes.cloud_flavors
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, FLAVOR, 'name', debug_hash=(config.log_level<20))
        while True:
            logging.info("Beginning flavor poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")

            # build unique cloud list to only query a given cloud once per cycle
            unique_cloud_dict = {}
            for cloud in cloud_list:
                if cloud.authurl+cloud.project not in unique_cloud_dict:
                    unique_cloud_dict[cloud.authurl+cloud.project] = {
                        'cloud_obj': cloud,
                        'groups': [(cloud.group_name, cloud.cloud_name)]
                    }
                else:
                    unique_cloud_dict[cloud.authurl+cloud.project]['groups'].append((cloud.group_name, cloud.cloud_name))


            for cloud in unique_cloud_dict:
                cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                logging.info("Processing flavours from cloud - %s" % cloud_name)
                session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                if session is False:
                    logging.error("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                    continue

                # setup OpenStack api objects
                nova = _get_nova_client(session)

                # Retrieve all flavours for this cloud.
                try:
                    flav_list =  nova.flavors.list()
                except Exception as exc:
                    logging.error("Failed to retrieve flavor data for %s, skipping this cloud..." % cloud_name)
                    logging.error(exc)
                    continue

                if flav_list is False:
                    logging.info("No flavors defined for %s::%s, skipping this cloud..." % cloud_name)
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

                    for groups in unique_cloud_dict[cloud]['groups']:
                        group_n = groups[0]
                        cloud_n = groups[1]

                        flav_dict = {
                            'group_name': group_n,
                            'cloud_name': cloud_n,
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

                        if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, flavor.name, flav_dict, new_poll_time, debug_hash=(config.log_level<20)):
                            continue

                        new_flav = FLAVOR(**flav_dict)
                        try:
                            db_session.merge(new_flav)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge flavor entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, flavor.name))
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
                        logging.exception("Failed to commit flavor updates for %s, aborting cycle..." % cloud_name)
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                db_session.close()
                time.sleep(config.sleep_interval_flavor)
                continue

            # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
            delete_obsolete_database_items('Flavor', inventory, db_session, FLAVOR, 'name', poll_time=new_poll_time)

            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_flavor)

    except Exception as exc:
        logging.exception("Flavor poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def image_poller():
    multiprocessing.current_process().name = "Image Poller"
    #Base = automap_base()
    #db_engine = create_engine(
    #    'mysql://%s:%s@%s:%s/%s' % (
    #        config.db_user,
    #        config.db_password,
    #        config.db_host,
    #        str(config.db_port),
    #        config.db_name
    #        )
    #    )
    #Base.prepare(db_engine, reflect=True)
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    IMAGE = config.db_map.classes.cloud_images
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, IMAGE, 'id', debug_hash=(config.log_level<20))
        while True:
            logging.info("Beginning image poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")

            # build unique cloud list to only query a given cloud once per cycle
            unique_cloud_dict = {}
            for cloud in cloud_list:
                if cloud.authurl+cloud.project not in unique_cloud_dict:
                    unique_cloud_dict[cloud.authurl+cloud.project] = {
                        'cloud_obj': cloud,
                        'groups': [(cloud.group_name, cloud.cloud_name)]
                    }
                else:
                    unique_cloud_dict[cloud.authurl+cloud.project]['groups'].append((cloud.group_name, cloud.cloud_name))

            for cloud in unique_cloud_dict:
                cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                logging.info("Processing Images from cloud - %s" % cloud_name)
                session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                if session is False:
                    logging.error("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                    continue

                # Retrieve all images for this cloud.
                nova = _get_nova_client(session)
                try:
                    image_list =  nova.glance.list()
                except Exception as exc:
                    logging.error("Failed to retrieve image data for %s, skipping this cloud..." % cloud_name)
                    logging.error(exc)
                    continue

                if image_list is False:
                    logging.info("No images defined for %s, skipping this cloud..." %  cloud_name)
                    continue

                uncommitted_updates = 0
                for image in image_list:
                    if image.size == "":
                        size = 0
                    else:
                        size = image.size

                    for groups in unique_cloud_dict[cloud]['groups']:
                        group_n = groups[0]
                        cloud_n = groups[1]

                        img_dict = {
                            'group_name': group_n,
                            'cloud_name': cloud_n,
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

                        if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, image.id, img_dict, new_poll_time, debug_hash=(config.log_level<20)):
                            continue

                        new_image = IMAGE(**img_dict)
                        try:
                            db_session.merge(new_image)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge image entry for %s::%s::%s:" % (group_n, cloud_n, image.name))
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
                        logging.exception("Failed to commit image updates for %s, aborting cycle..." % cloud_name)
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_image)
                continue

            # Scan the OpenStack images in the database, removing each one that is not in the inventory.
            delete_obsolete_database_items('Image', inventory, db_session, IMAGE, 'id')

            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_image)


    except Exception as exc:
        logging.exception("Image poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

# Retrieve keypairs.
def keypair_poller():
    multiprocessing.current_process().name = "Keypair Poller"
    #Base = automap_base()
    #db_engine = create_engine(
    #    'mysql://%s:%s@%s:%s/%s' % (
    #        config.db_user,
    #        config.db_password,
    #        config.db_host,
    #        str(config.db_port),
    #        config.db_name
    #        )
    #    )
    #Base.prepare(db_engine, reflect=True)
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))
    KEYPAIR = config.db_map.classes.cloud_keypairs
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, KEYPAIR, 'key_name', debug_hash=(config.log_level<20))
        while True:
            logging.info("Beginning keypair poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            # build unique cloud list to only query a given cloud once per cycle
            unique_cloud_dict = {}
            for cloud in cloud_list:
                if cloud.authurl+cloud.project not in unique_cloud_dict:
                    unique_cloud_dict[cloud.authurl+cloud.project] = {
                        'cloud_obj': cloud,
                        'groups': [(cloud.group_name, cloud.cloud_name)]
                    }
                else:
                    unique_cloud_dict[cloud.authurl+cloud.project]['groups'].append((cloud.group_name, cloud.cloud_name))

            for cloud in unique_cloud_dict:
                cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                logging.info("Processing Key pairs from group:cloud - %s" % cloud_name)
                session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                if session is False:
                    logging.error("Failed to establish session with %s" % cloud_name)
                    continue

                # setup openstack api objects
                nova = _get_nova_client(session)

                #setup fingerprint list
                fingerprint_list = []

                try:
                    # get keypairs and add them to database
                    cloud_keys = nova.keypairs.list()
                except Exception as exc:
                    logging.error("Failed to poll key pairs from nova, skipping %s" % cloud_name)
                    logging.error(exc)
                    continue

                uncommitted_updates = 0
                for key in cloud_keys:
                    fingerprint_list.append(key.fingerprint)
                    for groups in unique_cloud_dict[cloud]['groups']:
                        group_n = groups[0]
                        cloud_n = groups[1]
                        key_dict = {
                            "cloud_name":  cloud_n,
                            "group_name":  group_n,
                            "key_name":    key.name,
                            "fingerprint": key.fingerprint
                        }
                        

                        if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, key.name, key_dict, new_poll_time, debug_hash=(config.log_level<20)):
                            continue

                        new_key = KEYPAIR(**key_dict)
                        try:
                            db_session.merge(new_key)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge keypair entry for %s::%s, aborting cycle..." % (cloud_n, key.name))
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
                        logging.error("Failed to commit new keypairs for %s::%s, aborting cycle..."  % cloud_name)
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_keypair)
                continue

            # Scan the OpenStack keypairs in the database, removing each one that was not updated in the inventory.
            delete_obsolete_database_items('Keypair', inventory, db_session, KEYPAIR, 'key_name', poll_time=new_poll_time)

            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_keypair)

    except Exception as exc:
        logging.exception("Keypair poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def limit_poller():
    multiprocessing.current_process().name = "Limit Poller"
    Base = automap_base()
    #db_engine = create_engine(
    #    'mysql://%s:%s@%s:%s/%s' % (
    #        config.db_user,
    #        config.db_password,
    #        config.db_host,
    #        str(config.db_port),
    #        config.db_name
    #        )
    #    )
    #Base.prepare(db_engine, reflect=True)
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))
    LIMIT = config.db_map.classes.cloud_limits
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, LIMIT, '-', debug_hash=(config.log_level<20))
        while True:
            logging.info("Beginning limit poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            uncommitted_updates = 0
            for cloud in cloud_list:
                group_name = cloud.group_name
                cloud_name = cloud.cloud_name
                logging.info("Processing Limits from group:cloud -  %s::%s" % (group_name, cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (group_name, cloud_name))
                    continue

                # Retrieve limit list for the current cloud.
                nova = _get_nova_client(session)

                limits_dict = {}
                try:
                    limit_list = nova.limits.get().absolute
                    for limit in limit_list:
                        limits_dict[limit.name] = [limit.value]
                except Exception as exc:
                    logging.error("Failed to retrieve limits from nova, skipping %s::%s" % (group_name, cloud_name))
                    logging.error(exc)
                    continue

                if limits_dict is False:
                    logging.info("No limits defined for %s::%s, skipping this cloud..." % (group_name, cloud_name))
                    continue

                # Process limit list for the current cloud.
                limits_dict['group_name'] = cloud.group_name
                limits_dict['cloud_name'] = cloud.cloud_name
                limits_dict['last_updated'] = int(time.time())
                limits_dict, unmapped = map_attributes(src="os_limits", dest="csv2", attr_dict=limits_dict)
                if unmapped:
                    logging.error("Unmapped attributes found during mapping, discarding:")
                    logging.error(unmapped)

                if test_and_set_inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, '-', limits_dict, new_poll_time, debug_hash=(config.log_level<20)):
                    continue

                for limit in limits_dict:
                    if "-1" in str(limits_dict[limit]):
                        limits_dict[limit] = config.no_limit_default

                new_limits = LIMIT(**limits_dict)
                try:
                    db_session.merge(new_limits)
                    uncommitted_updates += 1
                except Exception as exc:
                    logging.exception("Failed to merge limits for %s::%s, aborting cycle..." % (group_name, cloud_name))
                    logging.error(exc)
                    abort_cycle = True
                    break

            del nova
            if abort_cycle:
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_limit)
                continue

            if uncommitted_updates > 0:
                try:
                    db_session.commit()
                    logging.info("Limit updates committed: %d" % uncommitted_updates)
                except Exception as exc:
                    logging.error("Failed to commit new limits for %s::%s, aborting cycle..."  % (group_name, cloud_name))
                    logging.error(exc)
                    abort_cycle = True
                    break

            # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
            delete_obsolete_database_items('Limit', inventory, db_session, LIMIT, '-', poll_time=new_poll_time)

            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_limit)

    except Exception as exc:
        logging.exception("Limit poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def network_poller():
    multiprocessing.current_process().name = "Network Poller"
    #Base = automap_base()
    #db_engine = create_engine(
    #    'mysql://%s:%s@%s:%s/%s' % (
    #        config.db_user,
    #        config.db_password,
    #        config.db_host,
    #        str(config.db_port),
    #        config.db_name
    #        )
    #    )
    #Base.prepare(db_engine, reflect=True)
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))
    NETWORK = config.db_map.classes.cloud_networks
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, NETWORK, 'name', debug_hash=(config.log_level<20))
        while True:
            logging.info("Beginning network poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            abort_cycle = False
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            for cloud in cloud_list:
                group_name = cloud.group_name
                cloud_name = cloud.cloud_name
                logging.info("Processing networks from group:cloud -  %s::%s" % (group_name, cloud_name))
                session = _get_openstack_session(cloud)
                if session is False:
                    logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (group_name, cloud_name))
                    continue

                # Retrieve network list.
                neutron = _get_neutron_client(session)
                try:
                    net_list = neutron.list_networks()['networks']
                except Exception as exc:
                    logging.error("Failed to retrieve networks from neutron, skipping %s::%s" % (group_name, cloud_name))
                    logging.error(exc)
                    continue

                if net_list is False:
                    logging.info("No networks defined for %s::%s, skipping this cloud..." % (group_name, cloud_name))
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

                    network_dict, unmapped = map_attributes(src="os_networks", dest="csv2", attr_dict=network_dict)
                    if unmapped:
                        logging.error("Unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)

                    if test_and_set_inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, network['name'], network_dict, new_poll_time, debug_hash=(config.log_level<20)):
                        continue

                    new_network = NETWORK(**network_dict)
                    try:
                        db_session.merge(new_network)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge network entry for %s::%s::%s, aborting cycle..." % (group_name, cloud_name, network['name']))
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
                        logging.error("Failed to commit new networks for %s::%s, aborting cycle..."  % (group_name, cloud_name))
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_network)
                continue

            # Scan the OpenStack networks in the database, removing each one that was not updated in the inventory.
            delete_obsolete_database_items('Network', inventory, db_session, NETWORK, 'name', poll_time=new_poll_time)

            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_network)

    except Exception as exc:
        logging.exception("Network poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

# Retrieve VMs.
def vm_poller():
    multiprocessing.current_process().name = "VM Poller"
    #Base = automap_base()
    #db_engine = create_engine(
    #    'mysql://%s:%s@%s:%s/%s' % (
    #        config.db_user,
    #        config.db_password,
    #        config.db_host,
    #        str(config.db_port),
    #        config.db_name
    #        )
    #    )
    #Base.prepare(db_engine, reflect=True)
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))
    VM = config.db_map.classes.csv2_vms
    FVM = config.db_map.classes.csv2_vms_foreign
    GROUP = config.db_map.classes.csv2_groups
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}
    
    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, VM, 'hostname', debug_hash=(config.log_level<20))
        while True:
            # This cycle should be reasonably fast such that the scheduler will always have the most
            # up to date data during a given execution cycle.
            logging.info("Beginning VM poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            # For each OpenStack cloud, retrieve and process VMs.
            abort_cycle = False
            group_list = db_session.query(GROUP)
            for group in group_list:
                logging.debug("Polling Group: %s" % group.group_name)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack", CLOUD.group_name == group.group_name)
                foreign_vm_list = db_session.query(FVM).filter(FVM.group_name == group.group_name)

                #set foreign vm counts to zero as we will recalculate them as we go, any rows left at zero should be deleted
                # dict[cloud+flavor]
                for_vm_dict = {}
                for for_vm in foreign_vm_list:
                    fvm_dict = {
                        "fvm_obj": for_vm,
                        "count": 0,
                    }
                    for_vm_dict[for_vm.cloud_name + "--" + for_vm.flavor_id] = fvm_dict

                for cloud in cloud_list:
                    group_name = group.group_name
                    cloud_name = cloud.cloud_name
                    logging.debug("Polling VMs from cloud: %s" % cloud_name)
                    session = _get_openstack_session(cloud)
                    if session is False:
                        logging.error("Failed to establish session with %s::%s, skipping this cloud..." % (group_name, cloud_name))
                        if group_name + cloud_name not in failure_dict:
                            failure_dict[group_name+cloud_name] = 1
                        else:
                            failure_dict[group_name+cloud_name] = failure_dict[group_name+cloud_name] + 1
                        if failure_dict[group_name+cloud_name] > 3: #should be configurable
                            logging.error("Failure threshhold limit reached for %s::%s, manual action required, exiting" % (group_name, cloud_name))
                            return False
                        continue

                    # Retrieve VM list for this cloud.
                    nova = _get_nova_client(session)
                    try:
                        vm_list = nova.servers.list()
                    except Exception as exc:
                        logging.error("Failed to retrieve VM data for %s::%s, skipping this cloud..." % (group_name, cloud_name))
                        logging.error("Exception type: %s" % type(exc))
                        logging.error(exc)
                        if group_name + cloud_name not in failure_dict:
                            failure_dict[group_name+cloud_name] = 1
                        else:
                            failure_dict[group_name+cloud_name] = failure_dict[group_name+cloud_name] + 1
                        if failure_dict[group_name+cloud_name] > 3: #should be configurable
                            logging.error("Failure threshhold limit reached for %s::%s, manual action required, exiting" % (group_name, cloud_name))
                            return False
                        continue

                    if vm_list is False:
                        logging.info("No VMs defined for %s::%s, skipping this cloud..." % (group_name, cloud_name))
                        del nova
                        continue

                    # if we get here the connection to openstack has been succussful and we can remove the error status
                    failure_dict.pop(group_name+cloud_name, None)

                    # Process VM list for this cloud.
                    # We've decided to remove the variable "status_changed_time" since it was holding the exact same value as "last_updated"
                    # This is because we are only pushing updates to the csv2 database when the state of a vm is changed and thus it would be logically equivalent
                    uncommitted_updates = 0
                    for vm in vm_list:
                    #~~~~~~~~
                    # figure out if it is foreign to this group or not based on tokenized hostname:
                    # hostname example: testing--otter--2049--256153399971170-1
                    # tokenized:        group,   cloud, csv2_host_id, ?vm identifier?
                    #
                    # at the end some of the dictionary enteries might not have a previous database object
                    # due to emergent flavors and thus a new obj will need to be created
                    #~~~~~~~~
                        try:
                            host_tokens = vm.name.split("--")
                            if host_tokens[0] != group_name:
                                logging.debug("group_name from host does not match, marking %s as foreign vm" % vm.name)
                                if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]= {
                                        'count': 1
                                    }
                                #foreign vm
                                continue
                            elif host_tokens[1] != cloud_name:
                                logging.debug("cloud_name from host does not match, marking %s as foreign vm" % vm.name)
                                if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]= {
                                        'count': 1
                                    }
                                #foreign vm
                                continue
                            elif int(host_tokens[2]) != int(config.csv2_host_id):
                                logging.debug("csv2 host id from host does not match (should be %s), marking %s as foreign vm" % (config.csv2_host_id, vm.name))
                                if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[cloud_name + "--" + vm.flavor["id"]]= {
                                        'count': 1
                                    }

                                #foreign vm
                                continue
                        except IndexError as exc:
                            #not enough tokens, bad hostname or foreign vm
                            logging.error("Not enough tokens from hostname, bad hostname or foreign vm: %s" % vm.name)
                            if cloud_name + "--" + vm.flavor["id"] in for_vm_dict:
                                for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] = for_vm_dict[cloud_name + "--" + vm.flavor["id"]]["count"] + 1
                            else:
                                # no entry yet
                                for_vm_dict[cloud_name + "--" + vm.flavor["id"]]= {
                                    'count': 1
                                }

                            continue

                        ip_addrs = []
                        floating_ips = []
                        for net in vm.addresses:
                            for addr in vm.addresses[net]:
                                if addr['OS-EXT-IPS:type'] == 'fixed':
                                    ip_addrs.append(addr['addr'])
                                elif addr['OS-EXT-IPS:type'] == 'floating':
                                    floating_ips.append(addr['addr'])
                        strt_time = vm.__dict__["OS-SRV-USG:launched_at"]
                        try:
                            dt_strt_time = datetime.datetime.strptime(strt_time, '%Y-%m-%dT%H:%M:%S.%f')
                            vm_start_time = dt_strt_time.strftime('%s')
                        except:
                            logging.info("No start time because VM still booting: %s, %s - setting start time equal to current time." % (type(strt_time), strt_time))
                            vm_start_time = new_poll_time
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
                            'vm_ips': str(ip_addrs),
                            'vm_floating_ips': str(floating_ips),
                            'start_time': vm_start_time,
                            'last_updated': new_poll_time
                        }

                        vm_dict, unmapped = map_attributes(src="os_vms", dest="csv2", attr_dict=vm_dict)
                        if unmapped:
                            logging.error("unmapped attributes found during mapping, discarding:")
                            logging.error(unmapped)

                        if test_and_set_inventory_item_hash(inventory, cloud.group_name, cloud.cloud_name, vm.name, vm_dict, new_poll_time, debug_hash=(config.log_level<20)):
                            continue

                        new_vm = VM(**vm_dict)
                        try:
                            db_session.merge(new_vm)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge VM entry for %s::%s::%s, aborting cycle..." % (group_name, cloud_name, vm.name))
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
                            logging.exception("Failed to commit VM updates for %s::%s, aborting cycle..." % (group_name, cloud_name))
                            logging.error(exc)
                            abort_cycle = True
                            break
                # proccess FVM dict
                # check if any rows have a zero count and delete them, otherwise update with new count
                for key in for_vm_dict:
                    split_key = key.split("--")
                    if for_vm_dict[key]['count'] == 0:
                        # delete this row
                        db_session.delete(for_vm_dict[key]['fvm_obj'])
                    else:
                        try:
                            # if we get here there is at least 1 count of this flavor, though there may not be a database object yet
                            for_vm_dict[key]['fvm_obj'].count = for_vm_dict[key]['count']
                            db_session.merge(for_vm_dict[key]['fvm_obj'])
                        except KeyError:
                            # need to create new db obj for this entry
                            fvm_dict = {
                                'group_name': group.group_name,
                                'cloud_name': split_key[0],
                                'flavor_id':  split_key[1],
                                'count':      for_vm_dict[key]['count']
                            }
                            new_fvm = FVM(**fvm_dict)
                            db_session.merge(new_fvm)
                try:
                    db_session.commit()
                except Exception as exc:
                    logging.exception("Failed to commit foreign VM updates, aborting cycle...")
                    logging.error(exc)
                    abort_cycle = True
                    break


            if abort_cycle:
                config.db_close()
                del db_session
                time.sleep(config.sleep_interval_vm)
                continue

            # Scan the OpenStack VMs in the database, removing each one that is not in the inventory.
            delete_obsolete_database_items('VM', inventory, db_session, VM, 'hostname', new_poll_time, failure_dict)

            logging.info("Completed VM poller cycle")
            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_vm)

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

## Main.

if __name__ == '__main__':
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', os.path.basename(sys.argv[0]))

    logging.basicConfig(
        filename=config.log_file,
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

    previous_count, current_count = set_orange_count(logging, config, 'csv2_openstack_error_count', 1, 0)

    # Wait for keyboard input to exit
    try:
        while True:
            orange = False
            for process in process_ids:
                if process not in processes or not processes[process].is_alive():
                    if process in processes:
                        orange = True
                        logging.error("%s process died, restarting...", process)
                        del(processes[process])
                    else:
                        logging.info("Restarting %s process", process)
                    processes[process] = Process(target=process_ids[process])
                    processes[process].start()
                    time.sleep(config.sleep_interval_main_short)

            if orange:
                previous_count, current_count = set_orange_count(logging, config, 'csv2_openstack_error_count', previous_count, current_count+1)
            else:
                previous_count, current_count = set_orange_count(logging, config, 'csv2_openstack_error_count', previous_count, current_count-1)
               
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    for process in processes:
        try:
            process.join()
        except:
            logging.error("failed to join process %s", process.name)
