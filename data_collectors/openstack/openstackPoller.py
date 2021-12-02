import multiprocessing
import logging
import socket
import time
import sys
import signal
import os
import datetime
from pytz import timezone
from dateutil import tz
import copy

from cloudscheduler.lib.attribute_mapper import map_attributes
from cloudscheduler.lib.db_config import Config
from cloudscheduler.lib.ProcessMonitor import ProcessMonitor, terminate, check_pid
#from cloudscheduler.lib.signal_manager import register_signal_receiver
from cloudscheduler.lib.view_utils import kill_retire
from cloudscheduler.lib.log_tools import get_frame_info
from cloudscheduler.lib.signal_functions import event_signal_send

#from glintwebui.glint_utils import get_keypair, transfer_keypair, generate_tx_id, check_cache
from glintwebui.glint_utils import generate_tx_id, check_cache
from glintwebui.keypair_utils import get_keypair, transfer_keypair
from glintwebui.celery_app import tx_request

from cloudscheduler.lib.poller_functions import \
    inventory_cleanup, \
    inventory_obsolete_database_items_delete, \
    inventory_get_item_hash_from_db_query_rows, \
    inventory_test_and_set_item_hash, \
    start_cycle, \
    wait_cycle

from cloudscheduler.lib.signal_functions import event_receiver_registration
from cloudscheduler.lib.openstack_functions import MyServer, get_openstack_sess, get_nova_connection, get_neutron_connection, get_cinder_connection, get_openstack_conn, convert_openstack_date_timezone
#import openstack

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

CLOUD = "csv2_clouds"

## Poller sub-functions.

def poller_setup(): 
    db_category_list = [os.path.basename(sys.argv[0]), "general", "signal_manager", "ProcessMonitor", "SQL"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    
    config.db_open()
    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")
    return config, PID_FILE

## Poller functions.

def flavor_poller():
    multiprocessing.current_process().name = "Flavor Poller"

    FLAVOR = "cloud_flavors"
    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='openstack'"
        rc, msg, rows = config.db_query(FLAVOR, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning flavor poller cycle")
                config.db_open()
                config.refresh()
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break
                
                signal.signal(signal.SIGINT, signal.SIG_IGN) 

                abort_cycle = False
                rc, msg, cloud_list = config.db_query(CLOUD, where="cloud_type='openstack'")

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                try:
                    for cloud in cloud_list:
                        if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                            unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                                'cloud_obj': cloud,
                                'groups': [(cloud["group_name"], cloud["cloud_name"])]
                            }
                        else:
                            unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))
                except Exception as exc:
                    logging.error("Failed to read cloud list %s" % exc)
                    continue

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj =  unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing flavours from cloud - %s" % cloud_name)
                    sess = get_openstack_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["openstackPoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                            continue

                    # setup OpenStack api objects
                    nova = get_nova_connection(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])

                    if nova is False:
                        logging.info("Openstack nova connection failed for %s, skipping this cloud..." % cloud_name)
                        continue

                    # Retrieve all flavours for this cloud.
                    try:
                        flav_list = nova.flavors()
                    except Exception as exc:
                        logging.error("Failed to retrieve flavor data for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if flav_list is False:
                        logging.info("No flavors defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    # Process flavours for this cloud.
                    uncommitted_updates = 0
                    try:
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
                                    'is_public': flavor.to_dict().get('is_public'),
                                    'last_updated': new_poll_time
                                    }

                                flav_dict, unmapped = map_attributes(src="os_flavors", dest="csv2", attr_dict=flav_dict, config=config)
                                if unmapped:
                                    logging.error("Unmapped attributes found during mapping, discarding:")
                                    logging.error(unmapped)

                                if inventory_test_and_set_item_hash(ikey_names, flav_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    config.db_merge(FLAVOR, flav_dict)
                                    uncommitted_updates += 1
                                except Exception as exc:
                                    logging.exception("Failed to merge flavor entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, flavor.name))
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc:
                                    logging.exception("Failed to commit flavor updates for %s, aborting cycle..." % cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                    except Exception as exc:
                        logging.error("Error proccessing flavor_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del nova
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Flavor updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_flavor"])
                    continue


                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                rc, msg, cloud_list = config.db_query(CLOUD, where="cloud_type='openstack'")
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1

                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                where_clause="cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(FLAVOR, where=where_clause)
                rows = []
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, FLAVOR)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_flavor"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("Flavor poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def image_poller():
    multiprocessing.current_process().name = "Image Poller"

    IMAGE = "cloud_images"

    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='openstack'"
        rc, msg, rows = config.db_query(IMAGE, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                config.db_open()
                logging.debug("Beginning image poller cycle")
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()

                abort_cycle = False
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud["group_name"], cloud["cloud_name"])]
                        }
                    else:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))

                for cloud in unique_cloud_dict:
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    logging.info("Processing Images from cloud - %s" % cloud_name)
                    sess = get_openstack_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["openstackPoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve all images for this cloud.
                    pre_req_time = time.time() * 1000000 
                    glance = get_openstack_conn(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])
                    conn_time = time.time() * 1000000
                    conn_time_cost = int(conn_time - pre_req_time)

                    if glance is False:
                        logging.info("Openstack glance connection failed for %s, skipping this cloud..." % cloud_name)
                        continue
                    
                    try:
                        image_service = glance.image
                    except Exception as exc:
                        logging.info("Openstack glance connection failed for %s, skipping this cloud..." % cloud_name)
                        continue
                    
                    try:
                        image_service_time = time.time() * 1000000
                        image_list = image_service.images()
                        post_req_time = time.time() * 1000000
                        image_time_cost = int(post_req_time - image_service_time)
                    except Exception as exc:
                        logging.error("Failed to retrieve image data for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0] 
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
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
                        failure_dict.pop(cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)
                        where_clause = "group_name='%s' and cloud_name='%s'" % (grp_nm, cld_nm)
                        rc, msg, cloud_rows = config.db_query(CLOUD, where=where_clause)
                        try:
                            cloud_row = cloud_rows[0]
                            cloud_row["communication_rt"] = int(conn_time_cost + image_time_cost)
                            logging.debug('cloud_tuple grp %s, cld %s, time diff %s' % (grp_nm, cld_nm, cloud_row["communication_rt"]))
                            cld_update_dict = {
                                "group_name": cloud_row["group_name"],
                                "cloud_name": cloud_row["cloud_name"],
                                "communication_rt": cloud_row["communication_rt"],
                            }
                            config.db_merge(CLOUD, cld_update_dict)
                            uncommitted_updates += 1
                            config.reset_cloud_error(grp_nm, cld_nm)
                        except Exception as exc:
                            logging.warning("Failed merge and commit an update for communication_rt on cloud row : %s" % cloud_row)
                            logging.warning(exc)

                    try:
                        for image in image_list:
                            if image.size == "" or image.size is None:
                                size = 0
                            else:
                                size = image.size

                            for groups in unique_cloud_dict[cloud]['groups']:
                                group_n = groups[0]
                                cloud_n = groups[1]

                                created_datetime = datetime.datetime.strptime(image.created_at, "%Y-%m-%dT%H:%M:%SZ")
                                created_datetime.strftime("%Y-%m-%d %H:%M:%S")
                                
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
                                    'created_at': created_datetime,
                                    'last_updated': new_poll_time
                                    }

                                img_dict, unmapped = map_attributes(src="os_images", dest="csv2", attr_dict=img_dict, config=config)
                                if unmapped:
                                    logging.error("Unmapped attributes found during mapping, discarding:")
                                    logging.error(unmapped)

                                if inventory_test_and_set_item_hash(ikey_names, img_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    logging.debug("Merging: %s" % img_dict)
                                    config.db_merge(IMAGE, img_dict)
                                    uncommitted_updates += 1
                                except Exception as exc:
                                    logging.exception("Failed to merge image entry for %s::%s::%s:" % (group_n, cloud_n, image.name))
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc:
                                    logging.exception("Failed to commit image updates for %s, aborting cycle..." % cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                    except Exception as exc:
                        logging.error("Error proccessing image_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue
                        

                    del glance 
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Image updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_image"])
                    continue
                config.db_commit()
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                new_f_dict = {}
                logging.debug("Proccessing failure, failure_dict: %s" % failure_dict)
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1
                        cld_update_dict = {
                            "group_name": cloud["group_name"],
                            "cloud_name": cloud["cloud_name"],
                            "communication_up": 0
                        }
                        config.db_commit()

                # Scan the OpenStack images in the database, removing each one that is not in the inventory.
                logging.debug("Doing deletes, omitting failures: %s" % new_f_dict)
                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                where_clause="cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(IMAGE, where=where_clause)
                rows = []
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, IMAGE)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_image"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue


    except Exception as exc:
        logging.exception("Image poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

# Retrieve keypairs.
def keypair_poller():
    multiprocessing.current_process().name = "Keypair Poller"
    
    KEYPAIR = "cloud_keypairs"
    ikey_names = ["group_name", "cloud_name", "fingerprint", "key_name"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='openstack'"
        rc, msg, rows = config.db_query(KEYPAIR, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:    
                logging.debug("Beginning keypair poller cycle")
                config.db_open()
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()

                abort_cycle = False
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud["group_name"], cloud["cloud_name"])]
                        }
                    else:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing Key pairs from group:cloud - %s" % cloud_name)
                    sess = get_openstack_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["openstackPoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s" % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # setup openstack api objects
                    nova = get_nova_connection(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])

                    if nova is False:
                        logging.info("Openstack nova connection failed for %s, skipping this cloud..." % cloud_name)
                        continue

                    #setup fingerprint list
                    fingerprint_list = []

                    try:
                        # get keypairs and add them to database
                        cloud_keys = nova.keypairs()
                    except Exception as exc:
                        logging.error("Failed to poll key pairs from nova, skipping %s" % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    uncommitted_updates = 0
                    try:
                        for key in cloud_keys:
                            fingerprint_list.append(key.fingerprint)
                            for groups in unique_cloud_dict[cloud]['groups']:
                                group_n = groups[0]
                                cloud_n = groups[1]
                                key_dict = {
                                    "cloud_name":  cloud_n,
                                    "group_name":  group_n,
                                    "key_name":    key.name,
                                    "cloud_type": "openstack",
                                    "fingerprint": key.fingerprint
                                }
                            

                                if inventory_test_and_set_item_hash(ikey_names, key_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    config.db_merge(KEYPAIR, key_dict)
                                    uncommitted_updates += 1
                                except Exception as exc:
                                    logging.exception("Failed to merge keypair entry for %s::%s, aborting cycle..." % (cloud_n, key.name))
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc:
                                    logging.error("Failed to commit new keypairs for %s, aborting cycle..."  % cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                    except Exception as exc:
                        logging.error("Error proccessing key_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del nova
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Keypair updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_keypair"])
                    continue
                
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1


                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                where_clause="cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(KEYPAIR, where=where_clause)
                rows = []
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, KEYPAIR)

                config.db_rollback()

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_keypair"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("Keypair poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def limit_poller():
    multiprocessing.current_process().name = "Limit Poller"

    LIMIT = "cloud_limits"
    ikey_names = ["group_name", "cloud_name"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='openstack'"
        rc, msg, rows = config.db_query(LIMIT, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning limit poller cycle")
                config.db_open()
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()

                abort_cycle = False
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                uncommitted_updates = 0

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud["group_name"], cloud["cloud_name"])]
                        }
                    else:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))

                logging.debug("Unique clouds dict: %s" % unique_cloud_dict.keys())

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing limits from cloud - %s" % cloud_name)
                    sess = get_openstack_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["openstackPoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve limit list for the current cloud.
                    nova = get_nova_connection(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])

                    if nova is False:
                        logging.info("Openstack nova connection failed for %s, skipping this cloud..." % cloud_name)
                        continue

                    shared_limits_dict = {}
                    try:
                        limit_list = nova.get_limits().absolute
                        for limit in limit_list:
                            shared_limits_dict[limit] = limit_list[limit]
                    except Exception as exc:
                        logging.error("Failed to retrieve limits from nova, skipping %s" %  cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if shared_limits_dict is False:
                        logging.info("No limits defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    # Process limit list for the current cloud.
                    try:
                        for groups in unique_cloud_dict[cloud]['groups']:
                            limits_dict = copy.deepcopy(shared_limits_dict)
                            # remove unused attributes
                            limits_dict.pop('id')
                            limits_dict.pop('name')
                            limits_dict.pop('location')

                            group_n = groups[0]
                            cloud_n = groups[1]                        
                            # We need to make just a connection object to get information about volumes
                            os_conn = get_openstack_conn(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])
                            try:
                                vol_limits = os_conn.get_volume_limits().absolute
                                vol_dict = {key:vol_limits[key] for key in ['maxTotalVolumes', 'totalVolumesUsed', 'maxTotalVolumeGigabytes', 'totalGigabytesUsed']}
                                limits_dict = { **limits_dict, **vol_dict}
                            except:
                                #no volume info for this cloud
                                logging.debug("No volume limits for %s::%s" % (group_n, cloud_n))


                            limits_dict['group_name'] = group_n
                            limits_dict['cloud_name'] = cloud_n
                            limits_dict['last_updated'] = int(time.time())
                            limits_dict, unmapped = map_attributes(src="os_limits", dest="csv2", attr_dict=limits_dict, config=config)
                            if unmapped:
                                logging.error("Unmapped attributes found during mapping, discarding:")
                                logging.error(unmapped)


                            if inventory_test_and_set_item_hash(ikey_names, limits_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                                continue

                            for limit in limits_dict:
                                if "-1" in str(limits_dict[limit]):
                                    limits_dict[limit] = config.categories["openstackPoller.py"]["no_limit_default"]
                                # for the data colleced from clouds, it shouldn't have any negative values unless in some error cases, so set the negative value to 0
                                else:
                                    try:
                                        if int(limits_dict[limit]) < 0:
                                            limits_dict[limit] = 0
                                    except:
                                        continue
                            limits_dict["cloud_type"] = "openstack"

                            try:
                                logging.debug("Updating grp:cld - %s:%s" % (group_n, cloud_n))
                                config.db_merge(LIMIT, limits_dict)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception("Failed to merge limits for %s::%s, aborting cycle..." % (group_n, cloud_n))
                                logging.error(exc)
                                abort_cycle = True
                                break

                            try:
                                config.db_commit()
                            except Exception as exc:
                                logging.error("Failed to commit new limits for %s, aborting cycle..."  % cloud_name)
                                logging.error(exc)
                                abort_cycle = True
                                break

                    except Exception as exc:
                        logging.error("Error proccessing limit_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del nova
                    if abort_cycle:
                        time.sleep(config.categories["openstackPoller.py"]["sleep_interval_limit"])
                        continue

                    if uncommitted_updates > 0:
                        logging.info("Limit updates committed: %d" % uncommitted_updates)

                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1

                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                where_clause="cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(LIMIT, where=where_clause)
                rows = []
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, LIMIT)

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()
 
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_limit"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("Limit poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

def network_poller():
    multiprocessing.current_process().name = "Network Poller"

    NETWORK = "cloud_networks"
    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='openstack'"
        rc, msg, rows = config.db_query(NETWORK, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning network poller cycle")
                config.db_open()
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)

                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()

                abort_cycle = False
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud["group_name"], cloud["cloud_name"])]
                        }
                    else:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))

                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing networks from cloud - %s" % cloud_name)
                    sess = get_openstack_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["openstackPoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve network list.
                    neutron = get_neutron_connection(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])

                    if neutron is False:
                        logging.info("Openstack neutron connection failed for %s, skipping this cloud..." % cloud_name)
                        continue
                    
                    try:
                        net_list = neutron.networks()
                    except Exception as exc:
                        logging.error("Failed to retrieve networks from neutron, skipping %s" %  cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if net_list is False:
                        logging.info("No networks defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    uncommitted_updates = 0
                    try:
                        for network in net_list:
                            for groups in unique_cloud_dict[cloud]['groups']:
                                group_n = groups[0]
                                cloud_n = groups[1]
                                network_dict = {
                                    'group_name': group_n,
                                    'cloud_name': cloud_n,
                                    'name': network['name'],
                                    'cloud_type': "openstack",
                                    'subnets': ''.join(network['subnet_ids']),
                                    'tenant_id': network['project_id'],
                                    'router:external': network['is_router_external'],
                                    'shared': network['is_shared'],
                                    'id': network['id'],
                                    'last_updated': int(time.time())
                                }

                                network_dict, unmapped = map_attributes(src="os_networks", dest="csv2", attr_dict=network_dict, config=config)
                                if unmapped:
                                    logging.error("Unmapped attributes found during mapping, discarding:")
                                    logging.error(unmapped)

                                if inventory_test_and_set_item_hash(ikey_names, network_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    config.db_merge(NETWORK, network_dict)
                                    uncommitted_updates += 1
                                except Exception as exc:
                                    logging.exception("Failed to merge network entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, network['name']))
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc:
                                    logging.error("Failed to commit new networks for %s, aborting cycle..." %  cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                    except Exception as exc:
                        logging.error("Error proccessing network_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del neutron
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Network updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    config.db_rollback()
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_network"])
                    continue
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1

                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                where_clause="cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(NETWORK, where=where_clause)
                rows = []
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, NETWORK)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)

                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_network"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                    config.db_close()
                    continue

    except Exception as exc:
        logging.exception("Network poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()


def security_group_poller():
    multiprocessing.current_process().name = "Security Group Poller"

    SECURITY_GROUP = "cloud_security_groups"
    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}
    my_pid = os.getpid()

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='openstack'"
        rc, msg, rows = config.db_query(SECURITY_GROUP, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning security group poller cycle")
                config.db_open()
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()

                abort_cycle = False
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud["group_name"], cloud["cloud_name"])]
                        }
                    else:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))


                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    logging.debug("Processing security groups from cloud - %s" % cloud_name)
                    sess = get_openstack_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["openstackPoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                            continue

                    # setup OpenStack api objects
                    neu = get_neutron_connection(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])
                    
                    if neu is False:
                        logging.info("Openstack neutron connection failed for %s, skipping this cloud..." % cloud_name)
                        continue

                    # Retrieve all flavours for this cloud.
                    try:
                        sec_grp_list = neu.security_groups()
                    except Exception as exc:
                        logging.error("Failed to retrieve security groups for %s, skipping this cloud..." % cloud_name)
                        logging.error(exc)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    if sec_grp_list is False:
                        logging.info("No security groups defined for %s, skipping this cloud..." % cloud_name)
                        continue

                    for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                        grp_nm = cloud_tuple[0]
                        cld_nm = cloud_tuple[1]
                        failure_dict.pop(cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)
                        config.reset_cloud_error(grp_nm, cld_nm)

                    # Process security groups for this cloud.
                    uncommitted_updates = 0
                    try:
                        for sec_grp in sec_grp_list:
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

                                flav_dict, unmapped = map_attributes(src="os_sec_grps", dest="csv2", attr_dict=sec_grp_dict, config=config)
                                if unmapped:
                                    logging.error("Unmapped attributes found during mapping, discarding:")
                                    logging.error(unmapped)

                                if inventory_test_and_set_item_hash(ikey_names, sec_grp_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                                    continue

                                try:
                                    config.db_merge(SECURITY_GROUP, sec_grp_dict)
                                    uncommitted_updates += 1
                                except Exception as exc:
                                    logging.exception("Failed to merge security group entry for %s::%s::%s, aborting cycle..." % (group_n, cloud_n, sec_grp.name))
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                                try:
                                    config.db_commit()
                                except Exception as exc:
                                    logging.exception("Failed to commit security group updates for %s, aborting cycle..." % cloud_name)
                                    logging.error(exc)
                                    abort_cycle = True
                                    break

                    except Exception as exc:
                        logging.error("Error proccessing security_group_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del neu
                    if abort_cycle:
                        break

                    if uncommitted_updates > 0:
                        logging.info("Security group updates committed: %d" % uncommitted_updates)

                if abort_cycle:
                    config.db_close()
                    time.sleep(config.categories["openstackPoller.py"]["sleep_interval_sec_grp"])
                    continue
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                where_clause = "cloud_type='openstack'"
                rc, qmsg, cloud_list = config.db_query(CLOUD, where=where_clause)
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1

                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                where_clause="cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(SECURITY_GROUP, where=where_clause)
                rows = []
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, SECURITY_GROUP)


                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    config.db_close()
                    break
                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)


                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()

                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_security_group"], config)

                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue

            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("sec_grp poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()



def vm_poller():
    multiprocessing.current_process().name = "VM Poller"

    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', [os.path.basename(sys.argv[0]), "SQL", "ProcessMonitor"], pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    VM = "csv2_vms"
    FVM = "csv2_vms_foreign"
    GROUP = "csv2_groups"
    CLOUD = "csv2_clouds"
    ikey_names = ["group_name", "cloud_name", "vmid"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config.db_open()
    event_receiver_registration(config, "insert_csv2_clouds_openstack")
    event_receiver_registration(config, "update_csv2_clouds_openstack")
    
    try:
        where_clause = "cloud_type='openstack'"
        rc, msg, rows = config.db_query(VM, where=where_clause)
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            # This cycle should be reasonably fast such that the scheduler will always have the most
            # up to date data during a given execution cycle.
            logging.debug("Beginning VM poller cycle")

            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break
            config.db_open()
            signal.signal(signal.SIGINT, signal.SIG_IGN)

            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
            config.refresh()

            # For each OpenStack cloud, retrieve and process VMs.
            abort_cycle = False
            rc, msg, group_list = config.db_query(GROUP)

            where_clause = "cloud_type='openstack'"
            rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
            try:
                avg_cycle_length = 0
                for poll_time in poll_time_history:
                    avg_cycle_length = avg_cycle_length + poll_time
                avg_cycle_length = avg_cycle_length/len(poll_time_history)
                if avg_cycle_length < config.categories["openstackPoller.py"]["sleep_interval_vm"]:
                    avg_cycle_length = config.categories["openstackPoller.py"]["sleep_interval_vm"]
                where_clause="cloud_type='openstack' and start_time<='%s'" % (new_poll_time-2*avg_cycle_length)
                rc, msg, unfiltered_rows = config.db_query(VM, where=where_clause)
            except Exception as exc:
                logging.error("Failed to read configuration: %s" % exc)
                where_clause = "cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(VM, where=where_clause)
            
            # build unique cloud list to only query a given cloud once per cycle
            unique_cloud_dict = {}
            for cloud in cloud_list:
                if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                    unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                        'cloud_obj': cloud,
                        'groups': [(cloud["group_name"], cloud["cloud_name"])]
                    }
                else:
                    unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))

            group_list = []
            for cloud in unique_cloud_dict:
                group_list = group_list +unique_cloud_dict[cloud]['groups']

            for cloud in unique_cloud_dict:
                auth_url = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                cloud_obj = unique_cloud_dict[cloud]['cloud_obj']

                where_clause = "authurl='%s' and region='%s' and project='%s'" % (cloud_obj["authurl"], cloud_obj["region"], cloud_obj["project"])
                rc, msg, foreign_vm_list = config.db_query(FVM, where=where_clause)

                #set foreign vm counts to zero as we will recalculate them as we go, any rows left at zero should be deleted
                # dict[cloud+flavor]
                for_vm_dict = {}
                for for_vm in foreign_vm_list:
                    fvm_dict = {
                        "fvm_obj": for_vm,
                        "count": 0,
                        "region": cloud_obj["region"],
                        "authurl": cloud_obj["authurl"],
                        "project": cloud_obj["project"]
                    }
                    for_vm_dict[auth_url + "--" + for_vm["flavor_id"]] = fvm_dict

                logging.debug("Polling VMs from cloud: %s" % auth_url)
                sess = get_openstack_sess(cloud_obj, config.categories["openstackPoller.py"]["cacerts"])
                if sess is False:
                    logging.debug("Failed to establish session with %s::%s::%s, using group %s's credentials skipping this cloud..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                    if auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                        failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                    else:
                        failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                    if failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #could be configurable
                        logging.error("Failure threshhold limit reached for %s::%s::%s, using group %s's credentials, manual action required, skipping" % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                    continue

                # Retrieve VM list for this cloud.
                nova = get_nova_connection(sess, region=cloud_obj["region"])

                if nova is False:
                    logging.info("Openstack nova connection failed for %s, skipping this cloud..." % cloud_obj["cloud_name"])
                    continue

                try:
                    vm_list = nova.servers()
                except Exception as exc:
                    logging.error("Failed to retrieve VM data for  %s::%s::%s, skipping this cloud..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"]))
                    logging.error("Exception type: %s" % type(exc))
                    logging.error(exc)
                    if auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                        failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                    else:
                        failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                    if failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                        logging.error("Failure threshhold limit reached for %s::%s::%s, using group %s's crednetials manual action required, skipping" % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                    continue

                if vm_list is False:
                    logging.info("No VMs defined for %s::%s:%s, skipping this cloud..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"]))
                    del nova
                    continue

                # if we get here the connection to openstack has been succussful and we can remove the error status
                failure_dict.pop(auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)
                #update network status
                for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                    grp_nm = cloud_tuple[0]
                    cld_nm = cloud_tuple[1]
                    #where_clause = "group_name='%s' and cloud_name='%s'" % (grp_nm, cld_nm)
                    #rc, msg, cloud_rows = config.db_query(CLOUD, where=where_clause)
                    #cloud_row = cloud_rows[0]
                    cloud_row = {
                        "group_name": grp_nm,
                        "cloud_name": cld_nm,
                        "communication_up": 1
                    }
                    config.db_update(CLOUD, cloud_row)
                    config.db_commit()
                    

                # Process VM list for this cloud.
                # We've decided to remove the variable "status_changed_time" since it was holding the exact same value as "last_updated"
                # This is because we are only pushing updates to the csv2 database when the state of a vm is changed and thus it would be logically equivalent
                uncommitted_updates = 0
                try:
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
                            found_flavor = nova.find_flavor(name_or_id=vm.flavor['original_name'])
                            vm_flavor_id = found_flavor.id
                     
                            if (host_tokens[0], host_tokens[1]) not in group_list:
                                logging.debug("Group-Cloud combination doesn't match any in csv2, marking %s as foreign vm" % vm.name)
                                logging.debug(group_list)
                                if auth_url + "--" + vm_flavor_id in for_vm_dict:
                                    for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] = for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[auth_url + "--" + vm_flavor_id]= {
                                        'count': 1,
                                        'region': cloud_obj["region"],
                                        'project': cloud_obj["project"],
                                        'authurl': cloud_obj["authurl"], 
                                        'flavor_id': vm_flavor_id
                                    }
                                continue
                            elif int(host_tokens[2]) != int(config.categories["SQL"]["csv2_host_id"]):
                                logging.debug("csv2 host id from host does not match (should be %s), marking %s as foreign vm" % (config.categories["SQL"]["csv2_host_id"], vm.name))
                                if auth_url + "--" + vm_flavor_id in for_vm_dict:
                                    for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] = for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] + 1
                                else:
                                    # no entry yet
                                    for_vm_dict[auth_url + "--" + vm_flavor_id]= {
                                        'count': 1,
                                        'region': cloud_obj["region"],
                                        'project': cloud_obj["project"],
                                        'authurl': cloud_obj["authurl"], 
                                        'flavor_id': vm_flavor_id
                                    }

                                #foreign vm
                                continue
                        except IndexError as exc:
                            #not enough tokens, bad hostname or foreign vm
                            logging.debug("Not enough tokens from hostname, bad hostname or foreign vm: %s" % vm.name)
                            found_flavor = nova.find_flavor(name_or_id=vm.flavor['original_name'])
                            if found_flavor is not None:
                                vm_flavor_id = found_flavor.id
                            else:
                                vm_flavor_id = vm.flavor['original_name']
                            if auth_url + "--" + vm_flavor_id in for_vm_dict:
                                for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] = for_vm_dict[auth_url + "--" + vm_flavor_id]["count"] + 1
                            else:
                                # no entry yet
                                for_vm_dict[auth_url + "--" + vm_flavor_id]= {
                                    'count': 1,
                                    'region': cloud_obj["region"],
                                    'project': cloud_obj["project"],
                                    'authurl': cloud_obj["authurl"], 
                                    'flavor_id': vm_flavor_id
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
                        
                        additions = {}
                        where_clause="group_name='%s' and cloud_name='%s' and hostname='%s'" % (vm_group_name, vm_cloud_name, vm.name)
                        rc, msg, rows = config.db_query(VM, where=where_clause)
                        if (not rows) or len(rows) == 0:
                            where_clause = "group_name='%s'" % cloud_obj["group_name"]
                            rc, msg, found_group = config.db_query("csv2_groups", where=where_clause)
                            keep_alive = 0
                            if found_group and len(found_group) > 0:
                                keep_alive = found_group[0].get("vm_keep_alive")
                            additions = {'start_time': int(time.time()), 'keep_alive': keep_alive}
                        
                        vm_error = None
                        if vm.status == "ERROR":
                            try:
                                s = nova._get(MyServer, vm.id)
                                if s.fault and s.fault.get('message'):
                                    vm_error = s.fault.get('message')
                                    #logging.error("Found vm %s in error state: %s" % (vm.name, s.fault.get('message')))
                            except Exception as exc:
                                logging.error("Failed to get error message from vm %s: %s" % (vm.name, exc))

                        vm_dict = {
                            'group_name': vm_group_name,
                            'cloud_name': vm_cloud_name,
                            'region': cloud_obj["region"],
                            'auth_url': cloud_obj["authurl"],
                            'project': cloud_obj["project"],
                            'cloud_type': "openstack",
                            'hostname': vm.name,
                            'vmid': vm.id,
                            'image_id': vm.image['id'],
                            'status': vm.status,
                            'vm_error': vm_error,
                            'flavor_id': vm_flavor_id,
                            'task': vm.to_dict().get('task_state'),
                            'power_state': vm.to_dict().get('power_state'),
                            'vm_ips': str(ip_addrs),
                            'vm_floating_ips': str(floating_ips),
                            'last_updated': new_poll_time,
                            **additions
                        }

                        vm_dict, unmapped = map_attributes(src="os_vms", dest="csv2", attr_dict=vm_dict, config=config)
                        if unmapped:
                            logging.error("unmapped attributes found during mapping, discarding:")
                            logging.error(unmapped)

                        if inventory_test_and_set_item_hash(ikey_names, vm_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                            continue

                        try:
                            config.db_merge(VM, vm_dict)
                            uncommitted_updates += 1
                        except Exception as exc:
                            logging.exception("Failed to merge VM entry for %s::%s::%s, using group %s's credentials aborting cycle..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                            logging.error(exc)
                            abort_cycle = True
                            break

                        try:
                            config.db_commit()
                        except Exception as exc:
                            logging.exception("Failed to commit VM updates for %s::%s:%s, using group %s's credentials aborting cycle..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                            logging.error(exc)
                            abort_cycle = True
                            break

                except Exception as exc:
                    logging.error("Error proccessing vm_list for cloud %s" % cloud_obj["cloud_name"])
                    logging.error(exc)
                    logging.error("Skipping cloud...")
                    continue

                del nova
                if abort_cycle:
                    break

                for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                    grp_nm = cloud_tuple[0]
                    cld_nm = cloud_tuple[1]
                    where_clause = "group_name='%s' and cloud_name='%s'" % (grp_nm, cld_nm)
                    cloud_row = { "freeze": 0 }
                    config.db_update("csv2_clouds", cloud_row, where=where_clause)
                    config.db_commit()
                    logging.debug("reset freeze for cloud %s" % cld_nm)
            
                if uncommitted_updates > 0:
                    logging.info("VM updates committed: %d for cloud %s" % (uncommitted_updates, cloud_obj["cloud_name"]))

                # proccess FVM dict
                # check if any rows have a zero count and delete them, otherwise update with new count
                for key in for_vm_dict:
                    split_key = key.split("--")
                    if for_vm_dict[key]['count'] == 0:
                        # delete this row
                        config.db_delete(FVM, for_vm_dict[key]['fvm_obj'])
                    else:
                        try:
                            # if we get here there is at least 1 count of this flavor, though there may not be a database object yet
                            for_vm_dict[key]['fvm_obj']["count"] = for_vm_dict[key]['count']
                            config.db_merge(FVM, for_vm_dict[key]['fvm_obj'])
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
                            config.db_merge(FVM, fvm_dict)
                    try:
                        config.db_commit()
                    except Exception as exc:
                        logging.exception("Failed to commit foreign VM updates, aborting cycle...")
                        logging.error(exc)
                        abort_cycle = True
                        break

            if abort_cycle:
                config.db_rollback()
                config.db_close()
                time.sleep(config.categories["openstackPoller.py"]["sleep_interval_vm"])
                continue

            # Scan the OpenStack VMs in the database, removing each one that is not in the inventory.
            # VMs have a different failure dict schema using group_name + auth_url instead of group_name + cloud_name
            #     failure_dict needs to be remapped before calling
            logging.debug("Expanding failure_dict: %s" % failure_dict)
            where_clause="cloud_type='openstack'"
            rc, qmsg, cloud_list = config.db_query(CLOUD, where=where_clause)
            new_f_dict = {}
            for cloud in cloud_list:
                key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                if key in failure_dict:
                    new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1
                    # update cloud network status
                    cloud_row = {
                        "group_name": cloud["group_name"],
                        "cloud_name": cloud["cloud_name"],
                        "communication_up": 0
                    }
                    config.db_update(CLOUD, cloud_row)
                    config.db_commit()

            # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
            rows = []            
            for row in unfiltered_rows:
                if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                    continue
                else:
                    rows.append(row)
            inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, VM)


            # Check on the core limits to see if any clouds need to be scaled down.
            logging.debug("checking for over-quota clouds")
            where_clause = "cloud_type='openstack'"
            rc, msg, over_quota_clouds = config.db_query("view_vm_kill_retire_over_quota", where=where_clause) 
            for cloud in over_quota_clouds:
                logging.info("Remove overquota vms from %s::%s" % (cloud["group_name"], cloud["cloud_name"]))
                kill_retire(config, cloud["group_name"], cloud["cloud_name"], "control", [cloud["cores"], cloud["ram"]], get_frame_info())
                config.db_commit()
            if len(over_quota_clouds) > 0: 
                try:
                    logging.info("Finish removing overquota vms, send signal")
                    event_signal_send(config, "update_csv2_clouds_openstack")
                except Exception as exc:
                    logging.error("Error when sending signals after removing overquota vms: %s" % exc)

            logging.debug("Completed VM poller cycle")

            if not os.path.exists(PID_FILE):
                logging.info("Stop set, exiting...")
                config.db_close()
                break

            # Cleanup inventory, this function will clean up inventory entries for deleted clouds
            inventory_cleanup(ikey_names, rows, inventory)

            signal.signal(signal.SIGINT, config.signals['SIGINT'])
            config.db_close()

            try:
                wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_vm"], config)
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                continue

    except Exception as exc:
        logging.exception("VM poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def volume_poller():
    multiprocessing.current_process().name = "Volume Poller"

    VOLUME = "cloud_volumes"
    ikey_names = ["group_name", "cloud_name", "id"]

    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]
    failure_dict = {}

    config, PID_FILE = poller_setup()

    try:
        where_clause = "cloud_type='openstack'"
        #rc, msg, rows = config.db_query(VOLUME, where=where_clause)
        rows = []
        config.db_open()
        inventory = inventory_get_item_hash_from_db_query_rows(ikey_names, rows)
        config.db_close()
        while True:
            try:
                logging.debug("Beginning volume poller cycle")
                config.db_open()
                if not os.path.exists(PID_FILE):
                    logging.debug("Stop set, exiting...")
                    break

                signal.signal(signal.SIGINT, signal.SIG_IGN)
                new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)
                config.refresh()

                abort_cycle = False
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                uncommitted_updates = 0

                # build unique cloud list to only query a given cloud once per cycle
                unique_cloud_dict = {}
                for cloud in cloud_list:
                    if cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"] not in unique_cloud_dict:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]] = {
                            'cloud_obj': cloud,
                            'groups': [(cloud["group_name"], cloud["cloud_name"])]
                        }
                    else:
                        unique_cloud_dict[cloud["authurl"]+cloud["project"]+cloud["region"]+cloud["username"]]['groups'].append((cloud["group_name"], cloud["cloud_name"]))

                group_list = []
                for cloud in unique_cloud_dict:
                    group_list = group_list +unique_cloud_dict[cloud]['groups']
                    logging.debug("Unique clouds dict: %s" % unique_cloud_dict.keys())
                for cloud in unique_cloud_dict:
                    cloud_name = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    cloud_obj = unique_cloud_dict[cloud]['cloud_obj']
                    auth_url = unique_cloud_dict[cloud]['cloud_obj']["authurl"]
                    logging.debug("Processing limits from cloud - %s" % cloud_name)
                    sess = get_openstack_sess(unique_cloud_dict[cloud]['cloud_obj'], config.categories["openstackPoller.py"]["cacerts"])
                    if sess is False:
                        logging.debug("Failed to establish session with %s, skipping this cloud..." % cloud_name)
                        for cloud_tuple in unique_cloud_dict[cloud]['groups']:
                            grp_nm = cloud_tuple[0]
                            cld_nm = cloud_tuple[1]
                            if cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                            else:
                                failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                            if failure_dict[cloud_obj["authurl"] + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                                logging.error("Failure threshhold limit reached for %s, manual action required, reporting cloud error" % grp_nm+cld_nm)
                                config.incr_cloud_error(grp_nm, cld_nm)
                        continue

                    # Retrieve volume list for the current cloud.
                    cinder = get_cinder_connection(sess, region=unique_cloud_dict[cloud]['cloud_obj']["region"])

                    if cinder is False:
                        logging.info("Openstack cinder connection failed for %s, skipping this cloud..." % cloud_name)
                        continue


                    try:
                        volume_list = cinder.volumes()
                    except Exception as exc:
                        logging.error("Failed to retrieve VM data for  %s::%s::%s, skipping this cloud..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"]))
                        logging.error("Exception type: %s" % type(exc))
                        logging.error(exc)
                    if auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"] not in failure_dict:
                        failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = 1
                    else:
                        failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] = failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] + 1
                    if failure_dict[auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"]] > 3: #should be configurable
                        logging.error("Failure threshhold limit reached for %s::%s::%s, using group %s's crednetials manual action required, skipping" % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))

                    if volume_list is False:
                        logging.info("No Volumes defined for %s::%s:%s, skipping this cloud..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"]))
                        del nova
                        continue

                    failure_dict.pop(auth_url + cloud_obj["project"] + cloud_obj["region"] + cloud_obj["username"], None)

                    # Process Volume list for this cloud.
                    # We've decided to remove the variable "status_changed_time" since it was holding the exact same value as "last_updated"
                    # This is because we are only pushing updates to the csv2 database when the state of a vm is changed and thus it would be logically equivalent
                    uncommitted_updates = 0
                    try:
                        for volume in volume_list:
                            try:
                                if volume.name.startswith("vol-"):
                                    host_tokens_string = volume.name[4:]
                                else:
                                    logging.debug("Volume name does not match csv2 nomenclature, marking %s as foreign vol" % volume.name)
                                    continue
                                host_tokens = host_tokens_string.split("--")
                                vol_group_name = host_tokens[0]
                                vol_cloud_name = host_tokens[1]

                                if (host_tokens[0], host_tokens[1]) not in group_list:
                                    logging.debug("Group-Cloud combination doesn't match any in csv2, marking %s as foreign vol" % volume.name)
                                    continue
                                elif int(host_tokens[2]) != int(config.categories["SQL"]["csv2_host_id"]):
                                    logging.debug("csv2 host id from host does not match (should be %s), marking %s as foreign vol" % (config.categories["SQL"]["csv2_host_id"], volume.name))
                                    continue
                            except IndexError as exc:
                                #not enough tokens, bad hostname or foreign vm
                                logging.debug("Not enough tokens from hostname, bad hostname or foreign volume: %s" % volume.name)
                                continue
                        
                            if volume.created_at:
                                datetimeObj = datetime.datetime.strptime(volume.created_at, '%Y-%m-%dT%H:%M:%S.%f')
                                created_time = convert_openstack_date_timezone(datetimeObj)
                            else:
                                created_time = None
                        
                            vol_dict = {
                                'group_name': vol_group_name,
                                'cloud_name': vol_cloud_name,
                                'id': volume.id,
                                'name': volume.name,
                                'size': volume.size,
                                'volume_type': volume.volume_type,
                                'status': volume.status,
                                'cloud_type': "openstack",
                                'created_at': created_time,
                                'last_updated': new_poll_time
                            }
                            if inventory_test_and_set_item_hash(ikey_names, vol_dict, inventory, new_poll_time, debug_hash=(config.categories["openstackPoller.py"]["log_level"] < 20)):
                                continue

                            try:
                                config.db_merge(VOLUME, vol_dict)
                                uncommitted_updates += 1
                            except Exception as exc:
                                logging.exception("Failed to merge Volume entry for %s::%s::%s, using group %s's credentials aborting cycle..." % (cloud_obj["authurl"], cloud_obj["project"], cloud_obj["region"], cloud_obj["group_name"]))
                                logging.error(exc)
                                abort_cycle = True
                                break

                            try:
                                config.db_commit()
                            except Exception as exc:
                                logging.error("Error during batch commit of Volumes:")
                                logging.error(exc)

                    except Exception as exc:
                        logging.error("Error proccessing volume_list for cloud %s" % cloud_name)
                        logging.error(exc)
                        logging.error("Skipping cloud...")
                        continue

                    del cinder
                    if abort_cycle:
                        time.sleep(config.categories["openstackPoller.py"]["sleep_interval_limit"])
                        continue

                    if uncommitted_updates > 0:
                        logging.info("Volume updates committed: %d" % uncommitted_updates)

                #~~~~~~~
                # Expand failure dict for deletion schema (key needs to be grp+cloud)
                where_clause = "cloud_type='openstack'"
                rc, msg, cloud_list = config.db_query(CLOUD, where=where_clause)
                new_f_dict = {}
                for cloud in cloud_list:
                    key = cloud["authurl"] + cloud["project"] + cloud["region"] + cloud["username"]
                    if key in failure_dict:
                        new_f_dict[cloud["group_name"]+cloud["cloud_name"]] = 1

                # since the new inventory function doesn't accept a failfure dict we need to screen the rows ourself
                where_clause="cloud_type='openstack'"
                rc, msg, unfiltered_rows = config.db_query(VOLUME, where=where_clause)
                rows = []
                for row in unfiltered_rows:
                    if row['group_name'] + row['cloud_name'] in new_f_dict.keys():
                        continue
                    else:
                        rows.append(row)
                inventory_obsolete_database_items_delete(ikey_names, rows, inventory, new_poll_time, config, VOLUME)

                # Cleanup inventory, this function will clean up inventory entries for deleted clouds
                inventory_cleanup(ikey_names, rows, inventory)

                if not os.path.exists(PID_FILE):
                    logging.info("Stop set, exiting...")
                    break
                signal.signal(signal.SIGINT, config.signals['SIGINT'])
                config.db_close()
 
                try:
                    wait_cycle(cycle_start_time, poll_time_history, config.categories["openstackPoller.py"]["sleep_interval_limit"], config)
                except KeyboardInterrupt:
                    # sigint recieved, cancel the sleep and start the loop
                    continue
            except KeyboardInterrupt:
                # sigint recieved, cancel the sleep and start the loop
                logging.error("Recieved wake-up signal during regular execution, resetting and continuing")
                config.db_close()
                continue

    except Exception as exc:
        logging.exception("Volume poller cycle while loop exception, process terminating...")
        logging.error(exc)
        config.db_close()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def defaults_replication():
    multiprocessing.current_process().name = "Defaults Replication"
    db_category_list = [os.path.basename(sys.argv[0]), "general", "glintPoller.py" "signal_manager", "ProcessMonitor"]
    config = Config('/etc/cloudscheduler/cloudscheduler.yaml', db_category_list, pool_size=3, signals=True)
    PID_FILE = config.categories["ProcessMonitor"]["pid_path"] + os.path.basename(sys.argv[0])
    GROUPS = "csv2_groups"
    CLOUDS = "csv2_clouds"
    KEYPAIRS = "cloud_keypairs"
    IMAGES = "cloud_images"
    IMAGE_TX = "csv2_image_transactions"


    cycle_start_time = 0
    new_poll_time = 0
    poll_time_history = [0,0,0,0]

    while True:
        try:
            config.db_open()
            config.refresh()
            if not os.path.exists(PID_FILE):
                logging.debug("Stop set, exiting...")
                break

            signal.signal(signal.SIGINT, signal.SIG_IGN)
            new_poll_time, cycle_start_time = start_cycle(new_poll_time, cycle_start_time)

            rc, msg, group_list = config.db_query(GROUPS)
            for group in group_list:
                logging.debug("Checking defaults for %s" % group["group_name"])
                src_image = None
                grp_default_image_name = group["vm_image"]
                enabled_clouds = []
                where_clause = "group_name='%s' and cloud_type='openstack' and enabled=1 and communication_up=1" % group["group_name"]
                rc, msg, cloud_list = config.db_query(CLOUDS, where=where_clause)
                for cld in cloud_list:
                    enabled_clouds.append(cld["cloud_name"])
                for cloud in cloud_list:
                    logging.debug("Checking defaults for group-cloud: %s-%s" % (group["group_name"], cloud["cloud_name"]))
                    # if there is a default image for the group, check for default image in the cloud
                    logging.debug("Group image: %s", grp_default_image_name)
                    logging.debug("Cloud image: %s", cloud["vm_image"])
                    if cloud["vm_image"] is None or cloud["vm_image"] == "":
                        default_image_name = grp_default_image_name
                    else:
                        default_image_name = cloud["vm_image"]
                    if default_image_name is not None and not default_image_name == "":
                        where_clause = "group_name='%s' and cloud_name='%s' and name='%s'" % (group["group_name"], cloud["cloud_name"], default_image_name)
                        rc, msg, images = config.db_query(IMAGES, where=where_clause)
                        if len(images) == 0:
                            # gasp, image isn't there, lets queue up a transfer.
                            if src_image is None:
                               where_clause = "group_name='%s' and name='%s'" % (group["group_name"], default_image_name)
                               rc, qmsg, image_candidates = config.db_query(IMAGES, where=where_clause)
                               img_count = len(image_candidates)
                               if img_count == 0:
                                   #default image not defined
                                   logging.error("Default image %s not present on any openstack clouds in group %s. Failed to replicate default image." % (default_image_name, group["group_name"]))
                                   continue
                               elif img_count > 1:
                                   logging.warning("More than one candidate image with name %s" % default_image_name)
                                   src_image = None
                                   for image in image_candidates:
                                       if image["cloud_name"] in enabled_clouds:
                                           src_image = image
                                           break
                                   if src_image is None:
                                       #no sources from enabled clouds
                                       logging.warning("Default image source only present on disabled clouds, manual transfer required.")
                                       continue
                               else:
                                   # no ambiguity about default image, simply select it
                                   src_image = image_candidates[0]
                            # We've got a source image, time to queue a transfer
                            # but first check the cache to see if we need to queue a pull request
                            cache_result = check_cache(config, default_image_name, src_image["checksum"], src_image["group_name"], "cloudscheduler")
                            if cache_result is False:
                                #Something went wrong checking the cache or queueing a pull request
                                logging.error("Failure checking cache or queuing pull request for image: %s" % default_image_name)
                                logging.error("...continuing to queue transfer (transfer task will queue up a pull request if needed)")
                            #Once here the image is in the cache of a pull request has been queued so we can go ahead and queue the transfer

                            #on second thought lets check to see we don't already have one queue'd up so we don't bombard the request queue
                            where_clause = "target_group_name='%s' and target_cloud_name='%s' and image_name='%s' and (status='pending' or status='error')" % (group["group_name"], cloud["cloud_name"], default_image_name)
                            rc, qmsg, pending_xfers = config.db_query(IMAGE_TX, where=where_clause)
                            if len(pending_xfers) > 0:
                                logging.info("Default image (%s) transfer already queued for cloud: %s... skipping" % (default_image_name, cloud["cloud_name"]))
                                continue
                            tx_id = generate_tx_id()
                            tx_req = {
                                "tx_id":             tx_id,
                                "status":            "pending",
                                "target_group_name": group["group_name"],
                                "target_cloud_name": cloud["cloud_name"],
                                "image_name":        default_image_name,
                                "image_id":          src_image["id"],
                                "checksum":          src_image["checksum"],
                                "requester":         "cloudscheduler",
                            }
                            config.db_merge(IMAGE_TX, tx_req)
                            config.db_commit()
                            logging.info("Transfer queued")
                            tx_request.apply_async((tx_id,), queue='tx_requests')

                            
                    else:
                        logging.info("No default image for group %s, skipping image transfers for cloud %s" % (group["group_name"], cloud["cloud_name"]))


            # seperate image and keypair loops so if one fails the other can have success
            rc, msg, group_list = config.db_query(GROUPS)
            for group in group_list:
                src_keypair = None
                default_key_name = group["vm_keyname"]
                where_clause = "group_name='%s' and cloud_type='openstack' and enabled=1 and communication_up=1"
                rc, msg, cloud_list = config.db_query(CLOUDS, where=where_clause)
                for cloud in cloud_list:

                    # now lets check keys- if there is a default key, check the keys for the cloud
                    if default_key_name is not None:
                        where_clause = "group_name='%s' and cloud_name='%s' and key_namee='%s'" % (group["group_name"], cloud["cloud_name"], default_key_name)
                        rc, msg, keys = config.db_query(KEYPAIRS, where=where_clause)
                        if len(keys) == 0:
                            # gasp again, keypair isn't present, keypairs are fast so lets just go ahead and do the transfer
                            if src_keypair == None:
                                # we haven't dug up a source keypair yet so lets grab one
                                where_clause = "group_name='%s' and key_name='%s'" % (group["group_name"], default_key_name)
                                rc, msg, db_keypairs = config.db_query(KEYPAIRS, where=where_clause)
                                db_keypair = db_keypairs[0]
                                if db_keypair == None:
                                    #we couldn't find a source keypair for this group, yikes
                                    logging.error("Unable to locate a source keypair: %s for group %s, skipping group." % (default_key_name, group["group_name"]))
                                    break
                                where_clause = "group_name='%s' and cloud_name='%s'" % (db_keypair["group_name"], db_keypair["cloud_name"])
                                rc, msg, src_cloud = config.db_query(CLOUDS, where=where_clause)
                                try:
                                    src_keypair = get_keypair(key_name=default_key_name, cloud=src_cloud)
                                except Exception as exc:
                                    logging.error("Exception while locating source keypair:")
                                    logging.error(exc)
                                    src_keypair = None
                                if src_keypair == None:
                                    #we couldn't find a source keypair for this group, yikes
                                    logging.error("Unable to locate a source keypair: %s for group %s, skipping group." % (default_key_name, group["group_name"]))
                                    break
                                #transfer keypair
                                logging.info("Source keypair found, uploading new keypair")
                                try:
                                    transfer_keypair(src_keypair, src_cloud)
                                    logging.info("Keypair %s transferred to cloud %s successfully" % (default_key_name, cloud["cloud_name"]))
                                except Exception as exc:
                                    logging.error("Keypair transfer failed:")
                                    logging.error(exc)

                    else:
                        logging.info("No default keypair for group %s, skipping keypair transfers for cloud %s" % (group["group_name"], cloud["cloud_name"]))
            
            config.db_commit()

        except Exception as exc:
            logging.error("Exception during general operation:")
            logging.exception(exc)

        if not os.path.exists(PID_FILE):
            logging.info("Stop set, exiting...")
            break
        signal.signal(signal.SIGINT, config.signals['SIGINT'])
        config.db_close()
        try:
            wait_cycle(cycle_start_time, poll_time_history, 21600, config) # sleep 6 hours if no cloud add/update
        except KeyboardInterrupt:
            # sigint recieved, cancel the sleep and start the loop
            continue


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
        'security_group_poller': security_group_poller,
        'volume':                volume_poller
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
