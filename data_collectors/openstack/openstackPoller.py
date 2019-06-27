import multiprocessing
import logging
import socket
import time
import sys
import os
import datetime
from dateutil import tz
import copy

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor
from cloudscheduler.lib.signal_manager import register_signal_receiver
from cloudscheduler.lib.schema import view_vm_kill_retire_over_quota
from cloudscheduler.lib.view_utils import kill_retire
from cloudscheduler.lib.log_tools import get_frame_info


from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    foreign, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
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

def _get_neutron_client(session, region=None):
    neutron = neuclient.Client(session=session, region_name=region, timeout=10)
    return neutron

def _get_nova_client(session, region=None):
    nova = novaclient.Client("2", session=session, region_name=region, timeout=10)
    return nova

def _get_openstack_session(cloud):
    authsplit = cloud.authurl.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.debug("Bad OpenStack URL, could not determine version, skipping %s", cloud.authurl)
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
            project_domain_name=cloud.project_domain_name,
            project_domain_id=cloud.project_domain_id,)
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

def _get_openstack_session_v1_v2(auth_url, username, password, project, user_domain="Default", project_domain_name="Default",
                                 project_domain_id=None):
    authsplit = auth_url.split('/')
    try:
        version = int(float(authsplit[-1][1:])) if len(authsplit[-1]) > 0 else int(float(authsplit[-2][1:]))
    except ValueError:
        logging.debug("Bad openstack URL: %s, could not determine version, aborting session", auth_url)
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
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,)
            sess = session.Session(auth=auth, verify=config.cacerts)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess


## Poller functions.

def flavor_poller():
    multiprocessing.current_process().name = "Flavor Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)

    FLAVOR = config.db_map.classes.cloud_flavors
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, FLAVOR, 'name', debug_hash=(config.log_level<20), cloud_type="openstack")
        while True:
            try:
                logging.debug("Beginning flavor poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl+cloud.project+cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region]['groups'].append((cloud.group_name, cloud.cloud_name))


                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing flavours from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                            continue

                    # setup OpenStack api objects
                    nova = _get_nova_client(session, region=unique_cloud_dict[cloud]['cloud_obj'].region)

                    # Retrieve all flavours for this cloud.
                    try:
                        flav_list =  nova.flavors.list()
                    except Exception as exc:
                        logging.error("Failed to retrieve flavor data for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if flav_list is False:
                        logging.info("No flavors defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm+cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

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
                                'cloud_type': "openstack",
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
                delete_obsolete_database_items('Flavor', inventory, db_session, FLAVOR, 'name', poll_time=new_poll_time, failure_dict=failure_dict, cloud_type="openstack")

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_flavor)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue

    except Exception as exc:
        logging.exception("Flavor poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def image_poller():
    multiprocessing.current_process().name = "Image Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)

    IMAGE = config.db_map.classes.cloud_images
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, IMAGE, 'id', debug_hash=(config.log_level<20), cloud_type="openstack")
        while True:
            try:
                logging.debug("Beginning image poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl+cloud.project+cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region]['groups'].append((cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing Images from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve all images for this cloud.
                    nova = _get_nova_client(session, region=unique_cloud_dict[cloud]['cloud_obj'].region)
                    try:
                        image_list =  nova.glance.list()
                    except Exception as exc:
                        logging.error("Failed to retrieve image data for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if image_list is False:
                        logging.info("No images defined for %s, skipping this cloud..." %  cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm+cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

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
                delete_obsolete_database_items('Image', inventory, db_session, IMAGE, 'id', failure_dict=failure_dict, cloud_type="openstack")

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_image)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue


    except Exception as exc:
        logging.exception("Image poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

# Retrieve keypairs.
def keypair_poller():
    multiprocessing.current_process().name = "Keypair Poller"
    
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    KEYPAIR = config.db_map.classes.cloud_keypairs
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, KEYPAIR, 'key_name', debug_hash=(config.log_level<20), cloud_type="openstack")
        while True:
            try:    
                logging.debug("Beginning keypair poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl+cloud.project+cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region]['groups'].append((cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing Key pairs from group:cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s" % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # setup openstack api objects
                    nova = _get_nova_client(session, region=unique_cloud_dict[cloud]['cloud_obj'].region)

                    #setup fingerprint list
                    fingerprint_list = []

                    try:
                        # get keypairs and add them to database
                        cloud_keys = nova.keypairs.list()
                    except Exception as exc:
                        logging.error("Failed to poll key pairs from nova, skipping %s" % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm+cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

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
                                'cloud_type': "openstack",
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
                            logging.error("Failed to commit new keypairs for %s, aborting cycle..."  % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_keypair)
                    continue

                # Scan the OpenStack keypairs in the database, removing each one that was not updated in the inventory.
                delete_obsolete_database_items('Keypair', inventory, db_session, KEYPAIR, 'key_name', poll_time=new_poll_time, failure_dict=failure_dict, cloud_type="openstack")

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_keypair)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue

    except Exception as exc:
        logging.exception("Keypair poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session

def limit_poller():
    multiprocessing.current_process().name = "Limit Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    LIMIT = config.db_map.classes.cloud_limits
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, LIMIT, '-', debug_hash=(config.log_level<20), cloud_type="openstack")
        while True:
            try:
                logging.debug("Beginning limit poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                uncommitted_updates = 0

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl+cloud.project+cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region]['groups'].append((cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing limits from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve limit list for the current cloud.
                    nova = _get_nova_client(session, region=unique_cloud_dict[cloud]['cloud_obj'].region)

                    shared_limits_dict = {}
                    try:
                        limit_list = nova.limits.get().absolute
                        for limit in limit_list:
                            shared_limits_dict[limit.name] = [limit.value]
                    except Exception as exc:
                        logging.error("Failed to retrieve limits from nova, skipping %s" %  cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if shared_limits_dict is False:
                        logging.info("No limits defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm+cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    # Process limit list for the current cloud.
                    for groups in unique_cloud_dict[cloud]['groups']:
                        limits_dict = copy.deepcopy(shared_limits_dict)
                        group_n = groups[0]
                        cloud_n = groups[1]

                        limits_dict['group_name'] = group_n
                        limits_dict['cloud_name'] = cloud_n
                        limits_dict['last_updated'] = int(time.time())
                        limits_dict, unmapped = map_attributes(src="os_limits", dest="csv2", attr_dict=limits_dict)
                        if unmapped:
                            logging.error("Unmapped attributes found during mapping, discarding:")
                            logging.error(unmapped)

                        if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, '-', limits_dict, new_poll_time, debug_hash=(config.log_level<20)):
                            continue

                        for limit in limits_dict:
                            if "-1" in str(limits_dict[limit]):
                                limits_dict[limit] = config.no_limit_default
                        limits_dict["cloud_type"] = "openstack"

                        new_limits = LIMIT(**limits_dict)
                        try:
                            db_session.merge(new_limits)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge limits for %s::%s, aborting cycle..." % (group_n, cloud_n))
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
                            logging.error("Failed to commit new limits for %s, aborting cycle..."  % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
                delete_obsolete_database_items('Limit', inventory, db_session, LIMIT, '-', poll_time=new_poll_time, failure_dict=failure_dict, cloud_type="openstack")

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_limit)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue

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
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    NETWORK = config.db_map.classes.cloud_networks
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, NETWORK, 'name', debug_hash=(config.log_level<20), cloud_type="openstack")
        while True:
            try:
                logging.debug("Beginning network poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl+cloud.project+cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region]['groups'].append((cloud.group_name, cloud.cloud_name))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing networks from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve network list.
                    neutron = _get_neutron_client(session, region=unique_cloud_dict[cloud]['cloud_obj'].region)
                    try:
                        net_list = neutron.list_networks()['networks']
                    except Exception as exc:
                        logging.error("Failed to retrieve networks from neutron, skipping %s" %  cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if net_list is False:
                        logging.info("No networks defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm+cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    uncommitted_updates = 0
                    for network in net_list:
                        for groups in unique_cloud_dict[cloud]['groups']:
                            group_n = groups[0]
                            cloud_n = groups[1]
                            network_dict = {
                                'group_name': group_n,
                                'cloud_name': cloud_n,
                                'name': network['name'],
                                'cloud_type': "openstack",
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

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, network['name'], network_dict, new_poll_time, debug_hash=(config.log_level<20)):
                                continue

                            new_network = NETWORK(**network_dict)
                            try:
                                db_session.merge(new_network)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception("Failed to merge network entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, network['name']))
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
                            logging.error("Failed to commit new networks for %s, aborting cycle..." %  cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    config.db_close()
                    del db_session
                    time.sleep(config.sleep_interval_network)
                    continue

                # Scan the OpenStack networks in the database, removing each one that was not updated in the inventory.
                delete_obsolete_database_items('Network', inventory, db_session, NETWORK, 'name', poll_time=new_poll_time, failure_dict=failure_dict, cloud_type="openstack")

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_network)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                    continue

    except Exception as exc:
        logging.exception("Network poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session


def security_group_poller():
    multiprocessing.current_process().name = "Security Group Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)

    SECURITY_GROUP = config.db_map.classes.cloud_security_groups
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}
    my_pid = os.getpid()

    register_signal_receiver(config, "insert_csv2_clouds")
    register_signal_receiver(config, "update_csv2_clouds")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, SECURITY_GROUP, 'id', debug_hash=(config.log_level<20), cloud_type="openstack")
        while True:
            try:
                logging.debug("Beginning security group poller cycle")
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.db_open()
                db_session = config.db_session

                abort_cycle = False
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud.authurl+cloud.project+cloud.region not in unique_cloud_dict:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud.group_name, cloud.cloud_name)]
                        }
                    else:
                        unique_cloud_dict[cloud.authurl+cloud.project+cloud.region]['groups'].append((cloud.group_name, cloud.cloud_name))


                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing security groups from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                            continue

                    # setup OpenStack api objects
                    neu = _get_neutron_client(session, region=unique_cloud_dict[cloud]['cloud_obj'].region)

                    # Retrieve all flavours for this cloud.
                    try:
                        sec_grp_list =  neu.list_security_groups()
                    except Exception as exc:
                        logging.error("Failed to retrieve security groups for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if grp_nm+cld_nm not in failure_dict:
                                failure_dict[grp_nm+cld_nm] = 1
                            else:
                                failure_dict[grp_nm+cld_nm] = failure_dict[grp_nm+cld_nm] + 1
                            if failure_dict[grp_nm+cld_nm] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if sec_grp_list is False:
                        logging.info("No security groups defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(grp_nm+cld_nm, None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    # Process security groups for this cloud.
                    uncommitted_updates = 0
                    for sec_grp in sec_grp_list["security_groups"]:
                        for groups in unique_cloud_dict[cloud]['groups']:
                            group_n = groups[0]
                            cloud_n = groups[1]

                            sec_grp_dict = {
                                'group_name': group_n,
                                'cloud_name': cloud_n,
                                'name': sec_grp["name"],
                                'cloud_type': "openstack",
                                'id': sec_grp["id"],
                                'last_updated': new_poll_time
                                }

                            flav_dict, unmapped = map_attributes(src="os_sec_grps", dest="csv2", attr_dict=sec_grp_dict)
                            if unmapped:
                                logging.error("Unmapped attributes found during mapping, discarding:")
                                logging.error(unmapped)

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, sec_grp["id"], sec_grp_dict, new_poll_time, debug_hash=(config.log_level<20)):
                                continue

                            new_sec_grp = SECURITY_GROUP(**sec_grp_dict)
                            try:
                                db_session.merge(new_sec_grp)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception("Failed to merge security group entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, sec_grp.name))
                                logging.error(exc)
                                abort_cycle = True
                                break

                    del neu
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        try:        
                            db_session.commit()
                            logging.info("Security group updates committed: %d" % uncommitted_updates)
                        except Exception as exc:
                            logging.exception("Failed to commit security group updates for %s, aborting cycle..." % cloud_name)
                            logging.error(exc)
                            abort_cycle = True
                            break

                if abort_cycle:
                    db_session.close()
                    time.sleep(config.sleep_interval_sec_grp)
                    continue

                # Scan the OpenStack sec_grps in the database, removing each one that was not iupdated in the inventory.
                delete_obsolete_database_items('sec_grp', inventory, db_session, SECURITY_GROUP, 'id', poll_time=new_poll_time, failure_dict=failure_dict, cloud_type="openstack")

                config.db_close()
                del db_session
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_security_group)

                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue

            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                continue

    except Exception as exc:
        logging.exception("sec_grp poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session



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
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), "SQL"], pool_size=8)
    VM = config.db_map.classes.csv2_vms
    FVM = config.db_map.classes.csv2_vms_foreign
    GROUP = config.db_map.classes.csv2_groups
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}
    
    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, VM, 'hostname', debug_hash=(config.log_level<20), cloud_type="openstack")
        while True:
            # This cycle should be reasonably fast such that the scheduler will always have the most
            # up to date data during a given execution cycle.
            logging.debug("Beginning VM poller cycle")
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.db_open()
            db_session = config.db_session

            # For each OpenStack cloud, retrieve and process VMs.
            abort_cycle = False
            group_list = db_session.query(GROUP)

            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")

            # build unique cloud list to only query a given cloud once per cycle
            unique_cloud_dict = {}
            for cloud in cloud_list:
                if cloud.authurl+cloud.project+cloud.region not in unique_cloud_dict:
                    unique_cloud_dict[cloud.authurl+cloud.project+cloud.region] = {
                        'cloud_obj': cloud,
                        'groups': [(cloud.group_name, cloud.cloud_name)]
                    }
                else:
                    unique_cloud_dict[cloud.authurl+cloud.project+cloud.region]['groups'].append((cloud.group_name, cloud.cloud_name))

            group_list = []
            for cloud in unique_cloud_dict:
                group_list = group_list +unique_cloud_dict[cloud]['groups']

            for cloud in unique_cloud_dict:
                auth_url = unique_cloud_dict[cloud]['cloud_obj'].authurl
                cloud_obj = unique_cloud_dict[cloud]['cloud_obj']

                foreign_vm_list = db_session.query(FVM).filter(FVM.authurl == cloud_obj.authurl, FVM.region == cloud_obj.region, FVM.project == cloud_obj.project)

                #set foreign vm counts to zero as we will recalculate them as we go, any rows left at zero should be deleted
                # dict[cloud+flavor]
                for_vm_dict = {}
                for for_vm in foreign_vm_list:
                    fvm_dict = {
                        "fvm_obj": for_vm,
                        "count": 0,
                        "region": cloud_obj.region,
                        "authurl": cloud_obj.authurl,
                        "project": cloud_obj.project
                    }
                    for_vm_dict[auth_url + "--" + for_vm.flavor_id] = fvm_dict

                logging.debug("Polling VMs from cloud: %s" % auth_url)
                session = _get_openstack_session(cloud_obj)

                if session is False:
                    logging.debug("Failed to establish session with %s::%s::%s, using group %s's credentials skipping this cloud..." % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region, cloud_obj.group_name))
                    if cloud_obj.group_name+auth_url not in failure_dict:
                        failure_dict[cloud_obj.group_name+auth_url] = 1
                    else:
                        failure_dict[cloud_obj.group_name+auth_url] = failure_dict[cloud_obj.group_name+auth_url] + 1
                    if failure_dict[cloud_obj.group_name+auth_url] > 3: #could be configurable
                        logging.error("Failure threshhold limit reached for %s::%s::%s, using group %s's credentials, manual action required, skipping" % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region, cloud_obj.group_name))
                    continue

                # Retrieve VM list for this cloud.
                nova = _get_nova_client(session, region=cloud_obj.region)
                try:
                    vm_list = nova.servers.list()
                except Exception as exc:
                    logging.error("Failed to retrieve VM data for  %s::%s::%s, skipping this cloud..." % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region))
                    logging.error("Exception type: %s" % type(exc))
                    logging.error(exc)
                    if cloud_obj.group_name+auth_url not in failure_dict:
                        failure_dict[cloud_obj.group_name+auth_url] = 1
                    else:
                        failure_dict[cloud_obj.group_name+auth_url] = failure_dict[cloud_obj.group_name+auth_url] + 1
                    if failure_dict[cloud_obj.group_name+auth_url] > 3: #should be configurable
                        logging.error("Failure threshhold limit reached for %s::%s::%s, using group %s's crednetials manual action required, skipping" % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region, cloud_obj.group_name))
                    continue

                if vm_list is False:
                    logging.info("No VMs defined for %s::%s:%s, skipping this cloud..." % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region))
                    del nova
                    continue

                # if we get here the connection to openstack has been succussful and we can remove the error status
                failure_dict.pop(cloud_obj.group_name+auth_url, None)

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
                        vm_group_name = host_tokens[0]
                        vm_cloud_name = host_tokens[1]
                        

                        if (host_tokens[0], host_tokens[1]) not in group_list:
                            logging.debug("Group-Cloud combination doesn't match any in csv2, marking %s as foreign vm" % vm.name)
                            logging.debug(group_list)
                            if auth_url + "--" + vm.flavor["id"] in for_vm_dict:
                                for_vm_dict[auth_url + "--" + vm.flavor["id"]]["count"] = for_vm_dict[auth_url + "--" + vm.flavor["id"]]["count"] + 1
                            else:
                                # no entry yet
                                for_vm_dict[auth_url + "--" + vm.flavor["id"]]= {
                                    'count': 1,
                                    'region': cloud_obj.region,
                                    'project': cloud_obj.project,
                                    'authurl': cloud_obj.authurl, 
                                    'flavor_id': vm.flavor["id"]
                                }
                            continue
                        elif int(host_tokens[2]) != int(config.csv2_host_id):
                            logging.debug("csv2 host id from host does not match (should be %s), marking %s as foreign vm" % (config.csv2_host_id, vm.name))
                            if auth_url + "--" + vm.flavor["id"] in for_vm_dict:
                                for_vm_dict[auth_url + "--" + vm.flavor["id"]]["count"] = for_vm_dict[auth_url + "--" + vm.flavor["id"]]["count"] + 1
                            else:
                                # no entry yet
                                for_vm_dict[auth_url + "--" + vm.flavor["id"]]= {
                                    'count': 1,
                                    'region': cloud_obj.region,
                                    'project': cloud_obj.project,
                                    'authurl': cloud_obj.authurl, 
                                    'flavor_id': vm.flavor["id"]
                                }

                            #foreign vm
                            continue
                    except IndexError as exc:
                        #not enough tokens, bad hostname or foreign vm
                        logging.debug("Not enough tokens from hostname, bad hostname or foreign vm: %s" % vm.name)
                        if auth_url + "--" + vm.flavor["id"] in for_vm_dict:
                            for_vm_dict[auth_url + "--" + vm.flavor["id"]]["count"] = for_vm_dict[auth_url + "--" + vm.flavor["id"]]["count"] + 1
                        else:
                            # no entry yet
                            for_vm_dict[auth_url + "--" + vm.flavor["id"]]= {
                                'count': 1,
                                'region': cloud_obj.region,
                                'project': cloud_obj.project,
                                'authurl': cloud_obj.authurl, 
                                'flavor_id': vm.flavor["id"]
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
                    vm_dict = {
                        'group_name': vm_group_name,
                        'cloud_name': vm_cloud_name,
                        "region": cloud_obj.region,
                        'auth_url': cloud_obj.authurl,
                        'project': cloud_obj.project,
                        'cloud_type': "openstack",
                        'hostname': vm.name,
                        'vmid': vm.id,
                        'status': vm.status,
                        'flavor_id': vm.flavor["id"],
                        'task': vm.__dict__.get("OS-EXT-STS:task_state"),
                        'power_state': vm.__dict__.get("OS-EXT-STS:power_state"),
                        'vm_ips': str(ip_addrs),
                        'vm_floating_ips': str(floating_ips),
                        'last_updated': new_poll_time
                    }

                    vm_dict, unmapped = map_attributes(src="os_vms", dest="csv2", attr_dict=vm_dict)
                    if unmapped:
                        logging.error("unmapped attributes found during mapping, discarding:")
                        logging.error(unmapped)

                    if test_and_set_inventory_item_hash(inventory, vm_group_name, vm_cloud_name, vm.name, vm_dict, new_poll_time, debug_hash=(config.log_level<20)):
                        continue

                    new_vm = VM(**vm_dict)
                    try:
                        db_session.merge(new_vm)
                        uncommitted_updates += 1
                    except Exception as exc:
                        logging.exception("Failed to merge VM entry for %s::%s::%s, using group %s's credentials aborting cycle..." % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region, cloud_obj.group_name))
                        logging.error(exc)
                        abort_cycle = True
                        break
                    if uncommitted_updates >= config.batch_commit_size:
                        try:
                            db_session.commit()
                            logging.debug("Comitted %s VMs" % uncommitted_updates)
                            uncommitted_updates = 0
                        except Exception as exc:
                            logging.error("Error during batch commit of VMs:")
                            logging.error(exc)

                del nova
                if abort_cycle:
                    break

                if uncommitted_updates > 0:
                    try:        
                        db_session.commit()
                        logging.info("VM updates committed: %d" % uncommitted_updates)
                    except Exception as exc:
                        logging.exception("Failed to commit VM updates for %s::%s:%s, using group %s's credentials aborting cycle..." % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region, cloud_obj.group_name))
                        logging.error(exc)
                        abort_cycle = True
                        break
                if abort_cycle:
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
                                'authurl':    for_vm_dict[key]['authurl'],
                                'project':    for_vm_dict[key]['project'],
                                'region':     for_vm_dict[key]['region'],
                                'flavor_id':  for_vm_dict[key]['flavor_id'],
                                'count':      for_vm_dict[key]['count'],
                                'cloud_type': "openstack"
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
            # VMs have a different failure dict schema using group_name + auth_url instead of group_name + cloud_name
            #     failure_dict needs to be remapped before calling
            logging.debug("Expanding failure_dict: %s" % failure_dict)
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            new_f_dict = {}
            for cloud in cloud_list:
                key = cloud.group_name + cloud.authurl
                if key in failure_dict:
                    new_f_dict[cloud.group_name+cloud.cloud_name] = 1
            delete_obsolete_database_items('VM', inventory, db_session, VM, 'hostname', new_poll_time, failure_dict=new_f_dict, cloud_type="openstack")


            # Check on the core limits to see if any clouds need to be scaled down.
            logging.debug("checking for over-quota clouds")
            over_quota_clouds = db_session.query(view_vm_kill_retire_over_quota).filter(view_vm_kill_retire_over_quota.c.cloud_type=="openstack")
            for cloud in over_quota_clouds:
                kill_retire(config, cloud.group_name, cloud.cloud_name, "control", [cloud.cores, cloud.ram], get_frame_info())


            logging.debug("Completed VM poller cycle")
            config.db_close()
            del db_session
            wait_cycle(cycle_start_time, poll_time_history, config.sleep_interval_vm)

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()
        del db_session


def service_registrar():
    multiprocessing.current_process().name = "Service Registrar"

    # database setup
    db_category_list = [os.path.basename(sys.argv[0]), "general"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=8)
    SERVICE_CATALOG = config.db_map.classes.csv2_service_catalog

    service_fqdn = socket.gethostname()
    service_name = "csv2-openstack"

    while True:
        config.db_open()

        service_dict = {
            "service":             service_name,
            "fqdn":                service_fqdn,
            "last_updated":        None,
            "yaml_attribute_name": "cs_condor_remote_openstack_poller"
        }
        service = SERVICE_CATALOG(**service_dict)
        try:
            config.db_session.merge(service)
            config.db_close(commit=True)
        except Exception as exc:
            logging.exception("Failed to merge service catalog entry, aborting...")
            logging.error(exc)
            return -1

        time.sleep(config.sleep_interval_registrar)

    return -1

## Main.

if __name__ == '__main__':
    process_ids = {
        'flavor':                flavor_poller,
        'image':                 image_poller,
        'keypair':               keypair_poller,
        'limit':                 limit_poller,
        'network':               network_poller,
        'vm':                    vm_poller,
        'registrar':             service_registrar,
        'security_group_poller': security_group_poller
    }
    db_categories = [os.path.basename(sys.argv[0]), "general", "signal_manager"]

    procMon = ProcessMonitor(config_params=db_categories, pool_size=9, orange_count_row='csv2_openstack_error_count', process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    logging.info("**************************** starting openstack VM poller - Running %s *********************************" % version)


    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        while True:
            procMon.check_processes()
            time.sleep(config.sleep_interval_main_long)

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()
