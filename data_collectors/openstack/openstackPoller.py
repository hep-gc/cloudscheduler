import multiprocessing
import logging
import socket
import time
import sys
import signal
import os
import datetime
from dateutil import tz
import copy

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, terminate, check_pid
#from cloudscheduler.lib.signal_manager import register_signal_receiver
from cloudscheduler.lib.schema import view_vm_kill_retire_over_quota
from cloudscheduler.lib.view_utils import kill_retire
from cloudscheduler.lib.log_tools import get_frame_info

from glintwebui.glint_utils import get_keypair, transfer_keypair, generate_tx_id, check_cache
from glintwebui.celery_app import tx_request

from cloudscheduler.lib.poller_functions import \
    delete_obsolete_database_items, \
    foreign, \
    get_inventory_item_hash_from_database, \
    test_and_set_inventory_item_hash, \
    start_cycle, \
    wait_cycle, \
    cleanup_inventory
#   get_last_poll_time_from_database, \
#   set_inventory_group_and_cloud, \
#   set_inventory_item, \

from cloudscheduler.lib.signal_functions import event_receiver_registration

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql import func

from keystoneclient.auth.identity import v2, v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from novaclient import client as novaclient
from neutronclient.v2_0 import client as neuclient
from cinderclient import client as cinclient
import glanceclient
import openstack



'''

#Below is an attempt to reduce the log output of the openstack api calls but even all this seems to supress everything

#openstack.enable_logging(
#    debug=False, path='/tmp/openstack.log', stream=sys.stdout)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Configure the default behavior of all keystoneauth logging to log at the
# INFO level.
logger = logging.getLogger('keystoneauth')
logger.setLevel(logging.INFO)

# Emit INFO messages from all keystoneauth loggers to stdout
logger.addHandler(stream_handler)

# Create an output formatter that includes logger name and timestamp.
formatter = logging.Formatter('%(asctime)s %(name)s %(message)s')

# Create a file output for request ids and response headers
request_handler = logging.FileHandler('/tmp/openstack.log')
request_handler.setFormatter(formatter)

# Create a file output for request commands, response headers and bodies
body_handler = logging.FileHandler('/tmp/openstack.log')
body_handler.setFormatter(formatter)

# Log all HTTP interactions at the DEBUG level
session_logger = logging.getLogger('keystoneauth.session')
session_logger.setLevel(logging.DEBUG)

# Emit request ids to the request log
request_id_logger = logging.getLogger('keystoneauth.session.request-id')
request_id_logger.addHandler(request_handler)

# Emit response headers to both the request log and the body log
header_logger = logging.getLogger('keystoneauth.session.response')
header_logger.addHandler(request_handler)
header_logger.addHandler(body_handler)

# Emit request commands to the body log
request_logger = logging.getLogger('keystoneauth.session.request')
request_logger.addHandler(body_handler)

# Emit bodies only to the body log
body_logger = logging.getLogger('keystoneauth.session.body')
body_logger.addHandler(body_handler)
'''

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
    neutron = neuclient.Client(session=session, region_name=region, timeout=10, logger=None)
    return neutron

def _get_nova_client(session, region=None):
    nova = novaclient.Client("2", session=session, region_name=region, timeout=10, logger=None)
    return nova

def _get_glance_client(session, region=None):
    glance = glanceclient.Client("2", session=session, region_name=region, logger=None)
    return glance

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
                (cloud.authurl, cloud.username, cloud.project, cloud.user_domain_name, cloud.project_domain_name))
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
            sess = session.Session(auth=auth, verify=config.categories["openstackPoller.py"]["cacerts"], split_loggers=False)
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
                project_domain_id=project_domain_id)
            sess = session.Session(auth=auth, verify=config.categories["openstackPoller.py"]["cacerts"], split_loggers=False)
        except Exception as exc:
            logging.error("Problem importing keystone modules, and getting session for grp:cloud - %s: %s", exc)
            logging.error("Connection parameters: \n authurl: %s \n username: %s \n project: %s \n user_domain: %s \n project_domain: %s", (auth_url, username, project, user_domain, project_domain_name))
            return False
        return sess


## Poller functions.

def flavor_poller():
    multiprocessing.current_process().name = "Flavor Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    FLAVOR = config.db_map.classes.cloud_flavors
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, FLAVOR, 'name', debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20), cloud_type="openstack")
        
        config.db_open()
        while True:
            try:
                logging.debug("Beginning flavor poller cycle")
                config.refresh()
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN) 
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
                    cloud_obj =  unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing flavours from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
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
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if flav_list is False:
                        logging.info("No flavors defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj.authurl + cloud_obj.project + cloud_obj.region, None)
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

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, flavor.name, flav_dict, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20)):
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
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_flavor"])
                    continue


                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud.authurl + cloud.project + cloud.region
                    if key in failure_dict:
                        new_f_dict[cloud.group_name+cloud.cloud_name] = 1

                # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
                delete_obsolete_database_items('Flavor', inventory, db_session, FLAVOR, 'name', poll_time=new_poll_time, failure_dict=new_f_dict, cloud_type="openstack")

                config.db_session.rollback()

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                group_clouds = config.db_connection.execute('select distinct group_name, cloud_name from csv2_clouds where cloud_type="openstack"')
                cleanup_inventory(inventory, group_clouds)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_flavor"], config)
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

def image_poller():
    multiprocessing.current_process().name = "Image Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    IMAGE = config.db_map.classes.cloud_images
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, IMAGE, 'id', debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20), cloud_type="openstack")
        config.db_open()
        while True:
            try:
                logging.debug("Beginning image poller cycle")
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()
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
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj'].authurl
                    logging.debug("Processing Images from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve all images for this cloud.
                    post_req_time = 0
                    pre_req_time = time.time() * 1000000 
                    glance = _get_glance_client(session, region=unique_cloud_dict[cloud]['cloud_obj'].region)
                    try:
                        image_list =  glance.images.list()
                        post_req_time = time.time()*1000000
                    except Exception as exc:
                        logging.error("Failed to retrieve image data for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if image_list is False:
                        logging.info("No images defined for %s, skipping this cloud..." %  cloud_name)
                        continue

                    uncommitted_updates = 0
                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj.authurl + cloud_obj.project + cloud_obj.region, None)
                        cloud_row = db_session.query(CLOUD).filter(CLOUD.group_name == grp_nm, CLOUD.cloud_name == cld_nm)[0]
                        logging.debug("pre request time:%s   post request time:%s" % (post_req_time, pre_req_time))
                        cloud_row.communication_rt = int(post_req_time - pre_req_time)
                        try:
                            db_session.merge(cloud_row)
                            uncommitted_updates += 1
                            config.reset_cloud_error(grp_nm, cld_nm)
                        except Exception as exc:
                            logging.warning("Failed merge and commit an update for communication_rt on cloud row : %s" % cloud_row)
                            logging.warning(exc)
                            db_session.rollback()

                    try:
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
                                  'checksum': image.checksum,
                                  'cloud_type': "openstack",
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

                              if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, image.id, img_dict, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20)):
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
                    except Exception as exc:
                        logging.error("Error proccessing image_list for cloud %s" % cloud_n)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue
                        

                    del glance 
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
                    config.db_session.rollback()
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_image"])
                    continue
                db_session.commit()
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                new_f_dict = {}
                logging.debug("Proccessing failure, failure_dict: %s" % failure_dict)
                for cloud in cloud_list:
                    key = cloud.authurl + cloud.project + cloud.region
                    if key in failure_dict:
                        new_f_dict[cloud.group_name+cloud.cloud_name] = 1
                        cloud_row = db_session.query(CLOUD).filter(CLOUD.group_name == cloud.group_name, CLOUD.cloud_name == cloud.cloud_name)[0]
                        db_session.merge(cloud_row)
                        db_session.commit()

                # Scan the OpenStack images in the database, removing each one that is not in the inventory.
                logging.info("Doing deletes, omitting failures: %s" % new_f_dict)
                delete_obsolete_database_items('Image', inventory, db_session, IMAGE, 'id', new_poll_time, failure_dict=new_f_dict, cloud_type="openstack")


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                group_clouds = config.db_connection.execute('select distinct group_name, cloud_name from csv2_clouds where cloud_type="openstack"')
                cleanup_inventory(inventory, group_clouds)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_image"], config)
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

# Retrieve keypairs.
def keypair_poller():
    multiprocessing.current_process().name = "Keypair Poller"
    
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    KEYPAIR = config.db_map.classes.cloud_keypairs
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, KEYPAIR, 'key_name', debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20), cloud_type="openstack")
        config.db_open()
        while True:
            try:    
                logging.debug("Beginning keypair poller cycle")
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()
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
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing Key pairs from group:cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s" % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
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
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj.authurl + cloud_obj.project + cloud_obj.region, None)
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
                            

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, key.name, key_dict, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20)):
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
                    config.db_session.rollback()
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_keypair"])
                    continue
                
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud.authurl + cloud.project + cloud.region
                    if key in failure_dict:
                        new_f_dict[cloud.group_name+cloud.cloud_name] = 1


                # Scan the OpenStack keypairs in the database, removing each one that was not updated in the inventory.
                delete_obsolete_database_items('Keypair', inventory, db_session, KEYPAIR, 'key_name', poll_time=new_poll_time, failure_dict=new_f_dict, cloud_type="openstack")

                config.db_session.rollback()

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                group_clouds = config.db_connection.execute('select distinct group_name, cloud_name from csv2_clouds where cloud_type="openstack"')
                cleanup_inventory(inventory, group_clouds)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_keypair"], config)
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

def limit_poller():
    multiprocessing.current_process().name = "Limit Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    LIMIT = config.db_map.classes.cloud_limits
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, LIMIT, '-', debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20), cloud_type="openstack")
        config.db_open()
        while True:
            try:
                logging.debug("Beginning limit poller cycle")
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()
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
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing limits from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
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
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if shared_limits_dict is False:
                        logging.info("No limits defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj.authurl + cloud_obj.project + cloud_obj.region, None)
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

                        if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, '-', limits_dict, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20)):
                            continue

                        for limit in limits_dict:
                            if "-1" in str(limits_dict[limit]):
                                limits_dict[limit] = config.categories["openstackPoller.py"]["no_limit_default"]
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
                        config.db_session.rollback()
                        time.sleep(config.categories["openstackPoller.py"]["sleep_interval_limit"])
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
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud.authurl + cloud.project + cloud.region
                    if key in failure_dict:
                        new_f_dict[cloud.group_name+cloud.cloud_name] = 1


                # Scan the OpenStack flavors in the database, removing each one that was` not iupdated in the inventory.
                delete_obsolete_database_items('Limit', inventory, db_session, LIMIT, '-', poll_time=new_poll_time, failure_dict=new_f_dict, cloud_type="openstack")

                config.db_session.rollback()
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                group_clouds = config.db_connection.execute('select distinct group_name, cloud_name from csv2_clouds where cloud_type="openstack"')
                cleanup_inventory(inventory, group_clouds)

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                signal.signal(signal.SIGINT, config.signals['SIGINT'])
 
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_limit"], config)
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

def network_poller():
    multiprocessing.current_process().name = "Network Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    NETWORK = config.db_map.classes.cloud_networks
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, NETWORK, 'name', debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20), cloud_type="openstack")
        config.db_open()
        while True:
            try:
                logging.debug("Beginning network poller cycle")
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)

                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()
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
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing networks from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
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
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if net_list is False:
                        logging.info("No networks defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj.authurl + cloud_obj.project + cloud_obj.region, None)
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

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, network['name'], network_dict, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20)):
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
                    config.db_session.rollback()
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_network"])
                    continue
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud.authurl + cloud.project + cloud.region
                    if key in failure_dict:
                        new_f_dict[cloud.group_name+cloud.cloud_name] = 1


                # Scan the OpenStack networks in the database, removing each one that was not updated in the inventory.
                delete_obsolete_database_items('Network', inventory, db_session, NETWORK, 'name', poll_time=new_poll_time, failure_dict=new_f_dict, cloud_type="openstack")

                config.db_session.rollback()

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                group_clouds = config.db_connection.execute('select distinct group_name, cloud_name from csv2_clouds where cloud_type="openstack"')
                cleanup_inventory(inventory, group_clouds)

                signal.signal(signal.SIGINT, config.signals['SIGINT'])

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_network"], config)
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


def security_group_poller():
    multiprocessing.current_process().name = "Security Group Poller"

    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])

    SECURITY_GROUP = config.db_map.classes.cloud_security_groups
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}
    my_pid = os.getpid()

    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")

    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, SECURITY_GROUP, 'id', debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20), cloud_type="openstack")
        config.db_open()
        while True:
            try:
                logging.debug("Beginning security group poller cycle")
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()
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
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing security groups from cloud - %s" % cloud_name)
                    session = _get_openstack_session(unique_cloud_dict[cloud]['cloud_obj'])
                    if session is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
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
                            if cloud_obj.authurl + cloud_obj.project + cloud_obj.region not in failure_dict:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = 1
                            else:
                                failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] = failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] + 1
                            if failure_dict[cloud_obj.authurl + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if sec_grp_list is False:
                        logging.info("No security groups defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj.authurl + cloud_obj.project + cloud_obj.region, None)
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

                            if test_and_set_inventory_item_hash(inventory, group_n, cloud_n, sec_grp["id"], sec_grp_dict, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20)):
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
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_sec_grp"])
                    continue
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud.authurl + cloud.project + cloud.region
                    if key in failure_dict:
                        new_f_dict[cloud.group_name+cloud.cloud_name] = 1

                # Scan the OpenStack sec_grps in the database, removing each one that was not iupdated in the inventory.
                delete_obsolete_database_items('sec_grp', inventory, db_session, SECURITY_GROUP, 'id', poll_time=new_poll_time, failure_dict=failure_dict, cloud_type="openstack")

                config.db_session.rollback()

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                group_clouds = config.db_connection.execute('select distinct group_name, cloud_name from csv2_clouds where cloud_type="openstack"')
                cleanup_inventory(inventory, group_clouds)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_security_group"], config)

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



def vm_poller():
    multiprocessing.current_process().name = "VM Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), "SQL", "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    VM = config.db_map.classes.csv2_vms
    FVM = config.db_map.classes.csv2_vms_foreign
    GROUP = config.db_map.classes.csv2_groups
    CLOUD = config.db_map.classes.csv2_clouds

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")
    
    try:
        inventory = get_inventory_item_hash_from_database(config.db_engine, VM, 'hostname', debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20), cloud_type="openstack")
        config.db_open()
        while True:
            # This cycle should be reasonably fast such that the scheduler will always have the most
            # up to date data during a given execution cycle.
            logging.debug("Beginning VM poller cycle")

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.refresh()
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
                    if auth_url + cloud_obj.project + cloud_obj.region not in failure_dict:
                        failure_dict[auth_url + cloud_obj.project + cloud_obj.region] = 1
                    else:
                        failure_dict[auth_url + cloud_obj.project + cloud_obj.region] = failure_dict[auth_url + cloud_obj.project + cloud_obj.region] + 1
                    if failure_dict[auth_url + cloud_obj.project + cloud_obj.region] > 3: #could be configurable
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
                    if auth_url + cloud_obj.project + cloud_obj.region not in failure_dict:
                        failure_dict[auth_url + cloud_obj.project + cloud_obj.region] = 1
                    else:
                        failure_dict[auth_url + cloud_obj.project + cloud_obj.region] = failure_dict[auth_url + cloud_obj.project + cloud_obj.region] + 1
                    if failure_dict[auth_url + cloud_obj.project + cloud_obj.region] > 3: #should be configurable
                        logging.error("Failure threshhold limit reached for %s::%s::%s, using group %s's crednetials manual action required, skipping" % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region, cloud_obj.group_name))
                    continue

                if vm_list is False:
                    logging.info("No VMs defined for %s::%s:%s, skipping this cloud..." % (cloud_obj.authurl, cloud_obj.project, cloud_obj.region))
                    del nova
                    continue

                # if we get here the connection to openstack has been succussful and we can remove the error status
                failure_dict.pop(auth_url + cloud_obj.project + cloud_obj.region, None)
                #update network status
                for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                    grp_nm = cloud_tuple[0]
                    cld_nm = cloud_tuple[1]
                    cloud_row = db_session.query(CLOUD).filter(CLOUD.group_name == grp_nm, CLOUD.cloud_name == cld_nm)[0]
                    cloud_row.communication_up = 1
                    db_session.merge(cloud_row)
                    db_session.commit()
                    

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
                        elif int(host_tokens[2]) != int(config.categories["SQL"]["csv2_host_id"]):
                            logging.debug("csv2 host id from host does not match (should be %s), marking %s as foreign vm" % (config.categories["SQL"]["csv2_host_id"], vm.name))
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
                        'image_id': vm.image['id'],
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

                    if test_and_set_inventory_item_hash(inventory, vm_group_name, vm_cloud_name, vm.name, vm_dict, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"]<20)):
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
                    if uncommitted_updates >= config.categories["openstackPoller.py"]["batch_commit_size"]:
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
                config.db_session.rollback()
                time.sleep(config.categories["openstackPoller.py"]["sleep_interval_vm"])
                continue

            # Scan the OpenStack VMs in the database, removing each one that is not in the inventory.
            # VMs have a different failure dict schema using group_name + auth_url instead of group_name + cloud_name
            #     failure_dict needs to be remapped before calling
            logging.debug("Expanding failure_dict: %s" % failure_dict)
            cloud_list = db_session.query(CLOUD).filter(CLOUD.cloud_type == "openstack")
            new_f_dict = {}
            for cloud in cloud_list:
                key = cloud.authurl + cloud.project + cloud.region
                if key in failure_dict:
                    new_f_dict[cloud.group_name+cloud.cloud_name] = 1
                    # update cloud network status
                    cloud.communication_up = 0
                    db_session.merge(cloud)
                    db_session.commit()

            delete_obsolete_database_items('VM', inventory, db_session, VM, 'hostname', new_poll_time, failure_dict=new_f_dict, cloud_type="openstack")


            # Check on the core limits to see if any clouds need to be scaled down.
            logging.debug("checking for over-quota clouds")
            over_quota_clouds = db_session.query(view_vm_kill_retire_over_quota).filter(view_vm_kill_retire_over_quota.c.cloud_type=="openstack")
            for cloud in over_quota_clouds:
                kill_retire(config, cloud.group_name, cloud.cloud_name, "control", [cloud.cores, cloud.ram], get_frame_info())


            logging.debug("Completed VM poller cycle")
            config.db_session.rollback()

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                break

            # Cleanup inventory, this function will clean up inventory entries for deleted clouds
            group_clouds = config.db_connection.execute('select distinct group_name, cloud_name from csv2_clouds where cloud_type="openstack"')
            cleanup_inventory(inventory, group_clouds)

            signal.signal(signal.SIGINT, config.signals['SIGINT'])

            try:
                wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_vm"], config)
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                continue

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()


def defaults_replication():
    multiprocessing.current_process().name = "Defaults Replication"
    db_category_list = [os.path.basename(sys.argv[0]), "general", "glintPoller.py" "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    GROUPS = config.db_map.classes.csv2_groups
    CLOUDS = config.db_map.classes.csv2_clouds
    KEYPAIRS = config.db_map.classes.cloud_keypairs
    IMAGES = config.db_map.classes.cloud_images
    IMAGE_TX = config.db_map.classes.csv2_image_transactions


    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    config.db_open()
    while True:
        try:
            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            db_session = config.db_session
            group_list = db_session.query(GROUPS)
            for group in group_list:
                src_keypair = None
                src_image = None
                default_image_name = group.vm_image
                default_key_name = group.vm_keyname
                cloud_list = db_session.query(CLOUDS).filter(CLOUDS.group_name == group.group_name, CLOUDS.cloud_type == "openstack")
                for cloud in cloud_list:
                    # if there is a default image for the group, check for default image in the cloud
                    if default_image_name is not None:
                        images = db_session.query(IMAGES).filter(IMAGES.group_name == group.group_name, IMAGES.cloud_name == cloud.cloud_name, IMAGES.name == default_image_name)
                        if images.count() == 0:
                            # gasp, image isn't there, lets queue up a transfer.
                            if src_image is None:
                               image_candidates = db_session.query(IMAGES).filter(IMAGES.group_name == group.group_name, IMAGES.name == default_image_name) 
                               img_count = image_candidates.count()
                               if img_count == 0:
                                   #default image not defined
                                   logging.error("Default image %s not present on any openstack clouds in group %s. Failed to replicate default image." % (default_image_name, group.group_name))
                                   continue
                               elif img_count > 1:
                                   logging.warning("More than one candidate image with name %s" % default_image_name)
                                   src_image = image_candidates[0]
                                   logging.warning("selecting candidate with checksum: %s" % src_image.checksum)
                               else:
                                   # no ambiguity about default image, simply select it
                                   src_image = image_candidates[0]
                            # We've got a source image, time to queue a transfer
                            # but first check the cache to see if we need to queue a pull request
                            cache_result = check_cache(config, default_image_name, src_image.checksum, src_image.group_name, "cloudscheduler")
                            if cache_result is False:
                                #Something went wrong checking the cache or queueing a pull request
                                logging.error("Failure checking cache or queuing pull request for image: %s" % default_image_name)
                                logging.error("...continuing to queue transfer (transfer task will queue up a pull request if needed)")
                            #Once here the image is in the cache of a pull request has been queued so we can go ahead and queue the transfer

                            #on second thought lets check to see we don't already have one queue'd up so we don't bombard the request queue
                            pending_xfers = db_session.query(IMAGE_TX).filter(IMAGE_TX.target_group_name == group.group_name, IMAGE_TX.target_cloud_name == cloud.cloud_name, IMAGE_TX.image_name == default_image_name, or_(IMAGE_TX.status == "pending", IMAGE_TX.status == "error"))
                            if pending_xfers.count() > 0:
                                logging.info("Default image (%s) transfer already queued for cloud: %s... skipping" % (default_image_name, cloud.cloud_name))
                                continue
                            tx_id = generate_tx_id()
                            tx_req = {
                                "tx_id":             tx_id,
                                "status":            "pending",
                                "target_group_name": group.group_name,
                                "target_cloud_name": cloud.cloud_name,
                                "image_name":        default_image_name,
                                "image_id":          src_image.id,
                                "checksum":          src_image.checksum,
                                "requester":         "cloudscheduler",
                            }
                            new_tx_req = IMAGE_TX(**tx_req)
                            db_session.merge(new_tx_req)
                            db_session.commit()
                            #tx_request.delay(tx_id = tx_id)
                            logging.info("Transfer queued")
                            tx_request.apply_async((tx_id,), queue='tx_requests')

                            
                    else:
                        logging.info("No default image for group %s, skipping image transfers for cloud %s" % (group.group_name, cloud.cloud_name))

                    # now lets check keys- if there is a default key, check the keys for the cloud
                    if default_key_name is not None:
                        keys = db_session.query(KEYPAIRS).filter(KEYPAIRS.group_name == group.group_name, KEYPAIRS.cloud_name == cloud.cloud_name, KEYPAIRS.key_name == default_key_name)
                        if keys.count() == 0:
                            # gasp again, keypair isn't present, keypairs are fast so lets just go ahead and do the transfer
                            if src_keypair == None:
                                # we haven't dug up a source keypair yet so lets grab one
                                db_keypair = db_session.query(KEYPAIRS).filter(KEYPAIRS.group_name == group.group_name, KEYPAIRS.key_name == default_key_name).first()
                                if db_keypair == None:
                                    #we couldn't find a source keypair for this group, yikes
                                    logging.error("Unable to locate a source keypair: %s for group %s, skipping group." % (default_key_name, group.group_name))
                                    break
                                src_cloud = db_session.query(CLOUDS).get((db_keypair.group_name, db_keypair.cloud_name))
                                try:
                                    src_keypair = get_keypair(default_key_name, src_cloud)
                                except Exception as exc:
                                    logging.error("Exception while locating source keypair:")
                                    logging.error(exc)
                                    src_keypair = None
                                if src_keypair == None:
                                    #we couldn't find a source keypair for this group, yikes
                                    logging.error("Unable to locate a source keypair: %s for group %s, skipping group." % (default_key_name, group.group_name))
                                    break
                                #transfer keypair
                                logging.info("Source keypair found, uploading new keypair")
                                try:
                                    transfer_keypair(src_keypair, src_cloud)
                                    logging.info("Keypair %s transferred to cloud %s successfully" % (default_key_name, cloud.cloud_name))
                                except Exception as exc:
                                    logging.error("Keypair transfer failed:")
                                    logging.error(exc)

                    else:
                        logging.info("No default keypair for group %s, skipping keypair transfers for cloud %s" % (group.group_name, cloud.cloud_name))
            
            db_session.commit()

        except Exception as exc:
            logging.error("Exception during general operation:")
            logging.error(exc)

        if not os.path.exists(PID_FILE):
            logging.info("Stop set, exiting...")
            break
        signal.signal(signal.SIGINT, config.signals['SIGINT'])
        wait_cycle(cycle_start_time, poll_time_history, 300, config)


## Main.

if __name__ == '__main__':
    process_ids = {
        'defaults_replication':  defaults_replication,
        'flavor':                flavor_poller,
        'image':                 image_poller,
        'keypair':               keypair_poller,
        'limit':                 limit_poller,
        'network':               network_poller,
        'vm':                    vm_poller,
        'security_group_poller': security_group_poller
    }
    db_categories = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor"]

    procMon = ProcessMonitor(config_params=db_categories, pool_size=3, process_ids=process_ids)
    config = procMon.get_config()
    logging = procMon.get_logging()
    version = config.get_version()

    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    with open(PID_FILE, "w") as fd:
        fd.write(str(os.getpid()))

    logging.info("**************************** starting openstack VM poller - Running %s *********************************" % version)


    # Wait for keyboard input to exit
    try:
        #start processes
        procMon.start_all()
        signal.signal(signal.SIGTERM, terminate)
        while True:
            config.refresh()
            config.update_service_catalog()
            stop = check_pid(PID_FILE)
            procMon.check_processes(stop=stop)
            time.sleep(config.categories["ProcessMonitor"]["sleep_interval_main_long"])

    except (SystemExit, KeyboardInterrupt):
        logging.error("Caught KeyboardInterrupt, shutting down threads and exiting...")

    except Exception as ex:
        logging.exception("Process Died: %s", ex)

    procMon.kill_join_all()
